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
tool_desc = _('Manage Mini-pac devices')


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
        #   Arguments:
        #       Debounce change only, read in config and adjust the debounce
        #       Single pin change (action, alternate_action, shift), reading in config and making the one change
        cur_config = None

        # Get devices we want to work with based on filters.
        devices = [dev for dev in
                   self.tool_env.devices.filter(class_id=DeviceClassID.MiniPac, bus=self.args.bus,
                                                address=self.args.address)]

        if not devices:
            _logger.error(_('No Mini-PAC devices found, aborting'))
            return -1

        # Get config from device
        if self.args.get_config:
            for dev in devices:
                with dev as dev_h:
                    indent = int(self.args.indent) if self.args.indent else None
                    response = dev_h.get_device_config(indent, self.args.file)
                    _logger.info(response)

        # Set mini-pac device configuration from a configuration file
        if self.args.set_config:
            for dev in devices:
                with dev as dev_h:
                    use_current = self.args.current
                    dev_h.set_config(self.args.set_config, use_current)
                    _logger.info(f'{dev.dev_key} ({dev.bus},{dev.address}): ' +
                                 _('configuration successfully applied to device.'))

        if self.args.set_pin:
            for dev in devices:
                with dev as dev_h:
                    dev_h.set_pin(self.args.set_pin)

        return 0


def run():
    # Set global debug value and setup application logging.
    ToolContextManager.initialize_logging(tool_cmd)
    parser = ToolContextManager.get_argparser(tool_cmd, tool_desc)
    group = parser.add_argument_group()

    # TODO:  Setup additional program arguments here.
    group.add_argument('--get-config', help=_('Get Mini-pac device config'), default=False, action='store_true')
    group.add_argument('--indent', help=_('Set the json indent level for the output of the device configuration'),
                       default=None, metavar='INT')
    group.add_argument('--file', help=_('File path to write out the json of the device configuration'), type=str,
                       default=None, metavar='FILE-NAME')
    group.add_argument('--set-config', help=_('Set Mini-pac device config from config file'), type=str, default=None,
                       metavar='CONFIG-FILE')
    group.add_argument('--current',
                       help=_('Use Mini-pac current config when applying config from file'), default=False,
                       action='store_true')
    group.add_argument('--set-pin', help=_('Set single Mini-pac pin'), type=str,
                       default=None, metavar=('PIN', 'ACTION', 'ALT_ACTION', 'IS_SHIFT'), nargs=4)
    args = parser.parse_args()

    if not args.get_config and args.indent:
        _logger.error(_('The --indent argument can only be used with the --get_config argument '))
        return -1
    if not args.get_config and args.file:
        _logger.error(_('The --file argument can only be used with the --get_config argument '))
        return -1
    if not args.set_config and args.current:
        _logger.error(_('The --current argument can only be used with the --set_config argument '))
        return -1

    with ToolContextManager(tool_cmd, args) as tool_env:
        process = MiniPACClass(args, tool_env)
        exit_code = process.run()
        return exit_code


# --- Main Program Call ---
if __name__ == "__main__":
    sys.exit(run())
