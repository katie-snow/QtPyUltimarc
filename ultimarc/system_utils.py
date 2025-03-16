# -*- coding: utf-8 -*-
#
# Small helper functions for system services
#
# !!! This file is python 3.x compliant !!!
#

import logging
import os
import subprocess
import sys

try:
    import requests
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass

_logger = logging.getLogger("ultimarc")


class TerminalColors(object):
    """
    Simple class for setting terminal colors.
    https://en.wikipedia.org/wiki/ANSI_escape_code
    """

    reset = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'

    fg_black = '\033[38;5;0m'
    fg_red = '\033[38;5;1m'
    fg_green = '\033[38;5;2m'
    fg_yellow = '\033[38;5;3m'
    fg_blue = '\033[38;5;4m'
    fg_magenta = '\033[38;5;5m'
    fg_cyan = '\033[38;5;6m'
    fg_white = '\033[38;5;7m'

    fg_bright_black = '\033[38;5;8m'
    fg_bright_red = '\033[38;5;9m'
    fg_bright_green = '\033[38;5;10m'
    fg_bright_yellow = '\033[38;5;11m'
    fg_bright_blue = '\033[38;5;12m'
    fg_bright_magenta = '\033[38;5;13m'
    fg_bright_cyan = '\033[38;5;14m'
    fg_bright_white = '\033[38;5;15m'

    bg_black = '\033[48;5;0m'
    bg_red = '\033[48;5;1m'
    bg_green = '\033[48;5;2m'
    bg_yellow = '\033[48;5;3m'
    bg_blue = '\033[48;5;4m'
    bg_magenta = '\033[48;5;5m'
    bg_cyan = '\033[48;5;6m'
    bg_white = '\033[48;5;7m'

    bg_bright_black = '\033[48;5;8m'
    bg_bright_red = '\033[48;5;9m'
    bg_bright_green = '\033[48;5;10m'
    bg_bright_yellow = '\033[48;5;11m'
    bg_bright_blue = '\033[48;5;12m'
    bg_bright_magenta = '\033[48;5;13m'
    bg_bright_cyan = '\033[48;5;14m'
    bg_bright_white = '\033[48;5;15m'

    _default_format = ''
    _default_background = ''
    _default_foreground = ''

    def custom_fg_color(self, index: int) -> str:
        """
        Get a custom color seq
        :param index: intger 0 - 255
        :return: string
        """
        return f'\033[38;5;{index}m'

    def custom_bg_color(self, index: int) -> str:
        """
        Get a custom color seq
        :param index: intger 0 - 255
        :return: string
        """
        return f'\033[48;5;{index}m'

    def set_default_formatting(self, *args):
        """
        Set the default colors for formatting.
        :param args: list of colors.
        """
        self._default_format = ''
        for arg in args:
            self._default_format += arg

    def set_default_background(self, *args):
        """
        Set default background colors
        :param args: list of colors
        """
        self._default_background = ''
        for arg in args:
            self._default_background += arg

    def set_default_foreground(self, *args):
        """
        Set default foreground colors
        :param args: list of colors
        """
        self._default_foreground = ''
        for arg in args:
            self._default_foreground += arg

    def fmt(self, line: str, *args) -> str:
        """
        Color a line of text
        :param line: string
        :param args: list of colors.
        :return: string
        """
        if not args:
            l = self._default_format
        else:
            l = ''
            for arg in args:
                l += arg

        l += str(line)
        l += self.reset

        l += self._default_background
        l += self._default_foreground

        return l


tc = TerminalColors()


class _ToolLoggingFormatter(logging.Formatter):
    """
    Add colorization to logging messages.
    """

    _color = TerminalColors()

    def format(self, record):
        msg = super(_ToolLoggingFormatter, self).format(record)
        if record.levelno == logging.DEBUG:
            msg = self._color.fmt(msg, self._color.fg_cyan)
        elif record.levelno == logging.ERROR:
            msg = self._color.fmt(msg, self._color.fg_bright_red)
        elif record.levelno == logging.WARNING:
            msg = self._color.fmt(msg, self._color.fg_bright_yellow)

        return msg


def setup_logging(logger, progname, debug=False, quiet=False, logfile=None):
    """
  Setup Python logging
  :param logger: Handle to logger object
  :param progname: Name of application or service
  :param debug: True if debugging enabled
  :param quiet: True if quiet output selected.
  :param logfile: Path and filename to log file to output to
  :return: Nothing
  """
    if not logger:
        return False

    # Set our logging options and formatter now that we have the program arguments.
    if debug:
        logging.basicConfig(filename=os.devnull, datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)
        formatter = _ToolLoggingFormatter("%(asctime)s {0}: %(levelname)s: %(message)s".format(progname))
    else:
        logging.basicConfig(filename=os.devnull, datefmt="%Y-%m-%d %H:%M:%S",
                            level=logging.WARNING if quiet else logging.INFO)
        # formatter = logging.Formatter('%(levelname)s: {0}: %(message)s'.format(progname))
        formatter = _ToolLoggingFormatter("%(message)s")

    # Setup stream logging handler
    handler = logging.StreamHandler(sys.stdout)
    handler.flush = sys.stdout.flush
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # Setup file logging handler
    if logfile:

        # make sure the path exists
        logpath = os.path.dirname(os.path.abspath(os.path.expanduser(logfile)))

        if not os.path.exists(logpath):
            os.makedirs(logpath)

        handler = logging.FileHandler(logfile)
        handler.setFormatter(logging.Formatter("%(asctime)s {0}: %(levelname)s: %(message)s".format(progname)))

        logger.addHandler(handler)


