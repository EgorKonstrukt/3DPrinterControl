from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSpinBox, QDoubleSpinBox, QGroupBox, QGridLayout,
                             QSlider, QCheckBox)
from PyQt6.QtCore import Qt


class ExtruderWidget(QWidget):
    def __init__(self, gcode_handler):
        super().__init__()
        self.gcode_handler = gcode_handler
        self.init_ui()
        self.init_values()
        self.connect_signals()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self._create_extrude_group())
        layout.addWidget(self._create_fan_group())
        layout.addStretch()
        self.setLayout(layout)

    def _create_extrude_group(self):
        group = QGroupBox("Экструзия")
        layout = QGridLayout()

        self.extrude_length = QDoubleSpinBox()
        self.extrude_length.setRange(0.1, 100.0)
        self.extrude_length.setSuffix(" мм")

        self.extrude_speed = QSpinBox()
        self.extrude_speed.setRange(1, 1000)
        self.extrude_speed.setSuffix(" мм/мин")

        self.extrude_btn = QPushButton("Подать")
        self.retract_btn = QPushButton("Втянуть")

        layout.addWidget(QLabel("Длина:"), 0, 0)
        layout.addWidget(self.extrude_length, 0, 1)
        layout.addWidget(QLabel("Скорость:"), 1, 0)
        layout.addWidget(self.extrude_speed, 1, 1)
        layout.addWidget(self.extrude_btn, 2, 0)
        layout.addWidget(self.retract_btn, 2, 1)

        group.setLayout(layout)
        return group

    def _create_fan_group(self):
        group = QGroupBox("Вентиляторы")
        layout = QGridLayout()

        self.part_fan_slider = QSlider(Qt.Orientation.Horizontal)
        self.part_fan_slider.setRange(0, 255)
        self.part_fan_label = QLabel("0%")

        self.hotend_fan_checkbox = QCheckBox("Вентилятор хотенда")

        layout.addWidget(QLabel("Обдув детали:"), 0, 0)
        layout.addWidget(self.part_fan_slider, 0, 1)
        layout.addWidget(self.part_fan_label, 0, 2)
        layout.addWidget(self.hotend_fan_checkbox, 1, 0, 1, 3)

        group.setLayout(layout)
        return group

    def init_values(self):
        self.extrude_length.setValue(10.0)
        self.extrude_speed.setValue(100)
        self.part_fan_slider.setValue(0)
        self.hotend_fan_checkbox.setChecked(True)

    def connect_signals(self):
        self.extrude_btn.clicked.connect(self.extrude_filament)
        self.retract_btn.clicked.connect(self.retract_filament)
        self.part_fan_slider.valueChanged.connect(self.update_part_fan)
        self.hotend_fan_checkbox.toggled.connect(self.toggle_hotend_fan)

    def extrude_filament(self):
        length = self.extrude_length.value()
        speed = self.extrude_speed.value()
        self.gcode_handler._send_command(f"G1 E{length} F{speed}")

    def retract_filament(self):
        length = self.extrude_length.value()
        speed = self.extrude_speed.value()
        self.gcode_handler._send_command(f"G1 E-{length} F{speed}")

    def update_part_fan(self, value):
        percentage = int((value / 255) * 100)
        self.part_fan_label.setText(f"{percentage}%")
        self.gcode_handler._send_command(f"M106 S{value}")

    def toggle_hotend_fan(self, checked):
        if checked:
            self.gcode_handler._send_command("M106 P1 S255")
        else:
            self.gcode_handler._send_command("M106 P1 S0")