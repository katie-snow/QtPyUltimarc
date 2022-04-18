#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
# Template for Ultimarc CLI tools.
#
import logging
import os
import sys

from ultimarc import translate_gettext as _
from ultimarc.devices import DeviceClassID
from ultimarc.tools import ToolContextManager, ToolEnvironmentObject


_logger = logging.getLogger('ultimarc')

# Tool_cmd and tool_desc name are required.
# Remember to add/update bash completion in 'tools.bash'
tool_cmd = _('ipac2')
tool_desc = _('Manage ipac2 devices')


class IPAC2Class(object):
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
                   self.tool_env.devices.filter(class_id=DeviceClassID.IPAC2, bus=self.args.bus,
                                                address=self.args.address)]

        if not devices:
            _logger.error(_('No ipac2 devices found, aborting'))
            return -1

        # Get config from device
        if self.args.get_config:
            for dev in devices:
                with dev as dev_h:
                    indent = int(self.args.indent) if self.args.indent else None
                    response = dev_h.get_device_config(indent, self.args.file)
                    _logger.info(response)

        # Set ipac2 device configuration from a configuration file
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
                    _logger.info(f'{dev.dev_key} ({dev.bus},{dev.address}): ' +
                                 _('pin successfully applied to device.'))

        # Set debounce value
        if self.args.set_debounce:
            for dev in devices:
                with dev as dev_h:
                    response = dev_h.set_debounce(self.args.set_debounce)
                    if response:
                        _logger.info(f'{dev.dev_key} ({dev.bus},{dev.address}): ' +
                                     _('debounce successfully applied to device.'))

        # Set paclink value
        if self.args.paclink is not None:
            for dev in devices:
                with dev as dev_h:
                    response = dev_h.set_paclink(self.args.paclink)
                    if response:
                        _logger.info(f'{dev.dev_key} ({dev.bus},{dev.address}): ' +
                                     _('paclink successfully applied to device.'))

        return 0


def run():
    # Set global debug value and setup application logging.
    ToolContextManager.initialize_logging(tool_cmd)
    parser = ToolContextManager.get_argparser(tool_cmd, tool_desc)
    group = parser.add_argument_group()

    # TODO:  Setup additional program arguments here.
    group.add_argument('--get-config', help=_('Get ipac2 device config'), default=False, action='store_true')
    group.add_argument('--indent', help=_('Set the json indent level for the output of the device configuration'),
                       default=None, metavar='INT')
    group.add_argument('--file', help=_('File path to write out the json of the device configuration'), type=str,
                       default=None, metavar='FILE-NAME')
    group.add_argument('--set-config', help=_('Set ipac2 device config from config file'), type=str, default=None,
                       metavar='CONFIG-FILE')
    group.add_argument('--current',
                       help=_('Use ipac2 current config when applying config from file'), default=False,
                       action='store_true')
    group.add_argument('--set-debounce', help=_('Set ipac2 debounce value'), type=str, metavar='STR')
    group.add_argument('--set-pin', help=_('Set single pin'), type=str,
                       default=None, metavar=('PIN', 'ACTION', 'ALT_ACTION', 'IS_SHIFT'), nargs=4)
    group.add_argument('--set-paclink', dest='paclink', help=_('Set ipac2 paclink value'), action='store_true')
    group.add_argument('--unset-paclink', dest='paclink', help=_('Unset ipac2 paclink value'), action='store_false')
    group.set_defaults(paclink=None)
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

    if args.set_config:
        # Always force absolute path for config files.
        args.set_config = ToolContextManager.clean_config_path(args.set_config)
        if not os.path.exists(args.set_config):
            _logger.error(_('Unable to find configuration file specified in argument.'))
            return -1

    with ToolContextManager(tool_cmd, args) as tool_env:
        process = IPAC2Class(args, tool_env)
        exit_code = process.run()
        return exit_code


# --- Main Program Call ---
if __name__ == "__main__":
    sys.exit(run())
