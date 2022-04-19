#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
# Tool for managing Ultimarc USB Button devices.
#
import logging
import os
import random
import re
import sys

from ultimarc import translate_gettext as _
from ultimarc.devices import DeviceClassID
from ultimarc.devices.usb_button import ConfigApplication
from ultimarc.tools import ToolContextManager, ToolEnvironmentObject

_logger = logging.getLogger('ultimarc')

# Tool_cmd and tool_desc name are required.
# Remember to add/update bash completion in 'tools.bash'
tool_cmd = _('usb-button')
tool_desc = _('manage usb-button devices.')

_RGB_STRING_REGEX = r"^.*?([0-9]{1,3}),\s*?([0-9]{1,3}),\s*?([0-9]{1,3})+.*?$"


class USBButtonClass(object):
    """ Tool class for managing USB buttons. """

    def __init__(self, args, env: ToolEnvironmentObject):
        """
        :param args: command line arguments.
        :param env: tool environment information, see: gcp_initialize().
        """
        self.args = args
        self.env = env

    def run(self):
        """
        Main program process
        :return: Exit code value
        """
        # Get devices we want to work with based on filters.
        devices = [dev for dev in
                   self.env.devices.filter(class_id=DeviceClassID.USBButton, bus=self.args.bus,
                                           address=self.args.address)]

        if not devices:
            _logger.error(_('No USB button devices found, aborting'))
            return -1

        # See if we are setting a color from the command line args.
        if self.args.set_color:
            match = re.match(_RGB_STRING_REGEX, self.args.set_color)
            red, green, blue = match.groups()
            for dev in devices:
                with dev as dev_h:
                    dev_h.set_color(int(red), int(green), int(blue))
                    _logger.info(f'{dev.dev_key} ({dev.bus},{dev.address}): ' +
                                 _('Color') + f': RGB({red},{green},{blue}).')

        # Return the current color RGB values.
        elif self.args.get_color:
            for dev in devices:
                with dev as dev_h:
                    red, green, blue = dev_h.get_color()
                    if red is not None:
                        _logger.info(f'{dev.dev_key} ({dev.bus},{dev.address}): ' +
                                     _('Color') + f': RGB({red},{green},{blue}).')

        # Set a random RGB color.
        elif self.args.set_random_color:
            for dev in devices:
                red = random.randrange(255)
                green = random.randrange(255)
                blue = random.randrange(255)
                with dev as dev_h:
                    dev_h.set_color(red, green, blue)
                _logger.info(f'{dev.dev_key} ({dev.bus},{dev.address}): ' +
                             _('randomly set button color to') + f' RGB({red},{green},{blue}).')

        # Apply a usb button config.
        elif self.args.set_config:
            for dev in devices:
                with dev as dev_h:
                    application = ConfigApplication.temporary if self.args.temporary else ConfigApplication.permanent
                    if dev_h.set_config(self.args.set_config, application):
                        _logger.info(f'{dev.dev_key} ({dev.bus},{dev.address}): ' +
                                     _('configuration successfully applied to device.'))
                    else:
                        _logger.error(f'{dev.dev_key} ({dev.bus},{dev.address}): ' +
                                      _('failed to apply configuration to device.'))

        return 0


def run():
    # Set global debug value and setup application logging.
    ToolContextManager.initialize_logging(tool_cmd)
    parser = ToolContextManager.get_argparser(tool_cmd, tool_desc)

    # --set-color --get-color --load-config --export-config
    parser.add_argument('--set-color', help=_('set usb button color with RGB value'), type=str, default=None,
                        metavar='INT,INT,INT')
    parser.add_argument('--set-random-color', help=_('randomly set usb button color'), default=False,
                        action='store_true')
    parser.add_argument('--get-color', help=_('output current usb button color RGB value'), default=False,
                        action='store_true')
    parser.add_argument('--set-config', help=_('Set button config from config file.'), type=str, default=None,
                        metavar='CONFIG-FILE')
    parser.add_argument('--temporary', help=_('Apply config until device unplugged.'), default=False,
                        action='store_true')

    args = parser.parse_args()

    num_args = sum([bool(args.set_color), args.set_random_color, args.get_color, bool(args.set_config)])
    if num_args == 0:
        _logger.warning(_('Nothing to do.'))
        return 0
    if num_args > 1 and (not args.set_config or not args.temporary):
        # Enhance this check and provide better feedback on which arguments are mutually exclusive.
        _logger.error(_('More than one mutually exclusive argument specified.'))
        return -1

    if args.set_color:
        if not re.match(_RGB_STRING_REGEX, args.set_color):
            _logger.error(_('Invalid RGB value found for --set-color argument.'))
            return -1

    if not args.set_config and args.temporary:
        _logger.error(_('The --temporary argument can only be used with the --set-config argument.'))
        return -1

    if args.set_config:
        # Always force absolute path for config files.
        args.set_config = ToolContextManager.clean_config_path(args.set_config)
        if not os.path.exists(args.set_config):
            _logger.error(_('Unable to find configuration file specified in argument.'))
            return -1

    with ToolContextManager(tool_cmd, args) as tool_env:
        process = USBButtonClass(args, tool_env)
        exit_code = process.run()
        return exit_code


# --- Main Program Call ---
if __name__ == "__main__":
    sys.exit(run())
