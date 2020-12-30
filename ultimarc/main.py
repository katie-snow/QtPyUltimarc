#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import sys

from PySide2 import QtCore, QtGui, QtQml

from ultimarc import translate_gettext as _
from ultimarc.tools import ToolContextManager

_logger = logging.getLogger('ultimarc')

_tool_title = _('Ultimarc Device Configuration Tool')

if __name__ == '__main__':
    """ Main entry point """
    ToolContextManager.initialize_logging('ultimarc')  # Configure logging
    # Setup default argparser arguments.
    parser = ToolContextManager.get_argparser('ultimarc', _tool_title)
    args = parser.parse_args()

    # Instantiate UI.
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtGui.QGuiApplication(sys.argv)
    engine = QtQml.QQmlApplicationEngine()
    url = QtCore.QUrl.fromLocalFile('ui/main.qml')

    engine.load(url)
    if not engine.rootObjects():
        _logger.error(_('Bad UI settings found, aborting.'))
        sys.exit(-1)

    # TODO: Get the window object to override the title with _tool_title value.

    # Run UI loop.
    ret = app.exec_()

    sys.exit(ret)
