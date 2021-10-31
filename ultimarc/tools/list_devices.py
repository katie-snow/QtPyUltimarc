#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
# List all Ultimarc devices attached to local host.
#
import logging
import sys

from ultimarc import translate_gettext as _
from ultimarc.devices import DeviceClassID
from ultimarc.exceptions import USBDeviceNotFoundError, USBDeviceClaimInterfaceError
from ultimarc.tools import ToolContextManager, ToolEnvironmentObject

_logger = logging.getLogger('ultimarc')

# Tool_cmd and tool_desc name are required.
# Remember to add/update bash completion in 'tools.bash'
tool_cmd = _('list')
tool_desc = _('list all attached ultimarc devices')


class ListDevicesClass(object):
    def __init__(self, args, env: (ToolEnvironmentObject, None)):
        """
        :param args: command line arguments.
        :param env: tool environment information, see: gcp_initialize().
        """
        self.args = args
        self.env = env

    def get_devices(self):
        """ Return a list of devices we should show information for. """
        return self.env.devices.filter(class_id=self.args.class_id, bus=self.args.bus, address=self.args.address)

    def list_devices_found(self):
        """ List all the devices found. """
        # Find all Ultimarc USB devices.
        _logger.info(_('Device classes found') + ':')
        for cat in self.env.devices.get_device_classes():
            _logger.info(f' {cat}')

        _logger.info('\n' + _('Devices') + ':')
        for dev in self.get_devices():
            _logger.info(f' {dev}')

        if not self.args.descriptors:
            return

        try:
            desc_string_fields = ['iManufacturer', 'iProduct', 'iSerialNumber', 'idProduct', 'idVendor']
            for dev in self.get_devices():
                _logger.info('')
                # Open device.
                with dev as dev_h:
                    _logger.info(_('Showing device descriptor properties for') + f' {dev.dev_key}')
                    _logger.info('  ' + _('Bus') + f': {dev.bus}')
                    _logger.info('  ' + _('Address') + f': {dev.address}')
                    for fld in dev_h.descriptor_fields:
                        desc_val = dev_h.get_descriptor_value(fld)
                        if fld in desc_string_fields:
                            desc_str = dev_h.get_descriptor_string(dev_h.get_descriptor_value(fld)) or ''
                            _logger.info(f'  {fld}: {desc_val:04x} (desc idx: 0x{desc_val:04x}, str: "{desc_str}")')
                        else:
                            _logger.info(f'  {fld}: {desc_val}')

        except (USBDeviceNotFoundError, USBDeviceClaimInterfaceError) as e:
            _logger.error(_('An error occurred while inspecting device') + f' {e.dev_key}.')

    def run(self):
        """
        Main program process
        :return: Exit code value
        """
        self.list_devices_found()
        return 0


def run():
    # Set global debug value and setup application logging.
    ToolContextManager.initialize_logging(tool_cmd)
    parser = ToolContextManager.get_argparser(tool_cmd, tool_desc)
    parser.add_argument('-c', '--class-id', help=_('filter by device class id'), type=str)
    parser.add_argument('-d', '--descriptors', help=_('Show device descriptor values.'), default=False,
                        action='store_true')

    classes = ','.join([c.value for c in DeviceClassID])
    parser.epilog = f"class ids: {classes}"
    args = parser.parse_args()

    # Verify class id is valid by looking in the Enum by value.
    if args.class_id:
        try:
            DeviceClassID(args.class_id)
        except ValueError:
            _logger.error('Invalid class id argument value.')
            return -1

    with ToolContextManager(tool_cmd, args) as tool_env:
        process = ListDevicesClass(args, tool_env)
        exit_code = process.run()
        return exit_code


# --- Main Program Call ---
if __name__ == "__main__":
    sys.exit(run())
