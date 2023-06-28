#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import argparse
import logging
import os.path
import sys
import traceback

from ultimarc import translate_gettext as _
from ultimarc.devices import USBDevices
from ultimarc.system_utils import remove_pidfile, write_pidfile_or_die, setup_logging, tc as _tc

toolname = 'ultimarc'

_logger = logging.getLogger('ultimarc')

_VENDOR_FILTER = ['d209']  # List of USB vendor IDs.


class ToolEnvironmentObject(object):
    """ Tool environment configuration object """

    devices = None  # USBDevices object

    def __init__(self, items):
        """
        :param items: dict of config key value pairs
        """
        for k, v in items.items():
            self.__dict__[k] = v

        # Turn on terminal colors.        
        _tc.set_default_formatting(_tc.bold, _tc.custom_fg_color(43))
        _tc.set_default_foreground(_tc.custom_fg_color(152))
        _logger.info('')

    def cleanup(self):
        """ Clean up or close everything we need to """
        _logger.info(_tc.reset)  # Turn off terminal colors.


class ToolContextManager(object):
    """
    A processing context manager for cli tools
    """
    _tool_cmd = None
    _command = None
    _env = None

    _env_config_obj = None

    def __init__(self, command, args):
        """
        Initialize Tool Context Manager
        :param command: command name
        :param args: parsed argparser commandline arguments object.
        """
        if not command:
            _logger.error(_('command not set, aborting.'))
            exit(1)

        self._command = command
        # The Environment dict is where we can set up any information related to all tools.
        self._env = {
            'command': command,
            'devices': USBDevices(_VENDOR_FILTER)
        }

        write_pidfile_or_die(command)

        if not self._env:
            remove_pidfile(command)
            exit(1)

    def __enter__(self):
        """ Return object with properties set to config values """
        self._env_config_obj = ToolEnvironmentObject(self._env)
        return self._env_config_obj

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Clean up or close everything we need to """
        self._env_config_obj.cleanup()

        remove_pidfile(self._command)

        if exc_type is not None:
            print((traceback.format_exc()))
            _logger.error(_('tool encountered an unexpected error, quitting.'))
            exit(1)

    @staticmethod
    def initialize_logging(tool_cmd):
        setup_logging(
            _logger, tool_cmd, '--debug' in sys.argv, '-q' in sys.argv or '--quiet' in sys.argv,
            '{0}.log'.format(tool_cmd) if '--log-file' in sys.argv else None)

    @staticmethod
    def get_argparser(tool_cmd, tool_desc):
        """
        :param tool_cmd: Tool command line id.
        :param tool_desc: Tool description.
        """
        # Setup program arguments.
        parser = argparse.ArgumentParser(prog=tool_cmd, description=tool_desc)
        parser.add_argument('--debug', help=_('enable debug output'), default=False, action='store_true')
        parser.add_argument('--log-file', help=_('write output to a log file'), default=False, action='store_true')
        parser.add_argument('-q', '--quiet', help=_('suppress normal output'), default=False, action='store_true')
        parser.add_argument('--bus', help=_('filter by usb device bus number'), type=int, default=None)
        parser.add_argument('--address', help=_('filter by usb device address number'), type=int, default=None)
        return parser

    @staticmethod
    def clean_config_path(config_path):
        """
        Convert a config file path to an absolute path. Use 'ultimarc' directory as starting point for converting
        relative path to absolute.
        :param config_path: user provided path to config file.
        :return: absolute path to config file.
        """
        if os.path.isabs(config_path):
            return config_path
        # get ultimarc directory
        um_root = os.path.realpath(__file__)
        # Walk backward directories until we hit the 'ultimarc' directory.
        count = 0
        while count < 4 and not um_root.endswith('ultimarc'):
            um_root = os.path.dirname(um_root)
            count += 1
        if not um_root.endswith('ultimarc'):
            raise EnvironmentError('Unable to determine path to the "ultimarc" root directory.')
        tmp_path = os.path.abspath(os.path.join(um_root, config_path))
        _logger.debug(f'config path: {tmp_path}.')
        return tmp_path
