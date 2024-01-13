#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
# Template for Ultimarc CLI tools.
#
import logging
import sys

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

        if hasattr(self.args, 'set_id'):
            _logger.info(_(f'Action : Change controller ID to {self.args.set_id}'))
            if len(devices) > 1:
                _logger.error(_('Multiple UltraStik devices found. Only one may be configured at a time, aborting'))
                return -1

            device = devices[0]
            _logger.info(_(f'Selected : {device.product_name} ({device.dev_key})'))

            with (device as dev_h):
                if dev_h.set_controller_id(self.args.set_id):
                    _logger.info(_(f'Result : Success'))
                else:
                    _logger.error(_('Result : Failure'))

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

    parser.add_argument('-i', '--set-id', help=_('set joystick controller id'), type=int, choices=[1, 2, 3, 4])

    # TODO:  Setup additional program arguments here.
    args = parser.parse_args()

    with ToolContextManager(tool_cmd, args) as tool_env:
        process = UltraStikTool(args, tool_env)
        exit_code = process.run()
        return exit_code


# --- Main Program Call ---
if __name__ == "__main__":
    sys.exit(run())
