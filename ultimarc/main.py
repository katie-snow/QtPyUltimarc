#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import sys

try:
    from PySide6 import QtCore, QtWidgets, QtQml
except ImportError:
    print("\nError: PyUltimarc QT libraries not installed, unable to launch UI.")
    print("   To install, run: 'pip install PyUltimarc[ui]'\n")
    sys.exit(-1)

from ultimarc import translate_gettext as _
from ultimarc.tools import ToolContextManager
from ultimarc.ui.device_class_model import DeviceClassModel
from ultimarc.ui.devices_filter_proxy_model import DevicesFilterProxyModel, ClassFilterProxyModel
from ultimarc.ui.devices_model import DevicesModel
from ultimarc.ui.devices_sort_proxy_model import DevicesSortProxyModel
from ultimarc.ui.pages import Pages
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
        pages = Pages()

        device_filter = DevicesFilterProxyModel(pages)
        class_filter = ClassFilterProxyModel(pages)
        device_sort = DevicesSortProxyModel()
        devices = DevicesModel(args, tool_env)

        # if there are no devices connected go directly to the configuration list view
        pages.set_front(devices.has_connected_devices())

        # Provide the list to the string model from the filter model
        device_class = DeviceClassModel()
        device_sort.setSourceModel(devices)
        class_filter.setSourceModel(device_sort)
        device_filter.setSourceModel(class_filter)

        # Connect Python to QML
        context = engine.rootContext()
        context.setContextProperty('_ultimarc_version', '1.1.0-alpha')
        context.setContextProperty('_class_filter', class_filter)
        context.setContextProperty('_devices_filter', device_filter)
        context.setContextProperty('_devices', devices)
        context.setContextProperty('_device_class_model', device_class)

        context.setContextProperty('_units', units)
        context.setContextProperty('_pages', pages)

        url = QtCore.QUrl.fromLocalFile('qml/main.qml')

        engine.load(url)
        if not engine.rootObjects():
            _logger.error(_('Bad UI settings found, aborting.'))
            sys.exit(-1)

        # Run UI loop.
        ret = app.exec_()

    sys.exit(ret)
