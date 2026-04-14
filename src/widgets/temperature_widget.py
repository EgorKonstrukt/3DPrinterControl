from PyQt5.QtCore import QTimer
from PyQt5.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSlider, QCheckBox, QSpinBox, QGroupBox,
                             QGridLayout, QFrame, QSplitter, QComboBox, QProgressBar, )
from PyQt5.QtCore import Qt as QtWidgets


class TemperatureWidget(QWidget):
    def __init__(self, gcode_handler, config_manager, localization_manager):
        super().__init__()
        self.gcode_handler = gcode_handler
        self.config_manager = config_manager
        self.localization_manager = localization_manager

        self.extruder_data = []
        self.bed_data = []
        self.max_data_points = 60

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

        self.chart = QChart()
        self.chart.setTitle(self.localization_manager.tr("temperature_chart_title"))
        self.chart.legend().hide()
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.extruder_series = QLineSeries()
        self.extruder_series.setName(self.localization_manager.tr("temperature_extruder"))
        self.chart.addSeries(self.extruder_series)

        self.bed_series = QLineSeries()
        self.bed_series.setName(self.localization_manager.tr("temperature_bed"))
        self.chart.addSeries(self.bed_series)

        axis_x = QValueAxis()
        axis_x.setLabelFormat("%i")
        axis_x.setTitleText(self.localization_manager.tr("temperature_chart_time"))
        self.chart.addAxis(axis_x, QtWidgets.AlignmentFlag.AlignBottom)
        self.extruder_series.attachAxis(axis_x)
        self.bed_series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%i °C")
        axis_y.setTitleText(self.localization_manager.tr("temperature_chart_temp"))
        axis_y.setRange(0, 300)
        self.chart.addAxis(axis_y, QtWidgets.AlignmentFlag.AlignLeft)
        self.extruder_series.attachAxis(axis_y)
        self.bed_series.attachAxis(axis_y)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(self.chart_view)

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
        self.chart_timer.setInterval(1000)  # Update every 1 second
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
            self.extruder_data.append(current)
        elif heater == 'bed':
            self.bed_temp_current.setText(f"{current} °C")
            self.bed_temp_progress.setValue(int(current))
            self.bed_data.append(current)

        if len(self.extruder_data) > self.max_data_points:
            self.extruder_data.pop(0)
        if len(self.bed_data) > self.max_data_points:
            self.bed_data.pop(0)

    def update_chart(self):
        self.extruder_series.clear()
        self.bed_series.clear()
        for i, temp in enumerate(self.extruder_data):
            self.extruder_series.append(i, temp)
        for i, temp in enumerate(self.bed_data):
            self.bed_series.append(i, temp)

        if self.extruder_data or self.bed_data:
            max_val = max(max(self.extruder_data) if self.extruder_data else 0, max(self.bed_data) if self.bed_data else 0)
            min_val = min(min(self.extruder_data) if self.extruder_data else 300, min(self.bed_data) if self.bed_data else 300)
            self.chart.axes(QtWidgets.AlignmentFlag.AlignLeft)[0].setRange(min_val - 10, max_val + 10)
            self.chart.axes(QtWidgets.AlignmentFlag.AlignBottom)[0].setRange(0, self.max_data_points)