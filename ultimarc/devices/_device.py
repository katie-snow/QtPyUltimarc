#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
# Base class for all USB device classes.
#

import ctypes as ct
import json
import logging
import os
from json import JSONDecodeError

from jsonschema import validate, ValidationError
import libusb as usb

from ultimarc import translate_gettext as _

_logger = logging.getLogger('ultimarc')


def usb_error(code, msg, debug=False):
    """
    Return string containing error code in string format.
    :param code: integer.
    :param msg: string, additional error message
    :param debug: boolean, if False show error else show debug statement.
    """
    if debug is False:
        _logger.error(f'{usb.error_name(code).decode("utf-8")} ({code}): ' + msg)
    else:
        _logger.debug(f'{usb.error_name(code).decode("utf-8")} ({code}): ' + msg)


class USBDeviceHandle:
    """
    Represents an opened USB device.  Do not instantiate directly, use object obtained
    from a USBDeviceInfo object using 'with' command.  IE 'with USBDeviceInfo as handle:'
    """
    __dev__ = None
    __dev_handle__ = None
    __dev_desc__ = None

    dev_key = None
    class_id = 'unset'  # Used to match/filter devices. Override in child classes.
    class_descr = 'unset'  # Override in child classes.

    property_fields = None  # List of available device property fields.

    def __init__(self, dev_handle, dev_key):
        self.__dev__ = usb.get_device(dev_handle)
        self.__dev_handle__ = dev_handle
        self.dev_key = dev_key
        self.property_fields = self._get_properties_fields()

    def _get_properties_fields(self):
        """
        Return a list of available property fields.
        :return: list of strings.
        """
        if not self.__dev_desc__:
            self.__dev_desc__ = usb.device_descriptor()
            usb.get_device_descriptor(self.__dev__, ct.byref(self.__dev_desc__))
        fields = sorted([fld[0] for fld in self.__dev_desc__._fields_])

        return fields

    def get_desc_value(self, prop_field):
        if prop_field and prop_field in self.property_fields:
            return getattr(self.__dev_desc__, prop_field)
        raise ValueError(_('Invalid descriptor property field name') + f' ({prop_field})')

    def get_desc_string(self, index):
        """
        Return the String value of a device descriptor property.
        :param index: integer
        :return: String or None
        """
        buf = ct.create_string_buffer(1024)
        ret = usb.get_string_descriptor_ascii(self.__dev_handle__, index, ct.cast(buf, ct.POINTER(ct.c_ubyte)),
                                              ct.sizeof(buf))
        if ret > 0:
            result = buf.value.decode('utf-8')
            return result

        usb_error(ret, _('failed to get descriptor property field string value.'), debug=True)
        return None

    # TODO: Write function to get device capabilities and other information based on this code.
    #      https://github.com/karpierz/libusb/blob/master/examples/testlibusb.py

    def _make_control_transfer(self, request_type, b_request, w_value, w_index, data, size):
        """
        Read/Write data from USB device.
        :param request_type: Request type value. Combines direction, type and recipient enum values.
        :param b_request: Request field for the setup packet
        :param w_value: Value field for the setup packet.
        :param w_index: Index field for the setup packet
        :param data: ctypes structure class.
        :param size: size of data.
        :return: True if successful otherwise False.
        """
        ret = usb.control_transfer(
            self.__dev_handle__,  # ct.c_char_p
            request_type,  # ct.c_uint8
            # TODO: Understand these next 3 arguments better.
            b_request,  # ct.c_uint8
            w_value,  # ct.c_uint16
            w_index,  # ct.c_uint16
            ct.cast(ct.pointer(data), ct.POINTER(ct.c_ubyte)),  # ct.POINTER(ct.c_ubyte)
            ct.c_uint16(size),  # ct.c_uint16
            2000)  # ct.c_uint32

        if ret >= 0:
            if request_type & usb.LIBUSB_ENDPOINT_IN:
                _logger.debug(_('Read {} bytes from device').format(size) + f' {self.dev_key}.')
            else:
                _logger.debug(_('Wrote {} bytes to device').format(size) + f' {self.dev_key}.')
            return True

        if request_type & usb.LIBUSB_ENDPOINT_IN:
            usb_error(ret, _('Failed to read data from device') + f' {self.dev_key}.')
        else:
            usb_error(ret, _('Failed to write data to device') + f' {self.dev_key}.')
        return False

    def write(self, b_request, w_value, w_index, data, size, request_type=usb.LIBUSB_REQUEST_TYPE_CLASS,
              recipient=usb.LIBUSB_RECIPIENT_INTERFACE):
        """
        Write data from USB device.
        :param b_request: Request field for the setup packet
        :param w_value: Value field for the setup packet.
        :param w_index: Index field for the setup packet
        :param data: ctypes structure class.
        :param size: size of data.
        :param request_type: Request type enum value.
        :param recipient: Recipient enum value.
        :return: True if successful otherwise False.
        """
        # Combine direction, request type and recipient together.
        request_type = usb.LIBUSB_ENDPOINT_OUT | request_type | recipient
        return self._make_control_transfer(request_type, b_request, w_value, w_index, data, size)

    def read(self, b_request, w_value, w_index, data, size, request_type=usb.LIBUSB_REQUEST_TYPE_CLASS,
             recipient=usb.LIBUSB_RECIPIENT_INTERFACE):
        """
        Read data from USB device.
        :param b_request: Request field for the setup packet
        :param w_value: Value field for the setup packet.
        :param w_index: Index field for the setup packet
        :param data: ctypes structure class.
        :param size: size of data.
        :param request_type: Request type enum value.
        :param recipient: Recipient enum value.
        :return: True if successful otherwise False.
        """
        # Combine direction, request type and recipient together.
        request_type = usb.LIBUSB_ENDPOINT_IN | request_type | recipient
        # we need to add 8 extra bytes to the data buffer for read requests.
        return self._make_control_transfer(request_type, b_request, w_value, w_index, data, size)

    def validate_config(self, config, schema_path):
        """
        Validate a configuration dict against a schema file.
        :param config: dict
        :param schema_path: relative or abspath of schema.
        :return: True if valid otherwise False.
        """
        schema_path = os.path.abspath(schema_path)
        with open(schema_path) as h:
            base_schema = json.loads(h.read())

        try:
            validate(config, base_schema)
        except ValidationError as e:
            _logger.error(_('Configuration file did not validate against config schema.'))
            return False

        return True

    def validate_config_base(self, config_file, resource_types):
        """
        Validate the configuration file against the base schema.
        :param config_file: Absolute path to configuration json file.
        :param resource_types: list of strings representing valid 'resourceType' values.
        :return: config dict.
        """
        # Read the base schema, all json configs must validate against this schema.
        schema_path = os.path.abspath('../schemas/base.schema')
        with open(schema_path) as h:
            base_schema = json.loads(h.read())

        try:
            with open(config_file) as h:
                config = json.loads(h.read())
        except JSONDecodeError:
            _logger.error(_('Configuration file is not valid JSON.'))
            return None

        try:
            validate(config, base_schema)
        except ValidationError as e:
            _logger.error(_('Configuration file did not validate against the base schema.'))
            return None

        if config['resourceType'] not in resource_types:
            _logger.error(_('Resource type does not match accepted types' + f' ({",".join(resource_types)}).'))
            return None

        return config
