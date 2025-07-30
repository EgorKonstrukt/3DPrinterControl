from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import pyqtSignal

from widgets.connection_widget import ConnectionWidget
from widgets.axis_control_widget import AxisControlWidget
from widgets.temperature_widget import TemperatureWidget
from widgets.speed_widget import SpeedWidget
from widgets.extruder_widget import ExtruderWidget


class PrinterControl(QWidget):
    position_changed = pyqtSignal(float, float, float)

    def __init__(self, gcode_handler):
        super().__init__()
        self.gcode_handler = gcode_handler
        self.init_ui()
        self.connect_widget_signals()

    def init_ui(self):
        layout = QVBoxLayout()

        self.tab_widget = QTabWidget()

        self.connection_widget = ConnectionWidget(self.gcode_handler)
        self.tab_widget.addTab(self.connection_widget, "Подключение")

        self.axis_control_widget = AxisControlWidget(self.gcode_handler)
        self.tab_widget.addTab(self.axis_control_widget, "Управление осями")

        self.temperature_widget = TemperatureWidget(self.gcode_handler)
        self.tab_widget.addTab(self.temperature_widget, "Температура")

        self.speed_widget = SpeedWidget(self.gcode_handler)
        self.tab_widget.addTab(self.speed_widget, "Скорость")

        self.extruder_widget = ExtruderWidget(self.gcode_handler)
        self.tab_widget.addTab(self.extruder_widget, "Экструдер")

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def connect_widget_signals(self):
        self.axis_control_widget.position_changed.connect(self.position_changed.emit)

    def update_position_from_3d(self, x, y, z):
        self.axis_control_widget.update_position_from_3d(x, y, z)

    def update_temperatures(self, extruder_temp, bed_temp):
        self.temperature_widget.update_temperatures(extruder_temp, bed_temp)