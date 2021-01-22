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
from enum import IntEnum
from json import JSONDecodeError

from jsonschema import validate, ValidationError
import libusb as usb

from ultimarc import translate_gettext as _
from ultimarc.exceptions import USBDeviceClaimInterfaceError, USBDeviceInterfaceNotClaimedError

_logger = logging.getLogger('ultimarc')

USB_REPORT_TYPE_OUT = ct.c_uint16(0x200)


class USBRequestCode(IntEnum):
    """
    Standard USB Setup Packet Request Codes.
    https://www.jungo.com/st/support/documentation/windriver/802/wdusb_man_mhtml/node55.html#usb_standard_dev_req_codes
    """
    GET_STATUS = 0
    CLEAR_FEATURE = 1
    # Reserved = 2
    SET_FEATURE = 3
    # Reserved = 4
    SET_ADDRESS = 5
    GET_DESCRIPTOR = 6
    SET_DESCRIPTOR = 7
    GET_CONFIGURATION = 8
    SET_CONFIGURATION = 9
    GET_INTERFACE = 10
    SET_INTERFACE = 11
    SYNCH_FRAME = 12


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

        if self.interface is not None:
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
        if self.interface is None:
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
                        Bit 7: Request direction (0=Host to device - Out, 1=Device to host - In).
                        Bits 5-6: Request type (0=standard, 1=class, 2=vendor, 3=reserved).
                        Bits 0-4: Recipient (0=device, 1=interface, 2=endpoint,3=other).
        :param b_request: Request field for the setup packet. The actual request, see USBRequestCodes Enum.
        :param w_value: Value field for the setup packet. A word-size value that varies according to the request.
                        For example, in the CLEAR_FEATURE request the value is used to select the feature, in the
                        GET_DESCRIPTOR request the value indicates the descriptor type and in the SET_ADDRESS
                        request the value contains the device address.
        :param w_index: Index field for the setup packet. A word-size value that varies according to the request.
                        The index is generally used to specify an endpoint or an interface.
        :param data: ctypes structure class.
        :param size: size of data.
        :return: True if successful otherwise False.
        https://www.jungo.com/st/support/documentation/windriver/802/wdusb_man_mhtml/node55.html#SECTION001213000000000000000
        """
        if self.interface is None:
            raise USBDeviceInterfaceNotClaimedError(self.dev_key)
        if not isinstance(b_request, USBRequestCode):
            raise ValueError('b_request argument must be USBRequestCode enum value.')

        ret = usb.control_transfer(
            self.__libusb_dev_handle__,  # ct.c_char_p
            request_type,  # ct.c_uint8
            b_request,  # ct.c_uint8, must be a USBRequestCode Enum value.
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
        if self.interface is None:
            raise USBDeviceInterfaceNotClaimedError(self.dev_key)

        if isinstance(report_id, int):
            report_id = ct.c_uint8(report_id)

        # Combine direction, request type and recipient together.
        request_type = usb.LIBUSB_ENDPOINT_OUT | request_type | recipient
        w_value = ct.c_uint16(USB_REPORT_TYPE_OUT.value | report_id.value)

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
        if self.interface is None:
            raise USBDeviceInterfaceNotClaimedError(self.dev_key)

        # Combine direction, request type and recipient together.
        request_type = usb.LIBUSB_ENDPOINT_IN | request_type | recipient
        return self._make_control_transfer(request_type, b_request, w_value, w_index, ct.byref(data), size)

    def read_interrupt(self, endpoint, response, uses_report_id=True):
        """
        Read response from USB device on the interrupt endpoint.
        :param endpoint: Endpoint to receive message on.
        :param response: Variable holding the complete response from the device.
        :param uses_report_id: True if report_id is in the message.
        """
        if self.interface is None:
            raise USBDeviceInterfaceNotClaimedError(self.dev_key)

        actual_length = ct.c_int(0)
        length = 5 if uses_report_id else 4  # Expecting the report_id in the message
        payload = (ct.c_ubyte * length)(0)
        payload_ptr = ct.byref(payload)

        # Here don't add the report_id into the response structure, 4 instead of 5
        for pos in range(0, ct.sizeof(response), 4 if uses_report_id else 5):
            self._make_interrupt_transfer(endpoint, payload_ptr, length, ct.byref(actual_length))
            # Remove report_id (byte 0) if it is used
            actual_length = actual_length \
                if actual_length == length and not uses_report_id else ct.c_int(actual_length.value - 1)
            ct.memmove(ct.addressof(response)+pos,
                       ct.byref(payload, 1) if uses_report_id else ct.byref(payload),
                       actual_length.value)
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
