#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import os
import sys

from ultimarc.ui.device_model import DeviceModel

try:
    from PySide6.QtQuickControls2 import QQuickStyle
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
except ImportError:
    print("\nError: Ultimarc QT libraries not installed, unable to launch UI.")
    print("   To install, run: 'pip install ultimarc[ui]'\n")
    sys.exit(-1)

from ultimarc import translate_gettext as _
from ultimarc.tools import ToolContextManager
from ultimarc.ui.devices_model import DevicesModel
from ultimarc.ui.devices_sort_filter_proxy_model import DevicesSortProxyModel
from ultimarc.ui.units import Units

import ultimarc.qml.rc_assets

_logger = logging.getLogger('ultimarc')

_tool_cmd = _('ui')
_tool_qml = _('qml/main.qml')
_tool_title = _('Ultimarc Editor')
_tool_version = _('1.0.0-alpha.7')


def run():
    proj_path = os.path.abspath(__file__).split('/ultimarc/')[0]
    app_base = os.path.join(proj_path, 'ultimarc')

    os.environ['PYTHONPATH'] = proj_path

    """ Main UI entry point """
    app = QGuiApplication(sys.argv)

    QQuickStyle.setStyle('Fusion')

    ToolContextManager.initialize_logging('ultimarc')  # Configure logging

    # Setup default argparser arguments.
    parser = ToolContextManager.get_argparser('ultimarc', _tool_title)
    args = parser.parse_args()

    # Instantiate UI.
    # QCoreApplication.setOrganizationDomain('')
    # QCoreApplication.setOrganizationName('')
    QCoreApplication.setApplicationName(_tool_title)

    engine = QQmlApplicationEngine()
    engine.addImportPath(app_base)

    with ToolContextManager(_tool_cmd, args) as tool_env:
        # Local class instantiation
        units = Units()

        device_model = DeviceModel(args, tool_env)
        devices = DevicesModel(args, tool_env, device_model)
        sort_devices = DevicesSortProxyModel()

        # Attach source model to proxy models
        sort_devices.setSourceModel(devices)

        # Connect Python to QML
        context = engine.rootContext()
        context.setContextProperty('_version', _tool_version)
        context.setContextProperty('_devices', devices)
        context.setContextProperty('_sort_devices', sort_devices)
        context.setContextProperty('_device_model', device_model)
        context.setContextProperty('_units', units)

        engine.loadFromModule('qml', 'Main')
        if not engine.rootObjects():
            _logger.error(_('Bad UI settings found, aborting.'))
            sys.exit(-1)

        # Run UI loop.
        ret = app.exec()

    sys.exit(ret)


if __name__ == '__main__':
    run()
