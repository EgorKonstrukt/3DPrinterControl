from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox, QGroupBox, QGridLayout, QProgressBar
from PyQt5.Qt import Qt
from pyqt5_chart_widget import ChartWidget


class TemperatureWidget(QWidget):
    def __init__(self, gcode_handler, config_manager, localization_manager):
        super().__init__()
        self.gcode_handler = gcode_handler
        self.config_manager = config_manager
        self.localization_manager = localization_manager

        self.extruder_data = []
        self.bed_data = []
        self.max_data_points = 60
        self.time_counter = 0

        self.init_ui()
        self.connect_signals()
        self.start_chart_timer()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self._create_extruder_group())
        layout.addWidget(self._create_bed_group())
        layout.addWidget(self._create_presets_group())
        layout.addWidget(self._create_chart_group())
        layout.addStretch()
        self.setLayout(layout)

    def _create_extruder_group(self):
        group = QGroupBox(self.localization_manager.tr("temperature_extruder"))
        layout = QGridLayout()

        self.extruder_temp_target = QSpinBox()
        self.extruder_temp_target.setRange(0, 300)
        self.extruder_temp_target.setSuffix(" °C")
        self.extruder_temp_target.setValue(self.config_manager.get("printer.default_temperatures.extruder"))

        self.extruder_temp_current = QLabel("0 °C")
        self.extruder_temp_progress = QProgressBar()
        self.extruder_temp_progress.setRange(0, 300)

        self.set_extruder_temp_btn = QPushButton(self.localization_manager.tr("temperature_set"))
        self.extruder_off_btn = QPushButton(self.localization_manager.tr("temperature_off"))

        layout.addWidget(QLabel(self.localization_manager.tr("temperature_target")), 0, 0)
        layout.addWidget(self.extruder_temp_target, 0, 1)
        layout.addWidget(self.set_extruder_temp_btn, 0, 2)
        layout.addWidget(QLabel(self.localization_manager.tr("temperature_current")), 1, 0)
        layout.addWidget(self.extruder_temp_current, 1, 1)
        layout.addWidget(self.extruder_off_btn, 1, 2)
        layout.addWidget(self.extruder_temp_progress, 2, 0, 1, 3)

        group.setLayout(layout)
        return group

    def _create_bed_group(self):
        group = QGroupBox(self.localization_manager.tr("temperature_bed"))
        layout = QGridLayout()

        self.bed_temp_target = QSpinBox()
        self.bed_temp_target.setRange(0, 120)
        self.bed_temp_target.setSuffix(" °C")
        self.bed_temp_target.setValue(self.config_manager.get("printer.default_temperatures.bed"))

        self.bed_temp_current = QLabel("0 °C")
        self.bed_temp_progress = QProgressBar()
        self.bed_temp_progress.setRange(0, 120)

        self.set_bed_temp_btn = QPushButton(self.localization_manager.tr("temperature_set"))
        self.bed_off_btn = QPushButton(self.localization_manager.tr("temperature_off"))

        layout.addWidget(QLabel(self.localization_manager.tr("temperature_target")), 0, 0)
        layout.addWidget(self.bed_temp_target, 0, 1)
        layout.addWidget(self.set_bed_temp_btn, 0, 2)
        layout.addWidget(QLabel(self.localization_manager.tr("temperature_current")), 1, 0)
        layout.addWidget(self.bed_temp_current, 1, 1)
        layout.addWidget(self.bed_off_btn, 1, 2)
        layout.addWidget(self.bed_temp_progress, 2, 0, 1, 3)

        group.setLayout(layout)
        return group

    def _create_presets_group(self):
        group = QGroupBox(self.localization_manager.tr("temperature_presets"))
        layout = QHBoxLayout()

        self.pla_preset_btn = QPushButton(self.localization_manager.tr("temperature_preset_pla"))
        self.abs_preset_btn = QPushButton(self.localization_manager.tr("temperature_preset_abs"))
        self.petg_preset_btn = QPushButton(self.localization_manager.tr("temperature_preset_petg"))
        self.cool_down_btn = QPushButton(self.localization_manager.tr("temperature_preset_cooldown"))

        layout.addWidget(self.pla_preset_btn)
        layout.addWidget(self.abs_preset_btn)
        layout.addWidget(self.petg_preset_btn)
        layout.addWidget(self.cool_down_btn)

        group.setLayout(layout)
        return group

    def _create_chart_group(self):
        group = QGroupBox(self.localization_manager.tr("temperature_chart"))
        layout = QVBoxLayout()

        self.chart = ChartWidget(show_toolbar=False, show_legend=True)
        self.chart.setLabel("bottom", self.localization_manager.tr("temperature_chart_time"))
        self.chart.setLabel("left", self.localization_manager.tr("temperature_chart_temp"))
        
        red_pen = QPen(QColor(255, 0, 0), 2)
        blue_pen = QPen(QColor(0, 0, 255), 2)
        
        self.extruder_line = self.chart.plot(color="#FF0000", width=2, label=self.localization_manager.tr("temperature_extruder"))
        self.bed_line = self.chart.plot(color="#0000FF", width=2, label=self.localization_manager.tr("temperature_bed"))

        layout.addWidget(self.chart)
        group.setLayout(layout)
        return group

    def connect_signals(self):
        self.set_extruder_temp_btn.clicked.connect(lambda: self.set_extruder_temp(self.extruder_temp_target.value()))
        self.extruder_off_btn.clicked.connect(lambda: self.set_extruder_temp(0))

        self.set_bed_temp_btn.clicked.connect(lambda: self.set_bed_temp(self.bed_temp_target.value()))
        self.bed_off_btn.clicked.connect(lambda: self.set_bed_temp(0))

        self.pla_preset_btn.clicked.connect(lambda: self.set_temp_preset(200, 60))
        self.abs_preset_btn.clicked.connect(lambda: self.set_temp_preset(240, 80))
        self.petg_preset_btn.clicked.connect(lambda: self.set_temp_preset(230, 70))
        self.cool_down_btn.clicked.connect(lambda: self.set_temp_preset(0, 0))

        self.gcode_handler.temperature_changed.connect(self.update_temperatures)

    def start_chart_timer(self):
        self.chart_timer = QTimer()
        self.chart_timer.setInterval(1000)
        self.chart_timer.timeout.connect(self.update_chart)
        self.chart_timer.start()

    def set_extruder_temp(self, temp=None):
        if temp is None:
            temp = self.extruder_temp_target.value()
        self.gcode_handler.send_command(f"M104 S{temp}")

    def set_bed_temp(self, temp=None):
        if temp is None:
            temp = self.bed_temp_target.value()
        self.gcode_handler.send_command(f"M140 S{temp}")

    def set_temp_preset(self, extruder_temp, bed_temp):
        self.extruder_temp_target.setValue(extruder_temp)
        self.bed_temp_target.setValue(bed_temp)
        self.set_extruder_temp(extruder_temp)
        self.set_bed_temp(bed_temp)

    def update_temperatures(self, heater, current, target):
        if heater == 'extruder':
            self.extruder_temp_current.setText(f"{current} °C")
            self.extruder_temp_progress.setValue(int(current))
            self.extruder_data.append((self.time_counter, current))
        elif heater == 'bed':
            self.bed_temp_current.setText(f"{current} °C")
            self.bed_temp_progress.setValue(int(current))
            self.bed_data.append((self.time_counter, current))

        if len(self.extruder_data) > self.max_data_points:
            self.extruder_data.pop(0)
        if len(self.bed_data) > self.max_data_points:
            self.bed_data.pop(0)

    def update_chart(self):
        self.time_counter += 1
        
        extruder_xs = [t for t, _ in self.extruder_data]
        extruder_ys = [temp for _, temp in self.extruder_data]
        bed_xs = [t for t, _ in self.bed_data]
        bed_ys = [temp for _, temp in self.bed_data]
        
        self.extruder_line.setData(extruder_xs, extruder_ys)
        self.bed_line.setData(bed_xs, bed_ys)

        if self.extruder_data or self.bed_data:
            all_temps = [temp for _, temp in self.extruder_data] + [temp for _, temp in self.bed_data]
            if all_temps:
                max_val = max(all_temps)
                min_val = min(all_temps)
                self.chart._vy0 = max(0, min_val - 10)
                self.chart._vy1 = max_val + 10
                self.chart._vx0 = 0
                self.chart._vx1 = self.max_data_points
                self.chart._canvas.update()
