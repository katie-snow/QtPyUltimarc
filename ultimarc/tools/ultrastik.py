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

from devices.ultrastik import UltraStikPre2015Device, UltraStikDevice
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

        if self.args.action == 'write-config':
            # See if we are changing the device controller id, if so only one device may be selected.
            if (self.args.set_device_id or (self.args.config and
                                            self.args.config['resourceType'] == 'ultrastik-controller-id')):

                if len(devices) > 1:
                    _logger.error(_('Multiple devices selected. Only one may be selected when changing controller ID'))
                    return -1

                device = devices[0]
                dev_h: [UltraStikPre2015Device, UltraStikDevice]
                with (device as dev_h):

                    if self.args.set_device_id:
                        new_id = self.args.set_device_id
                    else:
                        # Load schema and validate config
                        if not dev_h.validate_config(self.args.config, 'ultrastik-controller-id.schema'):
                            return -1
                        new_id = self.args.config['newControllerId']

                    _logger.info(_(f'Selected {device.product_name} ({device.dev_key})'))
                    _logger.info(_(f'Changing controller ID to {new_id}'))

                    if dev_h.set_controller_id(new_id) is True:
                        _logger.info(_(f'Success'))
                        return 0

                _logger.info(_(f'Failed'))
                return -1

            # Apply configuration to joystick.
            elif self.args.config and self.args.config['resourceType'] == 'ultrastik-config':
                # Loop through devices and apply config
                for device in devices:
                    dev_h: [UltraStikPre2015Device, UltraStikDevice]
                    with (device as dev_h):
                        # Load schema and validate config
                        if not dev_h.validate_config(self.args.config, 'ultrastik-config.schema'):
                            return -1

                        _logger.info(_(f'Updating {device.product_name} ({device.dev_key})'))
                        dev_h.set_config(self.args.config)

                _logger.info(_(f'Success'))
                return 0
            else:
                raise EnvironmentError(_('Should not have reached here'))
        """
        Example: Enabling colors in terminals.
            Using colors in terminal output is supported by using the ultimarc.system_utils
            object.  Errors and Warnings are automatically set to Red and Yellow respectively.
            The terminal_colors object has many predefined colors, but custom colors may be used
            as well. See ultimarc.system_utils for more information.
        """
        # from ultimarc.system_utils import tc as _tc
        # _logger.info(_tc.fmt('This is a blue info line.', _tc.fg_bright_blue))
        # _logger.info(_tc.fmt('This is a custom color line', _tc.custom_fg_color(156)))

        # TODO: write program main process here after setting 'tool_cmd' and 'tool_desc'...
        return 0


def run():
    # Set global debug value and setup application logging.
    ToolContextManager.initialize_logging(tool_cmd)
    parser = ToolContextManager.get_argparser(tool_cmd, tool_desc)

    filename_parser = argparse.ArgumentParser(add_help=False)
    filename_parser.add_argument('--filename', help=_('configuration file path and name'), type=str, default=None)

    # Create sub-parser groups, store group choice in 'args.action'
    sub_parsers = parser.add_subparsers(help=_('actions'), dest='action')

    # Write device configuration options
    set_parser = sub_parsers.add_parser('write-config', help=_('write device configuration'), parents=[filename_parser])
    set_parser.add_argument('--set-config', help=_('set joystick configuration'), action='store_true', default=False)
    set_parser.add_argument('--set-device-id', help=_('set joystick controller id'), type=int, choices=[1, 2, 3, 4])

    # Read device configuration options
    get_parser = sub_parsers.add_parser('read-config', help=_('read device configuration'), parents=[filename_parser])

    args = parser.parse_args()

    # Validate arguments
    if args.action == 'write-config':

        if not hasattr(args, 'set_config') and not hasattr(args, 'set_device_id'):
            _logger.error(_("Argument 'set-config' or 'set-device-id' must be used"))
            return -1

        # Set some default values if needed so the arg object always has these properties defined.
        args.config = None  # Set a default value for 'args.config'
        if not hasattr(args, 'set_device_id'):
            args.set_device_id = None

        if args.filename:
            if args.set_device_id:
                # Enhance this check and provide better feedback on which arguments are mutually exclusive.
                _logger.error(_('Configuration filename and set device id arguments may not be used together'))
                return -1

            args.filename = os.path.abspath(args.filename)

            if not os.path.exists(args.filename):
                _logger.error(_(f'Configuration file not found ({args.filename})'))

            with open(args.filename) as h:
                args.config = json.loads(h.read())

                if not args.config:
                    _logger.error(_('Empty configuration file'))
                    return -1

    with ToolContextManager(tool_cmd, args) as tool_env:
        process = UltraStikTool(args, tool_env)
        exit_code = process.run()
        return exit_code


# --- Main Program Call ---
if __name__ == "__main__":
    sys.exit(run())
