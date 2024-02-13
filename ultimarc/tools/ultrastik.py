#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
# Template for Ultimarc CLI tools.
#
import argparse
import json
import logging
import os.path
import sys

from devices.ultrastik import UltraStikPre2015Device, UltraStikDevice, USTIK_RESOURCE_TYPES
from ultimarc import translate_gettext as _
from ultimarc.devices import DeviceClassID
from ultimarc.tools import ToolContextManager, ToolEnvironmentObject


_logger = logging.getLogger('ultimarc')

# Tool_cmd and tool_desc name are required.
# Remember to add/update bash completion in 'tools.bash'
tool_cmd = _('ultrastik')
tool_desc = _('configure ultrastik 360 joysticks')


class UltraStikTool(object):
    def __init__(self, args, tool_env: ToolEnvironmentObject):
        """
        :param args: command line arguments.
        :param tool_env: tool environment information, see: gcp_initialize().
        """
        self.args = args
        self.tool_env = tool_env

    def run(self):
        """
        Main program process
        :return: Exit code value
        """
        # Get devices we want to work with based on filters.
        devices = [dev for dev in
                   self.tool_env.devices.filter(class_id=DeviceClassID.UltraStik, bus=self.args.bus,
                                                address=self.args.address)]
        if not devices:
            _logger.error(_('No UltraStik 360 joysticks found, aborting'))
            return -1

        if self.args.set_device_id:
            # Setup schema data
            config = {
                "schemaVersion" : 2.0,
                "resourceType" : "ultrastik-controller-id",
                "deviceClass" : "ultrastik",
                "newControllerId" : self.args.set_device_id
            }
        else:
            # Load and validate config file is one of the valid resource types
            with open(self.args.set_config) as h:
                config = json.loads(h.read())
            if 'resourceType' not in config or config['resourceType'] not in USTIK_RESOURCE_TYPES:
                _logger.error(_('Configuration file is invalid'))
                return -1

        # See if we are changing the device controller id, if so only one device may be selected.
        if config['resourceType'] == 'ultrastik-controller-id':
            # We can only set the controller id of one device at a time.
            if len(devices) > 1:
                _logger.error(_('Multiple devices selected. Only one may be selected when changing controller ID'))
                return -1

            device = devices[0]
            dev_h: [UltraStikPre2015Device, UltraStikDevice]
            with (device as dev_h):
                # Load schema and validate config
                if not dev_h.validate_config(config, 'ultrastik-controller-id.schema'):
                    return -1
                new_id = config['newControllerId']

                _logger.info(_(f'Selected {device.product_name} ({device.dev_key})'))
                _logger.info(_(f'Changing controller ID to {new_id}'))

                if dev_h.set_controller_id(new_id) is True:
                    _logger.info(_(f'Success'))
                    return 0

            _logger.info(_(f'Failed'))
            return -1

        # Apply configuration to joystick.
        else:
            # Loop through devices and apply config
            for device in devices:
                dev_h: [UltraStikPre2015Device, UltraStikDevice]
                with (device as dev_h):
                    # Load schema and validate config
                    if not dev_h.validate_config(config, 'ultrastik-config.schema'):
                        return -1

                    _logger.info(_(f'Updating {device.product_name} ({device.dev_key})'))
                    dev_h.set_config(self.args.set_config)

            _logger.info(_(f'Success'))
            return 0


def run():
    # Set global debug value and setup application logging.
    ToolContextManager.initialize_logging(tool_cmd)
    parser = ToolContextManager.get_argparser(tool_cmd, tool_desc)

    parser.add_argument('--set-config', help=_('Set joystick config from config file.'), type=str, default=None,
                        metavar='CONFIG-FILE')
    parser.add_argument('--set-device-id', help=_('set joystick controller id'), type=int, choices=[1, 2, 3, 4],
                        default=None)

    args = parser.parse_args()

    # Validate arguments
    num_args = sum([bool(args.set_device_id), bool(args.set_config)])
    if num_args == 0:
        _logger.warning(_('Nothing to do.'))
        return 0

    if args.set_config:
        args.set_config = os.path.abspath(args.set_config)
        if not os.path.exists(args.set_config):
            _logger.error(_(f'Configuration file not found ({args.set_config})'))

    with ToolContextManager(tool_cmd, args) as tool_env:
        process = UltraStikTool(args, tool_env)
        exit_code = process.run()
        return exit_code


# --- Main Program Call ---
if __name__ == "__main__":
    sys.exit(run())
