#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
# Template for Ultimarc CLI tools.
#
import logging
import sys

from ultimarc import translate_gettext as _
from ultimarc.tools import ToolContextManager, ToolEnvironmentObject


_logger = logging.getLogger('ultimarc')

# Tool_cmd and tool_desc name are required.
# Remember to add/update bash completion in 'tools.bash'
tool_cmd = _('template')
tool_desc = _('put tool help description here')


class ProgramTemplateClass(object):
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

    # TODO:  Setup additional program arguments here.
    args = parser.parse_args()

    with ToolContextManager(tool_cmd, args) as tool_env:
        process = ProgramTemplateClass(args, tool_env)
        exit_code = process.run()
        return exit_code


# --- Main Program Call ---
if __name__ == "__main__":
    sys.exit(run())
