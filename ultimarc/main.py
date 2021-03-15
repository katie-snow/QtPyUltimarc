#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import sys

from PySide6 import QtCore, QtWidgets, QtQml, QtQuick, QtQuickControls2

from ultimarc import translate_gettext as _
from ultimarc.tools import ToolContextManager
from ultimarc.ui.devices_list_proxy_model import DeviceListProxyModel
from ultimarc.ui.devices_model import DevicesModel
from ultimarc.ui.units import Units

_logger = logging.getLogger('ultimarc')

_tool_cmd = _('ui')
_tool_title = _('Ultimarc Editor')

if __name__ == '__main__':
    """ Main entry point """
    ToolContextManager.initialize_logging('ultimarc')  # Configure logging

    # Setup default argparser arguments.
    parser = ToolContextManager.get_argparser('ultimarc', _tool_title)
    args = parser.parse_args()

    # Instantiate UI.
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtCore.QCoreApplication.setOrganizationDomain('SnowyWhitewater.org')
    QtCore.QCoreApplication.setOrganizationName('SnowyWhitewater.org')
    QtCore.QCoreApplication.setApplicationName('UltimarcEditor')

    app = QtWidgets.QApplication(sys.argv)
    # QtQuickControls2.QQuickStyle('org.fedoraproject.AdwaitaTheme')
    #QtQuickControls2.QQuickStyle('Fusion')
    engine = QtQml.QQmlApplicationEngine()

    with ToolContextManager(_tool_cmd, args) as tool_env:
        # Local class instantiation
        units = Units()
        devices = DeviceListProxyModel()
        model = DevicesModel(args, tool_env)
        devices.setSourceModel(model)

        # Connect Python to QML
        context = engine.rootContext()
        context.setContextProperty('_ultimarc_version', '0.1')
        context.setContextProperty('_releases', devices)
        context.setContextProperty('_deviceModel', model)
        context.setContextProperty('_units', units)

        url = QtCore.QUrl.fromLocalFile('qml/main.qml')

        engine.load(url)
        if not engine.rootObjects():
            _logger.error(_('Bad UI settings found, aborting.'))
            sys.exit(-1)

        # Run UI loop.
        ret = app.exec_()

    sys.exit(ret)
