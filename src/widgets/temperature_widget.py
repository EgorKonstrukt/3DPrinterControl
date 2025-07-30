from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSpinBox, QGroupBox, QGridLayout, QProgressBar)


class TemperatureWidget(QWidget):
    def __init__(self, gcode_handler):
        super().__init__()
        self.gcode_handler = gcode_handler
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self._create_extruder_group())
        layout.addWidget(self._create_bed_group())
        layout.addWidget(self._create_presets_group())
        layout.addStretch()
        self.setLayout(layout)

    def _create_extruder_group(self):
        group = QGroupBox("Экструдер")
        layout = QGridLayout()

        self.extruder_temp_target = QSpinBox()
        self.extruder_temp_target.setRange(0, 300)
        self.extruder_temp_target.setSuffix(" °C")

        self.extruder_temp_current = QLabel("0 °C")
        self.extruder_temp_progress = QProgressBar()
        self.extruder_temp_progress.setRange(0, 300)

        self.set_extruder_temp_btn = QPushButton("Установить")
        self.extruder_off_btn = QPushButton("Выключить")

        layout.addWidget(QLabel("Целевая:"), 0, 0)
        layout.addWidget(self.extruder_temp_target, 0, 1)
        layout.addWidget(self.set_extruder_temp_btn, 0, 2)
        layout.addWidget(QLabel("Текущая:"), 1, 0)
        layout.addWidget(self.extruder_temp_current, 1, 1)
        layout.addWidget(self.extruder_off_btn, 1, 2)
        layout.addWidget(self.extruder_temp_progress, 2, 0, 1, 3)

        group.setLayout(layout)
        return group

    def _create_bed_group(self):
        group = QGroupBox("Стол")
        layout = QGridLayout()

        self.bed_temp_target = QSpinBox()
        self.bed_temp_target.setRange(0, 120)
        self.bed_temp_target.setSuffix(" °C")

        self.bed_temp_current = QLabel("0 °C")
        self.bed_temp_progress = QProgressBar()
        self.bed_temp_progress.setRange(0, 120)

        self.set_bed_temp_btn = QPushButton("Установить")
        self.bed_off_btn = QPushButton("Выключить")

        layout.addWidget(QLabel("Целевая:"), 0, 0)
        layout.addWidget(self.bed_temp_target, 0, 1)
        layout.addWidget(self.set_bed_temp_btn, 0, 2)
        layout.addWidget(QLabel("Текущая:"), 1, 0)
        layout.addWidget(self.bed_temp_current, 1, 1)
        layout.addWidget(self.bed_off_btn, 1, 2)
        layout.addWidget(self.bed_temp_progress, 2, 0, 1, 3)

        group.setLayout(layout)
        return group

    def _create_presets_group(self):
        group = QGroupBox("Предустановки")
        layout = QHBoxLayout()

        self.pla_preset_btn = QPushButton("PLA\n(200°C / 60°C)")
        self.abs_preset_btn = QPushButton("ABS\n(240°C / 80°C)")
        self.petg_preset_btn = QPushButton("PETG\n(230°C / 70°C)")
        self.cool_down_btn = QPushButton("Охлаждение\n(0°C / 0°C)")

        layout.addWidget(self.pla_preset_btn)
        layout.addWidget(self.abs_preset_btn)
        layout.addWidget(self.petg_preset_btn)
        layout.addWidget(self.cool_down_btn)

        group.setLayout(layout)
        return group

    def connect_signals(self):
        self.set_extruder_temp_btn.clicked.connect(self.set_extruder_temp)
        self.extruder_off_btn.clicked.connect(lambda: self.set_extruder_temp(0))
        self.set_bed_temp_btn.clicked.connect(self.set_bed_temp)
        self.bed_off_btn.clicked.connect(lambda: self.set_bed_temp(0))

        self.pla_preset_btn.clicked.connect(lambda: self.set_temp_preset(200, 60))
        self.abs_preset_btn.clicked.connect(lambda: self.set_temp_preset(240, 80))
        self.petg_preset_btn.clicked.connect(lambda: self.set_temp_preset(230, 70))
        self.cool_down_btn.clicked.connect(lambda: self.set_temp_preset(0, 0))

    def set_extruder_temp(self, temp=None):
        if temp is None:
            temp = self.extruder_temp_target.value()
        self.gcode_handler._send_command(f"M104 S{temp}")

    def set_bed_temp(self, temp=None):
        if temp is None:
            temp = self.bed_temp_target.value()
        self.gcode_handler._send_command(f"M140 S{temp}")

    def set_temp_preset(self, extruder_temp, bed_temp):
        self.extruder_temp_target.setValue(extruder_temp)
        self.bed_temp_target.setValue(bed_temp)
        self.set_extruder_temp(extruder_temp)
        self.set_bed_temp(bed_temp)

    def update_temperatures(self, extruder_temp, bed_temp):
        self.extruder_temp_current.setText(f"{extruder_temp} °C")
        self.bed_temp_current.setText(f"{bed_temp} °C")
        self.extruder_temp_progress.setValue(int(extruder_temp))
        self.bed_temp_progress.setValue(int(bed_temp))