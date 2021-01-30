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
tool_cmd = _('mini-pac')
tool_desc = _('manage mini-pac devices')


class MiniPACClass(object):
    """ Tool class for managing Mini-PAC devices """

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
        # TODO: write program main process here after setting 'tool_cmd' and 'tool_desc'...
        # TODO:
        #   Arguments:
        #       Debounce change only, read in config and adjust the debounce
        #       Single pin change (action, alternate_action, shift), reading in config and making the one change
        #       Config file change with current configurations
        cur_config = None

        # Get devices we want to work with based on filters.
        devices = [dev for dev in
                   self.tool_env.devices.filter(class_id=DeviceClassID.MiniPac, bus=self.args.bus,
                                                address=self.args.address)]

        if not devices:
            _logger.error(_('No Mini-PAC devices found, aborting'))
            return -1

        # Read config from device
        if self.args.read_config:
            for dev in devices:
                with dev as dev_h:
                    response = dev_h.get_current_configuration()
                    _logger.debug(response)
                    cur_config = response

        # Set mini-pac device configuration from a configuration file
        if self.args.set_config:
            for dev in devices:
                with dev as dev_h:
                    dev_h.set_config(self.args.set_config)
                    _logger.info(f'{dev.dev_key} ({dev.bus},{dev.address}): ' +
                                 _('configuration successfully applied to device.'))

        return 0


def run():
    # Set global debug value and setup application logging.
    ToolContextManager.initialize_logging(tool_cmd)
    parser = ToolContextManager.get_argparser(tool_cmd, tool_desc)

    # TODO:  Setup additional program arguments here.
    parser.add_argument('--read-config', help=_('Read Mini-pac device config'), default=False, action='store_true')
    parser.add_argument('--set-config', help=_('Set Mini-pac device config from config file'), type=str, default=None,
                        metavar='CONFIG-FILE')
    args = parser.parse_args()

    with ToolContextManager(tool_cmd, args) as tool_env:
        process = MiniPACClass(args, tool_env)
        exit_code = process.run()
        return exit_code


# --- Main Program Call ---
if __name__ == "__main__":
    sys.exit(run())
