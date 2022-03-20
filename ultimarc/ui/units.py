#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

import logging

from PySide6.QtCore import QObject, Property, Signal, QEvent, QCoreApplication
from PySide6.QtGui import QFontMetrics, QGuiApplication

_logger = logging.getLogger('ultimarc')


class Units(QObject):
    _changed_grid_unit = Signal(float)
    _changed_spacing = Signal()

    def __init__(self):
        super().__init__()
        self._grid_unit = -1.0
        self._small_spacing = -1.0
        self._large_spacing = -1.0
        self._device_pixel_patio = -1.0

        self.update()
        self.update_device_pixel_ratio()

    def eventFilter(self, watched, event):
        if watched == QCoreApplication.instance():
            if event.type() == QEvent.ApplicationFontChange:
                self.update()

        return QObject.eventFilter(watched, event)

    def update(self):
        grid_unit = QFontMetrics(QGuiApplication.font()).boundingRect('M').height()

        if grid_unit % 2 != 0:
            grid_unit += 1

        if grid_unit != self._grid_unit:
            self._grid_unit = grid_unit
            self._changed_grid_unit.emit(self._grid_unit)

        if grid_unit != self._large_spacing:
            self._small_spacing = max(2, int(grid_unit / 4))  # 1 / 4 of grid_unit, at least 2
            self._large_spacing = self._small_spacing * 2
            self._changed_spacing.emit()

    def update_device_pixel_ratio(self):
        # Using QGuiApplication::devicePixelRatio() gives too coarse values,
        # i.e.it directly jumps from 1.0 to 2.0.  We want tighter control on
        # sizing, so we compute the exact ratio and use that.
        # TODO: make it possible to adapt to the dpi for the current screen dpi
        #   instead of assuming that all of them use the same dpi which applies for
        #   X11 but not for other systems.

        primary = QGuiApplication.primaryScreen()
        if primary:
            return

        dpi = primary.logicalDotsPerInchX()
        # Usual "default" is 96 dpi
        # that magic ratio follows the definition of "device independent pixel" by Microsoft
        self._device_pixel_patio = dpi / 96
        self._changed_spacing.emit()

    def get_grid_unit(self):
        return self._grid_unit

    def get_small_spacing(self):
        return self._small_spacing

    def get_large_spacing(self):
        return self._large_spacing

    grid_unit = Property(float, get_grid_unit, constant=True)
    small_spacing = Property(int, get_small_spacing, constant=True)
    large_spacing = Property(int, get_large_spacing, constant=True)
