#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import sys

from PySide6 import QtCore, QtWidgets, QtQml

from ultimarc import translate_gettext as _
from ultimarc.tools import ToolContextManager
from ultimarc.ui.device_class_model import DeviceClassModel
from ultimarc.ui.devices_filter_proxy_model import DevicesFilterProxyModel, ClassFilterProxyModel
from ultimarc.ui.devices_model import DevicesModel
from ultimarc.ui.devices_sort_proxy_model import DevicesSortProxyModel
from ultimarc.ui.units import Units

import ultimarc.qml.rc_assets

_logger = logging.getLogger('ultimarc')

_tool_cmd = _('ui')
_tool_title = _('Ultimarc Editor')

if __name__ == '__main__':
    """ Main entry point """
    app = QtWidgets.QApplication(sys.argv)
    # QtQuickControls2.QQuickStyle('org.fedoraproject.AdwaitaTheme')
    # QtQuickControls2.QQuickStyle('Fusion')

    ToolContextManager.initialize_logging('ultimarc')  # Configure logging

    # Setup default argparser arguments.
    parser = ToolContextManager.get_argparser('ultimarc', _tool_title)
    args = parser.parse_args()

    # Instantiate UI.
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtCore.QCoreApplication.setOrganizationDomain('SnowyWhitewater.org')
    QtCore.QCoreApplication.setOrganizationName('SnowyWhitewater.org')
    QtCore.QCoreApplication.setApplicationName('UltimarcEditor')
    engine = QtQml.QQmlApplicationEngine()

    with ToolContextManager(_tool_cmd, args) as tool_env:
        # Local class instantiation
        units = Units()
        device_filter = DevicesFilterProxyModel()
        class_filter = ClassFilterProxyModel()
        device_sort = DevicesSortProxyModel()
        devices = DevicesModel(args, tool_env)
        # Provide the list to the string model from the filter model
        device_class = DeviceClassModel()
        device_sort.setSourceModel(devices)
        class_filter.setSourceModel(device_sort)
        device_filter.setSourceModel(class_filter)

        # Connect Python to QML
        context = engine.rootContext()
        context.setContextProperty('_ultimarc_version', '0.1')
        context.setContextProperty('_class', class_filter)
        context.setContextProperty('_devices', device_filter)
        # devices is only used to calculate the position by the number of devices connected in the QML.
        context.setContextProperty('_d', devices)
        context.setContextProperty('_classes', device_class)
        context.setContextProperty('_units', units)

        url = QtCore.QUrl.fromLocalFile('qml/main.qml')

        engine.load(url)
        if not engine.rootObjects():
            _logger.error(_('Bad UI settings found, aborting.'))
            sys.exit(-1)

        # Run UI loop.
        ret = app.exec_()

    sys.exit(ret)
