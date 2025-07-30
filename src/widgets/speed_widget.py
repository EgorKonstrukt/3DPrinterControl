from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                             QLabel, QSpinBox, QDoubleSpinBox, QGroupBox, QGridLayout)


class SpeedWidget(QWidget):
    def __init__(self, gcode_handler):
        super().__init__()
        self.gcode_handler = gcode_handler
        self.init_ui()
        self.init_values()
        self.connect_signals()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self._create_speed_group())
        layout.addWidget(self._create_acceleration_group())
        layout.addWidget(self._create_jerk_group())
        layout.addWidget(self._create_apply_button())
        layout.addStretch()
        self.setLayout(layout)

    def _create_speed_group(self):
        group = QGroupBox("Скорости движения")
        layout = QGridLayout()

        self.print_speed = QSpinBox()
        self.print_speed.setRange(1, 10000)
        self.print_speed.setSuffix(" мм/мин")

        self.travel_speed = QSpinBox()
        self.travel_speed.setRange(1, 15000)
        self.travel_speed.setSuffix(" мм/мин")

        self.z_speed = QSpinBox()
        self.z_speed.setRange(1, 1000)
        self.z_speed.setSuffix(" мм/мин")

        layout.addWidget(QLabel("Печать:"), 0, 0)
        layout.addWidget(self.print_speed, 0, 1)
        layout.addWidget(QLabel("Перемещение:"), 1, 0)
        layout.addWidget(self.travel_speed, 1, 1)
        layout.addWidget(QLabel("Z-ось:"), 2, 0)
        layout.addWidget(self.z_speed, 2, 1)

        group.setLayout(layout)
        return group

    def _create_acceleration_group(self):
        group = QGroupBox("Ускорения")
        layout = QGridLayout()

        self.print_acceleration = QSpinBox()
        self.print_acceleration.setRange(100, 10000)
        self.print_acceleration.setSuffix(" мм/с²")

        self.travel_acceleration = QSpinBox()
        self.travel_acceleration.setRange(100, 10000)
        self.travel_acceleration.setSuffix(" мм/с²")

        layout.addWidget(QLabel("Печать:"), 0, 0)
        layout.addWidget(self.print_acceleration, 0, 1)
        layout.addWidget(QLabel("Перемещение:"), 1, 0)
        layout.addWidget(self.travel_acceleration, 1, 1)

        group.setLayout(layout)
        return group

    def _create_jerk_group(self):
        group = QGroupBox("Рывки")
        layout = QGridLayout()

        self.xy_jerk = QDoubleSpinBox()
        self.xy_jerk.setRange(0.1, 50.0)
        self.xy_jerk.setSuffix(" мм/с")

        self.z_jerk = QDoubleSpinBox()
        self.z_jerk.setRange(0.1, 10.0)
        self.z_jerk.setSuffix(" мм/с")

        self.e_jerk = QDoubleSpinBox()
        self.e_jerk.setRange(0.1, 25.0)
        self.e_jerk.setSuffix(" мм/с")

        layout.addWidget(QLabel("XY:"), 0, 0)
        layout.addWidget(self.xy_jerk, 0, 1)
        layout.addWidget(QLabel("Z:"), 1, 0)
        layout.addWidget(self.z_jerk, 1, 1)
        layout.addWidget(QLabel("E:"), 2, 0)
        layout.addWidget(self.e_jerk, 2, 1)

        group.setLayout(layout)
        return group

    def _create_apply_button(self):
        self.apply_btn = QPushButton("Применить настройки")
        self.apply_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; }")
        return self.apply_btn

    def init_values(self):
        self.print_speed.setValue(1500)
        self.travel_speed.setValue(3000)
        self.z_speed.setValue(300)
        self.print_acceleration.setValue(1000)
        self.travel_acceleration.setValue(3000)
        self.xy_jerk.setValue(10.0)
        self.z_jerk.setValue(0.4)
        self.e_jerk.setValue(5.0)

    def connect_signals(self):
        self.apply_btn.clicked.connect(self.apply_speed_settings)

    def apply_speed_settings(self):
        print_speed = self.print_speed.value()
        travel_speed = self.travel_speed.value()
        z_speed = self.z_speed.value()

        print_accel = self.print_acceleration.value()
        travel_accel = self.travel_acceleration.value()

        xy_jerk = self.xy_jerk.value()
        z_jerk = self.z_jerk.value()
        e_jerk = self.e_jerk.value()

        self.gcode_handler._send_command(f"M203 X{travel_speed/60:.2f} Y{travel_speed/60:.2f} Z{z_speed/60:.2f}")
        self.gcode_handler._send_command(f"M204 P{print_accel} T{travel_accel}")
        self.gcode_handler._send_command(f"M205 X{xy_jerk} Y{xy_jerk} Z{z_jerk} E{e_jerk}")
        self.gcode_handler._send_command(f"M220 S{print_speed/100}")
        self.gcode_handler._send_command(f"M221 S{100}")