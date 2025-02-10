#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import os
import sys

from ultimarc.ui.device_model import DeviceModel

try:
    from PySide6 import QtCore, QtWidgets, QtQml
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
_tool_version = _('1.0.0-alpha.6')


def run():
    proj_path = os.path.abspath(__file__).split('/ultimarc/')[0]
    app_base = os.path.join(proj_path, 'ultimarc')

    os.environ['PYTHONPATH'] = proj_path

    """ Main UI entry point """
    app = QtWidgets.QApplication(sys.argv)

    ToolContextManager.initialize_logging('ultimarc')  # Configure logging

    # Setup default argparser arguments.
    parser = ToolContextManager.get_argparser('ultimarc', _tool_title)
    args = parser.parse_args()

    # Instantiate UI.
    QtCore.QCoreApplication.setOrganizationDomain('SnowyWhitewater.org')
    QtCore.QCoreApplication.setOrganizationName('SnowyWhitewater')
    QtCore.QCoreApplication.setApplicationName('Ultimarc Editor')
    engine = QtQml.QQmlApplicationEngine()

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
        context.setContextProperty('_ultimarc_version', _tool_version)
        context.setContextProperty('_devices', devices)
        context.setContextProperty('_sort_devices', sort_devices)
        context.setContextProperty('_device_model', device_model)
        context.setContextProperty('_units', units)

        url = QtCore.QUrl.fromLocalFile(os.path.join(app_base, _tool_qml))

        engine.load(url)
        if not engine.rootObjects():
            _logger.error(_('Bad UI settings found, aborting.'))
            sys.exit(-1)

        # Run UI loop.
        ret = app.exec()

    sys.exit(ret)


if __name__ == '__main__':
    run()
