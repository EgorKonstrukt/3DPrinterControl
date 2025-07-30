from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QFormLayout, QSpinBox, QDoubleSpinBox,
                             QComboBox, QCheckBox, QLineEdit, QPushButton,
                             QGroupBox, QDialogButtonBox, QSlider, QLabel)
from PyQt6.QtCore import Qt


class SettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Настройки")
        self.setMinimumSize(600, 500)
        self.setModal(True)

        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self._create_printer_tab()
        self._create_serial_tab()
        self._create_ui_tab()
        self._create_gcode_tab()
        self._create_calibration_tab()

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._apply_settings)
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self._restore_defaults)

        layout.addWidget(button_box)

    def _create_printer_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        build_volume_group = QGroupBox("Размеры стола печати")
        build_volume_layout = QFormLayout()
        build_volume_group.setLayout(build_volume_layout)

        self.build_volume_x = QSpinBox()
        self.build_volume_x.setRange(50, 1000)
        self.build_volume_x.setSuffix(" мм")
        build_volume_layout.addRow("Длина (X):", self.build_volume_x)

        self.build_volume_y = QSpinBox()
        self.build_volume_y.setRange(50, 1000)
        self.build_volume_y.setSuffix(" мм")
        build_volume_layout.addRow("Ширина (Y):", self.build_volume_y)

        self.build_volume_z = QSpinBox()
        self.build_volume_z.setRange(50, 1000)
        self.build_volume_z.setSuffix(" мм")
        build_volume_layout.addRow("Высота (Z):", self.build_volume_z)

        layout.addWidget(build_volume_group)

        feedrate_group = QGroupBox("Максимальные скорости")
        feedrate_layout = QFormLayout()
        feedrate_group.setLayout(feedrate_layout)

        self.max_feedrate_x = QSpinBox()
        self.max_feedrate_x.setRange(1, 10000)
        self.max_feedrate_x.setSuffix(" мм/мин")
        feedrate_layout.addRow("X:", self.max_feedrate_x)

        self.max_feedrate_y = QSpinBox()
        self.max_feedrate_y.setRange(1, 10000)
        self.max_feedrate_y.setSuffix(" мм/мин")
        feedrate_layout.addRow("Y:", self.max_feedrate_y)

        self.max_feedrate_z = QSpinBox()
        self.max_feedrate_z.setRange(1, 1000)
        self.max_feedrate_z.setSuffix(" мм/мин")
        feedrate_layout.addRow("Z:", self.max_feedrate_z)

        self.max_feedrate_e = QSpinBox()
        self.max_feedrate_e.setRange(1, 1000)
        self.max_feedrate_e.setSuffix(" мм/мин")
        feedrate_layout.addRow("Экструдер:", self.max_feedrate_e)

        layout.addWidget(feedrate_group)

        temp_group = QGroupBox("Температуры по умолчанию")
        temp_layout = QFormLayout()
        temp_group.setLayout(temp_layout)

        self.default_extruder_temp = QSpinBox()
        self.default_extruder_temp.setRange(0, 300)
        self.default_extruder_temp.setSuffix("°C")
        temp_layout.addRow("Экструдер:", self.default_extruder_temp)

        self.default_bed_temp = QSpinBox()
        self.default_bed_temp.setRange(0, 150)
        self.default_bed_temp.setSuffix("°C")
        temp_layout.addRow("Стол:", self.default_bed_temp)

        layout.addWidget(temp_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Принтер")

    def _create_serial_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        tab.setLayout(layout)

        self.serial_port = QComboBox()
        self.serial_port.setEditable(True)
        self.serial_port.addItems(["AUTO", "COM1", "COM2", "COM3", "/dev/ttyUSB0", "/dev/ttyACM0"])
        layout.addRow("Порт:", self.serial_port)

        self.serial_baudrate = QComboBox()
        self.serial_baudrate.addItems(["9600", "19200", "38400", "57600", "115200", "250000"])
        layout.addRow("Скорость:", self.serial_baudrate)

        self.serial_timeout = QDoubleSpinBox()
        self.serial_timeout.setRange(0.1, 10.0)
        self.serial_timeout.setSingleStep(0.1)
        self.serial_timeout.setSuffix(" сек")
        layout.addRow("Таймаут:", self.serial_timeout)

        self.auto_connect = QCheckBox("Автоподключение при запуске")
        layout.addRow(self.auto_connect)

        self.tab_widget.addTab(tab, "Serial")

    def _create_ui_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        appearance_group = QGroupBox("Внешний вид")
        appearance_layout = QFormLayout()
        appearance_group.setLayout(appearance_layout)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        appearance_layout.addRow("Тема:", self.theme_combo)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["ru", "en"])
        appearance_layout.addRow("Язык:", self.language_combo)

        layout.addWidget(appearance_group)

        visualization_group = QGroupBox("3D визуализация")
        visualization_layout = QFormLayout()
        visualization_group.setLayout(visualization_layout)

        self.show_grid = QCheckBox("Показать сетку")
        visualization_layout.addRow(self.show_grid)

        self.show_axes = QCheckBox("Показать оси")
        visualization_layout.addRow(self.show_axes)

        self.show_build_plate = QCheckBox("Показать стол печати")
        visualization_layout.addRow(self.show_build_plate)

        self.lighting_enabled = QCheckBox("Включить освещение")
        visualization_layout.addRow(self.lighting_enabled)

        self.smooth_movement = QCheckBox("Плавное движение")
        visualization_layout.addRow(self.smooth_movement)

        self.visualization_quality = QComboBox()
        self.visualization_quality.addItems(["low", "medium", "high"])
        visualization_layout.addRow("Качество:", self.visualization_quality)

        layout.addWidget(visualization_group)

        console_group = QGroupBox("Консоль")
        console_layout = QFormLayout()
        console_group.setLayout(console_layout)

        self.auto_scroll_console = QCheckBox("Автоскролл")
        console_layout.addRow(self.auto_scroll_console)

        self.console_max_lines = QSpinBox()
        self.console_max_lines.setRange(100, 10000)
        self.console_max_lines.setSingleStep(100)
        console_layout.addRow("Максимум строк:", self.console_max_lines)

        layout.addWidget(console_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Интерфейс")

    def _create_gcode_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        tab.setLayout(layout)

        self.auto_load_preview = QCheckBox("Автозагрузка превью")
        layout.addRow(self.auto_load_preview)

        self.show_toolpath = QCheckBox("Показать траекторию инструмента")
        layout.addRow(self.show_toolpath)

        self.highlight_current_line = QCheckBox("Подсвечивать текущую строку")
        layout.addRow(self.highlight_current_line)

        animation_layout = QHBoxLayout()
        self.animation_speed = QSlider(Qt.Orientation.Horizontal)
        self.animation_speed.setRange(1, 50)
        self.animation_speed_label = QLabel("1.0x")
        self.animation_speed.valueChanged.connect(
            lambda v: self.animation_speed_label.setText(f"{v / 10:.1f}x")
        )
        animation_layout.addWidget(self.animation_speed)
        animation_layout.addWidget(self.animation_speed_label)
        layout.addRow("Скорость анимации:", animation_layout)

        self.tab_widget.addTab(tab, "G-код")

    def _create_calibration_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        tab.setLayout(layout)

        self.bed_leveling_points = QSpinBox()
        self.bed_leveling_points.setRange(4, 25)
        layout.addRow("Точки калибровки стола:", self.bed_leveling_points)

        self.probe_offset_x = QDoubleSpinBox()
        self.probe_offset_x.setRange(-50, 50)
        self.probe_offset_x.setSingleStep(0.1)
        self.probe_offset_x.setSuffix(" мм")
        layout.addRow("Смещение датчика X:", self.probe_offset_x)

        self.probe_offset_y = QDoubleSpinBox()
        self.probe_offset_y.setRange(-50, 50)
        self.probe_offset_y.setSingleStep(0.1)
        self.probe_offset_y.setSuffix(" мм")
        layout.addRow("Смещение датчика Y:", self.probe_offset_y)

        self.probe_offset_z = QDoubleSpinBox()
        self.probe_offset_z.setRange(-10, 10)
        self.probe_offset_z.setSingleStep(0.1)
        self.probe_offset_z.setSuffix(" мм")
        layout.addRow("Смещение датчика Z:", self.probe_offset_z)

        self.z_probe_speed = QSpinBox()
        self.z_probe_speed.setRange(1, 50)
        self.z_probe_speed.setSuffix(" мм/с")
        layout.addRow("Скорость зондирования:", self.z_probe_speed)

        self.tab_widget.addTab(tab, "Калибровка")

    def _load_settings(self):
        config = self.config_manager

        build_volume = config.get('printer.build_volume')
        self.build_volume_x.setValue(build_volume['x'])
        self.build_volume_y.setValue(build_volume['y'])
        self.build_volume_z.setValue(build_volume['z'])

        max_feedrate = config.get('printer.max_feedrate')
        self.max_feedrate_x.setValue(max_feedrate['x'])
        self.max_feedrate_y.setValue(max_feedrate['y'])
        self.max_feedrate_z.setValue(max_feedrate['z'])
        self.max_feedrate_e.setValue(max_feedrate['e'])

        default_temps = config.get('printer.default_temperatures')
        self.default_extruder_temp.setValue(default_temps['extruder'])
        self.default_bed_temp.setValue(default_temps['bed'])

        self.serial_port.setCurrentText(config.get('serial.port'))
        self.serial_baudrate.setCurrentText(str(config.get('serial.baudrate')))
        self.serial_timeout.setValue(config.get('serial.timeout'))
        self.auto_connect.setChecked(config.get('serial.auto_connect'))

        self.theme_combo.setCurrentText(config.get('ui.theme'))
        self.language_combo.setCurrentText(config.get('ui.language'))
        self.show_grid.setChecked(config.get('ui.show_grid'))
        self.show_axes.setChecked(config.get('ui.show_axes'))
        self.show_build_plate.setChecked(config.get('ui.show_build_plate'))
        self.lighting_enabled.setChecked(config.get('ui.lighting_enabled'))
        self.smooth_movement.setChecked(config.get('ui.smooth_movement'))
        self.visualization_quality.setCurrentText(config.get('ui.visualization_quality'))
        self.auto_scroll_console.setChecked(config.get('ui.auto_scroll_console'))
        self.console_max_lines.setValue(config.get('ui.console_max_lines'))

        self.auto_load_preview.setChecked(config.get('gcode.auto_load_preview'))
        self.show_toolpath.setChecked(config.get('gcode.show_toolpath'))
        self.highlight_current_line.setChecked(config.get('gcode.highlight_current_line'))
        self.animation_speed.setValue(int(config.get('gcode.animation_speed') * 10))

        self.bed_leveling_points.setValue(config.get('calibration.bed_leveling_points'))
        probe_offset = config.get('calibration.probe_offset')
        self.probe_offset_x.setValue(probe_offset['x'])
        self.probe_offset_y.setValue(probe_offset['y'])
        self.probe_offset_z.setValue(probe_offset['z'])
        self.z_probe_speed.setValue(config.get('calibration.z_probe_speed'))

    def _save_settings(self):
        config = self.config_manager

        config.set('printer.build_volume.x', self.build_volume_x.value())
        config.set('printer.build_volume.y', self.build_volume_y.value())
        config.set('printer.build_volume.z', self.build_volume_z.value())

        config.set('printer.max_feedrate.x', self.max_feedrate_x.value())
        config.set('printer.max_feedrate.y', self.max_feedrate_y.value())
        config.set('printer.max_feedrate.z', self.max_feedrate_z.value())
        config.set('printer.max_feedrate.e', self.max_feedrate_e.value())

        config.set('printer.default_temperatures.extruder', self.default_extruder_temp.value())
        config.set('printer.default_temperatures.bed', self.default_bed_temp.value())

        config.set('serial.port', self.serial_port.currentText())
        config.set('serial.baudrate', int(self.serial_baudrate.currentText()))
        config.set('serial.timeout', self.serial_timeout.value())
        config.set('serial.auto_connect', self.auto_connect.isChecked())

        config.set('ui.theme', self.theme_combo.currentText())
        config.set('ui.language', self.language_combo.currentText())
        config.set('ui.show_grid', self.show_grid.isChecked())
        config.set('ui.show_axes', self.show_axes.isChecked())
        config.set('ui.show_build_plate', self.show_build_plate.isChecked())
        config.set('ui.lighting_enabled', self.lighting_enabled.isChecked())
        config.set('ui.smooth_movement', self.smooth_movement.isChecked())
        config.set('ui.visualization_quality', self.visualization_quality.currentText())
        config.set('ui.auto_scroll_console', self.auto_scroll_console.isChecked())
        config.set('ui.console_max_lines', self.console_max_lines.value())

        config.set('gcode.auto_load_preview', self.auto_load_preview.isChecked())
        config.set('gcode.show_toolpath', self.show_toolpath.isChecked())
        config.set('gcode.highlight_current_line', self.highlight_current_line.isChecked())
        config.set('gcode.animation_speed', self.animation_speed.value() / 10.0)

        config.set('calibration.bed_leveling_points', self.bed_leveling_points.value())
        config.set('calibration.probe_offset.x', self.probe_offset_x.value())
        config.set('calibration.probe_offset.y', self.probe_offset_y.value())
        config.set('calibration.probe_offset.z', self.probe_offset_z.value())
        config.set('calibration.z_probe_speed', self.z_probe_speed.value())

    def _apply_settings(self):
        self._save_settings()

    def _restore_defaults(self):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Восстановление настроек",
            "Восстановить настройки по умолчанию?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.config_data = self.config_manager._get_default_config()
            self._load_settings()

    def accept(self):
        self._save_settings()
        super().accept()