def run_external_program(args, cwd=None, env=None, shell=False, debug=False):
    """
  Run an external program, arguments
  :param args: program name plus arguments in a list
  :param cwd: Current working directory
  :param env: A modified environment to use
  :param shell: Use shell to execute command
  :param debug: Add '--debug' to args if '--debug' is in sys.argv
  :return: exit code, stdoutdata, stderrdata
  """

    if not args:
        _logger.debug("run_external_program: bad arguments")
        return -1, None, None

    if debug is True and "--debug" in sys.argv and "--debug" not in args:
        args.append("--debug")

    _logger.debug("external: {0}".format(os.path.basename(args[0])))

    p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, shell=shell)
    stdoutdata, stderrdata = p.communicate()
    p.wait()

    if isinstance(stdoutdata, (bytes, bytearray)):
        stdoutdata = stdoutdata.decode("utf-8")
    if isinstance(stderrdata, (bytes, bytearray)):
        stderrdata = stderrdata.decode("utf-8")

    return p.returncode, stdoutdata, stderrdata


def pid_is_running(pid: int):
    """
  Check For the existence of a unix pid.
  :param pid: integer ID of this process
  :return: True if process with this ID is running, otherwise False
  """
    # See if there is a currently running mysqld instance
    # pylint: disable=unused-variable
    args = ['ps', '-eo', 'ruid,pid,ppid,args']
    code, so, se = run_external_program(args=args)
    if code == 0:
        lines = so.split('\n')
        for line in lines:
            if str(pid) in line:
                while '  ' in line:
                    line = line.replace('  ', ' ')
                if pid == int(line.strip().split(' ')[1]) and '<defunct>' not in line:
                    return True
    return False


def write_pidfile_or_die(progname: str, pid_file: str = None):
    """
  Attempt to write our PID to the given PID file or raise an exception.
  :param progname: Name of this program
  :param pid_file: an alternate path and pid file to use
  :return: pid path and filename
  """
    if not pid_file:
        home = os.path.expanduser("~")
        pid_path = os.path.join(home, ".local/run")
        pid_file = os.path.join(pid_path, "{0}.pid".format(progname))
    else:
        pid_path = os.path.dirname(pid_file)

    if not os.path.exists(pid_path):
        os.makedirs(pid_path)

    if os.path.exists(pid_file):
        pid = int(open(pid_file).read())

        if pid_is_running(pid):
            _logger.warning("program is already running, aborting.")
            raise SystemExit

        else:
            os.remove(pid_file)

    open(pid_file, "w").write(str(os.getpid()))

    return pid_file


def remove_pidfile(progname: str, pid_file: str = None):
    """
  Remove the PID file for the given program
  :param progname: Name of this program
  :param pid_file: an alternate pid file to use
  """
    if not pid_file:
        home = os.path.expanduser("~")
        pid_path = os.path.join(home, ".local/run")
        pid_file = os.path.join(pid_path, "{0}.pid".format(progname))

    if os.path.exists(pid_file):
        os.remove(pid_file)


def print_progress_bar(iteration, total, prefix="", suffix="", decimals=1, bar_length=90, fill="█"):
    """
  Call in a loop to create terminal progress bar.
  https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
  https://gist.github.com/aubricus/f91fb55dc6ba5557fbab06119420dd6a
  :param iteration: Required  : current iteration (Int)
  :param total: Required  : total iterations (Int)
  :param prefix: Optional  : prefix string (Str)
  :param suffix: Optional  : suffix string (Str)
  :param decimals: Optional  : positive number of decimals in percent complete (Int)
  :param bar_length: Optional  : character length of bar (Int)
  :param fill: Optional  : bar fill character (Str)
  """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = fill * filled_length + "-" * (bar_length - filled_length)

    sys.stdout.write("\r{0} [{1}] {2}{3} {4}".format(prefix, bar, percents, "%", suffix))

    if iteration == total:
        sys.stdout.write("\n")
    sys.stdout.flush()


def git_project_root(path=None):
    """
    Figure out the git project top level directory.
    :param path: optional: path to check.
    :return: Git project root path or None
    """
    cwd = os.curdir
    if path:
        if not os.path.exists(path):
            raise ValueError('Invalid directory path argument')
        os.chdir(path)

    args = ['git', 'rev-parse', '--show-toplevel']
    # pylint: disable=unused-variable
    code, so, se = run_external_program(args=args)

    os.chdir(cwd)

    if code == 0:
        return so.strip()

    return None
