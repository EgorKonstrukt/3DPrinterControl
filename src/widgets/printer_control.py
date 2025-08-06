from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import pyqtSignal

from widgets.connection_widget import ConnectionWidget
from widgets.axis_control_widget import AxisControlWidget
from widgets.speed_widget import SpeedWidget
from widgets.extruder_widget import ExtruderWidget


class PrinterControl(QWidget):
    position_changed = pyqtSignal(float, float, float)

    def __init__(self, gcode_handler, config_manager, localization_manager):
        super().__init__()
        self.gcode_handler = gcode_handler
        self.config_manager = config_manager
        self.localization_manager = localization_manager
        self.init_ui()
        self.connect_widget_signals()

    def init_ui(self):
        layout = QVBoxLayout()

        self.tab_widget = QTabWidget()

        self.connection_widget = ConnectionWidget(self.gcode_handler, self.localization_manager)
        self.tab_widget.addTab(self.connection_widget, self.localization_manager.tr("control_connection"))

        self.axis_control_widget = AxisControlWidget(self.gcode_handler, self.localization_manager)
        self.tab_widget.addTab(self.axis_control_widget, self.localization_manager.tr("control_axis"))

        self.speed_widget = SpeedWidget(self.gcode_handler, self.localization_manager)
        self.tab_widget.addTab(self.speed_widget, self.localization_manager.tr("control_speed"))

        self.extruder_widget = ExtruderWidget(self.gcode_handler, self.localization_manager)
        self.tab_widget.addTab(self.extruder_widget, self.localization_manager.tr("control_extruder"))

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def connect_widget_signals(self):
        self.axis_control_widget.position_changed.connect(self.position_changed.emit)

    def update_position_from_3d(self, x, y, z):
        self.axis_control_widget.update_position_from_3d(x, y, z)