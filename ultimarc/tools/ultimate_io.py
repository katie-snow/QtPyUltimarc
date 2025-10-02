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
tool_cmd = _('ultimate-io')
tool_desc = _('Manage UltimateIO devices')


class UltimateIOClass(object):
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
                   self.tool_env.devices.filter(class_id=DeviceClassID.UltimateIO, bus=self.args.bus,
                                                address=self.args.address)]

        if not devices:
            _logger.error(_('No ultimate-io devices found, aborting'))
            return -1

        # Get the pin configuration from the device
        if self.args.get_pin_config:
            for dev in devices:
                with dev as dev_h:
                    indent = int(self.args.indent) if self.args.indent else None
                    response = dev_h.get_device_config(indent, self.args.file)
                    _logger.info(response)

        # Set ultimate-io device pin configuration from a configuration file
        if self.args.set_pin_config:
            for dev in devices:
                with dev as dev_h:
                    use_current = self.args.current
                    dev_h.set_config(self.args.set_pin_config, use_current)
                    _logger.info(f'{dev.dev_key} ({dev.bus},{dev.address}): ' +
                                 _('pin configuration successfully applied to device.'))

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

        # LED configuration options
        # Set LED values with configuration file
        if self.args.set_led_config:
            for dev in devices:
                with dev as dev_h:
                    response = dev_h.set_led_config(self.args.set_led_config)
                    _logger.info(response)

        # Set one LED
        if self.args.set_led:
            for dev in devices:
                with dev as dev_h:
                    led = self.args.set_led[0]
                    value = self.args.set_led[1]

                    # check value is in range
                    if led not in range(1-97):
                        _logger.info(f'LED {led} is not between 1 to 96')
                        return -1

                    if value not in range(0-256):
                        _logger.info(f'LED value {value} is not between 0 to 255')
                        return -1

                    response = dev_h.set_led_intensity(led, value)
                    _logger.info(response)

        # Set all LEDs to one intensity
        if self.args.set_all_leds:
            for dev in devices:
                with dev as dev_h:
                    value = self.args.set_all_leds
                    if value not in range(0-256):
                        _logger.info(f'LED value {value} is not between 0 to 255')
                        return -1

                    response = dev_h.set_all_led_intensities(value)
                    _logger.info(response)

        # Set fade rate for all LEDs
        if self.args.set_leds_fade_rate:
            for dev in devices:
                with dev as dev_h:
                    value = self.args.set_leds_fade_rate
                    if value not in range(0 - 256):
                        _logger.info(f'LED fade rate {value} is not between 0 to 255')
                        return -1

                    response = dev_h.set_all_led_intensities(self.args.set_leds_fade_rate)
                    _logger.info(response)

        # Set LEDs to random state
        if self.args.set_leds_random_state:
            for dev in devices:
                with dev as dev_h:
                    response = dev_h.set_led_random_state()
                    _logger.info(response)
        return 0


def run():
    # Set global debug value and setup application logging.
    ToolContextManager.initialize_logging(tool_cmd)
    parser = ToolContextManager.get_argparser(tool_cmd, tool_desc)
    group = parser.add_argument_group()

    # TODO:  Setup additional program arguments here.
    group.add_argument('--current',
                       help=_('Use ultimate-io current pin config when applying config from file'), default=False,
                       action='store_true')
    group.add_argument('--indent', help=_('Set the json indent level for the output of the device configuration'),
                       default=None, metavar='INT')
    group.add_argument('--file', help=_('File path to write out the json of the device configuration'), type=str,
                       default=None, metavar='FILE-NAME')
    group.add_argument('--get-pin-config', help=_('Get ultimate-io device pin config'), default=False, action='store_true')
    group.add_argument('--set-pin-config', help=_('Set ultimate-io device pin config from config file'), type=str, default=None,
                       metavar='CONFIG-FILE')
    group.add_argument('--set-debounce', help=_('Set debounce value'), type=str, metavar='STR')
    group.add_argument('--set-pin', help=_('Set single pin'), type=str,
                       default=None, metavar=('PIN', 'ACTION', 'ALT_ACTION', 'IS_SHIFT'), nargs=4)
    group.add_argument('--set-led-config', help=_('Set ultimate-io device LEDs from config file'), type=str,
                       default=None,
                       metavar='CONFIG-FILE')
    group.add_argument('--set-led', help=_('Set single LED'), type=int, default=None,
                       metavar=('LED[1-96]', 'VALUE[0-255]'), nargs=2)
    group.add_argument('--set-all-leds', help=_('Set all LEDs to one intensity'), type=int, default=None,
                       metavar='INT[0-255]')
    group.add_argument('--set-leds-fade-rate', help=_('Set fade rade for all LEDs'), type=int, default=None,
                       metavar='INT[0-255]')
    group.add_argument('--set-leds-random-state', help=_('Set all LEDs to random states'), default=False, action='store_true')
    args = parser.parse_args()

    if not args.get_pin_config and args.indent:
        _logger.error(_('The --indent argument can only be used with the --get_pin_config argument '))
        return -1
    if not args.get_pin_config and args.file:
        _logger.error(_('The --file argument can only be used with the --get_pin_config argument '))
        return -1
    if not args.set_pin_config and args.current:
        _logger.error(_('The --current argument can only be used with the --set_pin_config argument '))
        return -1

    if args.set_pin_config or args.set_led_config:
        # Always force absolute path for config files.
        args.set_config = ToolContextManager.clean_config_path(args.set_config)
        if not os.path.exists(args.set_config):
            _logger.error(_('Unable to find configuration file specified in argument.'))
            return -1

    with ToolContextManager(tool_cmd, args) as tool_env:
        process = UltimateIOClass(args, tool_env)
        exit_code = process.run()
        return exit_code


# --- Main Program Call ---
if __name__ == "__main__":
    sys.exit(run())
