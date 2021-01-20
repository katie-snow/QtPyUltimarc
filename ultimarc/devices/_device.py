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
from ultimarc.exceptions import USBDeviceClaimInterfaceError, USBDeviceInterfaceNotClaimedError

_logger = logging.getLogger('ultimarc')

USB_REPORT_TYPE_OUT = 0x200

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
    __libusb_dev__ = None
    __libusb_dev_handle__ = None
    __libusb_dev_desc__ = None

    dev_key = None
    class_id = 'unset'  # Used to match/filter devices. Override in child classes.
    class_descr = 'unset'  # Override in child classes.
    interface = None  # Interface to write and read from.

    descriptor_fields = None  # List of available device property fields.

    def __init__(self, dev_handle, dev_key):
        self.__libusb_dev__ = usb.get_device(dev_handle)
        self.__libusb_dev_handle__ = dev_handle
        self.dev_key = dev_key
        self.descriptor_fields = self._get_descriptor_fields()

        if self.interface:
            self.claim_interface(self.interface)

    def _get_descriptor_fields(self):
        """
        Return a list of available descriptor property fields.
        :return: list of strings.
        """
        if not self.__libusb_dev_desc__:
            self.__libusb_dev_desc__ = usb.device_descriptor()
            usb.get_device_descriptor(self.__libusb_dev__, ct.byref(self.__libusb_dev_desc__))
        fields = sorted([fld[0] for fld in self.__libusb_dev_desc__._fields_])

        return fields

    def get_descriptor_value(self, prop_field):
        if prop_field and prop_field in self.descriptor_fields:
            return getattr(self.__libusb_dev_desc__, prop_field)
        raise ValueError(_('Invalid descriptor property field name') + f' ({prop_field})')

    def get_descriptor_string(self, index):
        """
        Return the String value of a device descriptor property.
        :param index: integer
        :return: String or None
        """
        buf = ct.create_string_buffer(1024)
        ret = usb.get_string_descriptor_ascii(self.__libusb_dev_handle__, index, ct.cast(buf, ct.POINTER(ct.c_ubyte)),
                                              ct.sizeof(buf))
        if ret > 0:
            result = buf.value.decode('utf-8')
            return result

        usb_error(ret, _('failed to get descriptor property field string value.'), debug=True)
        return None

    # TODO: Write function(s) to get device capabilities and other information based on this code.
    #      https://github.com/karpierz/libusb/blob/master/examples/testlibusb.py

    def claim_interface(self, interface):
        """
        :param interface: int, interface to write and read from.
        """
        self.interface = int(interface)
        # We need to claim the USB device interface.
        usb.set_auto_detach_kernel_driver(self.__libusb_dev_handle__, 1)
        status = usb.claim_interface(self.__libusb_dev_handle__, self.interface)
        if status != usb.LIBUSB_SUCCESS:
            # __exit__ function should close the handle for us
            # usb.close(self.__libusb_dev_handle__)
            raise USBDeviceClaimInterfaceError(self.dev_key)

    def _make_interrupt_transfer(self, endpoint, data, size, actual_length, timeout=2000):
        """
        Read message from USB device
        :param endpoint: Endpoint address to listen on.
        :param data: Variable to hold received data.
        :param size: Size expected to be received.
        :param actual_length: Actual length received.
        """
        if not self.interface:
            raise USBDeviceInterfaceNotClaimedError(self.dev_key)

        ret = usb.interrupt_transfer(
            self.__libusb_dev_handle__,  # ct.c_char_p
            endpoint,  # ct.ubyte
            ct.cast(data, ct.POINTER(ct.c_ubyte)),  # ct.POINTER(ct.c_ubyte)
            size,
            ct.cast(actual_length, ct.POINTER(ct.c_int)),  # ct.POINTER(ct.c_int)
            timeout)  # ct.c_uint32

        if ret >= 0:
            _logger.debug(f'Read {size} ' + _('bytes from device').format(size) + f' {self.dev_key}.')
            return True

        usb_error(ret, _('Failed to communicate with device') + f' {self.dev_key}.')
        return False

    def _make_control_transfer(self, request_type, b_request, w_value, w_index, data, size, timeout=2000):
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
        if not self.interface:
            raise USBDeviceInterfaceNotClaimedError(self.dev_key)

        ret = usb.control_transfer(
            self.__libusb_dev_handle__,  # ct.c_char_p
            request_type,  # ct.c_uint8
            # TODO: Understand these next 3 arguments better.
            b_request,  # ct.c_uint8
            w_value,  # ct.c_uint16
            w_index,  # ct.c_uint16
            ct.cast(data, ct.POINTER(ct.c_ubyte)),  # ct.POINTER(ct.c_ubyte)
            ct.c_uint16(size),  # ct.c_uint16
            timeout)  # ct.c_uint32

        if ret >= 0:
            direction = _('Read') if request_type & usb.LIBUSB_ENDPOINT_IN else _('Write')
            _logger.debug(f'{direction} {size} ' + _('bytes from device').format(size) + f' {self.dev_key}.')
            return True

        usb_error(ret, _('Failed to communicate with device') + f' {self.dev_key}.')
        return False

    def write(self, b_request, report_id, w_index, data=None, size=None, request_type=usb.LIBUSB_REQUEST_TYPE_CLASS,
              recipient=usb.LIBUSB_RECIPIENT_INTERFACE):
        """
        Write message to USB device.
        :param b_request: Request field for the setup packet
        :param report_id: report_id portion of the Value field for the setup packet.
        :param w_index: Index field for the setup packet
        :param data: ctypes structure class.
        :param size: size of message.
        :param request_type: Request type enum value.
        :param recipient: Recipient enum value.
        :return: True if successful otherwise False.
        """
        if not self.interface:
            raise USBDeviceInterfaceNotClaimedError(self.dev_key)

        # Combine direction, request type and recipient together.
        request_type = usb.LIBUSB_ENDPOINT_OUT | request_type | recipient
        w_value = USB_REPORT_TYPE_OUT | report_id

        payload = (ct.c_ubyte * 5)(0)
        payload[0] = report_id

        ct.memmove(ct.addressof(payload) + 1, ct.byref(data, 0),
                   size if size <= 4 else 4)

        payload_ptr = ct.byref(payload) if report_id else ct.byref(payload, 1)
        ret = self._make_control_transfer(request_type, b_request, w_value,
                                           w_index, payload_ptr,
                                           ct.sizeof(payload) if report_id else size)
        _logger.debug(_(' '.join(hex(x) for x in payload)))
        return ret

    def read(self, b_request, w_value, w_index, data=None, size=None, request_type=usb.LIBUSB_REQUEST_TYPE_CLASS,
             recipient=usb.LIBUSB_RECIPIENT_INTERFACE):
        """
        Read message from USB device.
        :param b_request: Request field for the setup packet
        :param w_value: Value field for the setup packet.
        :param w_index: Index field for the setup packet
        :param data: ctypes structure class.
        :param size: size of message.
        :param request_type: Request type enum value.
        :param recipient: Recipient enum value.
        :return: True if successful otherwise False.
        """
        if not self.interface:
            raise USBDeviceInterfaceNotClaimedError(self.dev_key)

        # Combine direction, request type and recipient together.
        request_type = usb.LIBUSB_ENDPOINT_IN | request_type | recipient
        # we need to add 8 extra bytes to the structure buffer for read requests.
        return self._make_control_transfer(request_type, b_request, w_value, w_index, data, size)

    def read_interrupt(self, endpoint, response, uses_report_id=True):
        """
        Read response from USB device on the interrupt endpoint.
        :param endpoint: Endpoint to receive message on.
        :param response: Variable holding the complete response from the device.
        :param uses_report_id: True if report_id is in the message.
        """
        if not self.interface:
            raise USBDeviceInterfaceNotClaimedError(self.dev_key)

        actual_length = int(0)
        length = 5 if uses_report_id else 4
        payload = (ct.c_ubyte * length)(0)
        payload_ptr = ct.byref(payload)

        for pos in range(0, ct.sizeof(response), 4):
            self._make_interrupt_transfer(endpoint, payload_ptr, length, actual_length)
            # Remove report_id (byte 0) if it is used
            ct.memmove(ct.addressof(response)+pos,
                       ct.byref(payload, 1) if uses_report_id else ct.byref(payload),
                       4)
            _logger.debug(_(' '.join(hex(x) for x in payload)))

        return response


    def load_config_schema(self, schema_file):
        """
        Load the requested schema file.
        :param schema_file: Schema file name only, no path included.
        :return: schema dict.
        """
        schema_paths = ['../schemas', './schemas', './ultimarc/schemas']
        schema_path = None

        for path in schema_paths:
            schema_path = os.path.abspath(os.path.join(path, schema_file))
            if os.path.exists(schema_path):
                break

        if not schema_path:
            _logger.error(_('Unable to locate schema directory.'))
            return None

        with open(schema_path) as h:
            return json.loads(h.read())

    def validate_config(self, config, schema_file):
        """
        Validate a configuration dict against a schema file.
        :param config: dict
        :param schema_file: relative or abspath of schema.
        :return: True if valid otherwise False.
        """
        schema = self.load_config_schema(schema_file)
        if not schema:
            return False

        try:
            validate(config, schema)
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
        base_schema = self.load_config_schema('base.schema')
        if not base_schema:
            return None

        try:
            with open(config_file) as h:
                config = json.loads(h.read())
        except JSONDecodeError:
            _logger.error(_('Configuration file is not valid JSON.'))
            return None

        try:
            validate(config, base_schema)
        except ValidationError as e:
            _logger.error(_('Configuration file did not validate against the base schema.') + f'\n{e}')
            return None

        if config['resourceType'] not in resource_types:
            valid_types = ",".join(resource_types)
            _logger.error(_('Resource type does not match accepted types') + f' ({valid_types}).')
            return None

        return config
