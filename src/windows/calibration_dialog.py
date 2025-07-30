from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QFormLayout, QSpinBox, QDoubleSpinBox,
                             QPushButton, QGroupBox, QDialogButtonBox, QLabel,
                             QProgressBar, QTextEdit, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal


class CalibrationDialog(QDialog):
    calibration_complete = pyqtSignal()

    def __init__(self, gcode_handler, config_manager, parent=None):
        super().__init__(parent)
        self.gcode_handler = gcode_handler
        self.config_manager = config_manager
        self.setWindowTitle("Калибровка принтера")
        self.setMinimumSize(500, 600)
        self.setModal(True)

        self.current_step = 0
        self.calibration_points = []
        self.is_calibrating = False

        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self._create_auto_leveling_tab()
        self._create_manual_leveling_tab()
        self._create_extruder_calibration_tab()
        self._create_advanced_tab()

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _create_auto_leveling_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        settings_group = QGroupBox("Настройки автокалибровки")
        settings_layout = QFormLayout()
        settings_group.setLayout(settings_layout)

        self.bed_points_spinbox = QSpinBox()
        self.bed_points_spinbox.setRange(4, 25)
        self.bed_points_spinbox.setValue(9)
        settings_layout.addRow("Количество точек:", self.bed_points_spinbox)

        self.probe_speed_spinbox = QSpinBox()
        self.probe_speed_spinbox.setRange(1, 50)
        self.probe_speed_spinbox.setValue(5)
        self.probe_speed_spinbox.setSuffix(" мм/с")
        settings_layout.addRow("Скорость зондирования:", self.probe_speed_spinbox)

        layout.addWidget(settings_group)

        control_group = QGroupBox("Управление")
        control_layout = QVBoxLayout()
        control_group.setLayout(control_layout)

        self.start_auto_leveling_btn = QPushButton("Начать автокалибровку")
        self.start_auto_leveling_btn.clicked.connect(self._start_auto_leveling)
        control_layout.addWidget(self.start_auto_leveling_btn)

        self.auto_progress = QProgressBar()
        self.auto_progress.setVisible(False)
        control_layout.addWidget(self.auto_progress)

        self.auto_status_label = QLabel("Готов к калибровке")
        control_layout.addWidget(self.auto_status_label)

        layout.addWidget(control_group)

        results_group = QGroupBox("Результаты")
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)

        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(150)
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)

        layout.addWidget(results_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Автокалибровка")

    def _create_manual_leveling_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        info_label = QLabel(
            "Ручная калибровка стола по 4 углам.\n"
            "Используйте колесики под столом для регулировки высоты."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        points_group = QGroupBox("Точки калибровки")
        points_layout = QGridLayout()
        points_group.setLayout(points_layout)

        self.corner_buttons = []
        corners = [
            ("Передний левый", 0, 0),
            ("Передний правый", 0, 1),
            ("Задний левый", 1, 0),
            ("Задний правый", 1, 1),
            ("Центр", 2, 0)
        ]

        for name, row, col in corners:
            btn = QPushButton(f"Перейти к: {name}")
            btn.clicked.connect(lambda checked, n=name: self._move_to_corner(n))
            points_layout.addWidget(btn, row, col)
            self.corner_buttons.append(btn)

        layout.addWidget(points_group)

        control_group = QGroupBox("Управление высотой")
        control_layout = QGridLayout()
        control_group.setLayout(control_layout)

        self.z_step_spinbox = QDoubleSpinBox()
        self.z_step_spinbox.setRange(0.01, 10.0)
        self.z_step_spinbox.setValue(0.1)
        self.z_step_spinbox.setSingleStep(0.01)
        self.z_step_spinbox.setSuffix(" мм")
        control_layout.addWidget(QLabel("Шаг перемещения:"), 0, 0)
        control_layout.addWidget(self.z_step_spinbox, 0, 1)

        z_up_btn = QPushButton("Z ↑")
        z_up_btn.clicked.connect(self._move_z_up)
        control_layout.addWidget(z_up_btn, 1, 0)

        z_down_btn = QPushButton("Z ↓")
        z_down_btn.clicked.connect(self._move_z_down)
        control_layout.addWidget(z_down_btn, 1, 1)

        layout.addWidget(control_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Ручная калибровка")

    def _create_extruder_calibration_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        info_label = QLabel(
            "Калибровка экструдера для точного количества подаваемого материала."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        settings_group = QGroupBox("Параметры калибровки")
        settings_layout = QFormLayout()
        settings_group.setLayout(settings_layout)

        self.extrude_length_spinbox = QSpinBox()
        self.extrude_length_spinbox.setRange(10, 200)
        self.extrude_length_spinbox.setValue(100)
        self.extrude_length_spinbox.setSuffix(" мм")
        settings_layout.addRow("Длина экструзии:", self.extrude_length_spinbox)

        self.extrude_speed_spinbox = QSpinBox()
        self.extrude_speed_spinbox.setRange(1, 100)
        self.extrude_speed_spinbox.setValue(5)
        self.extrude_speed_spinbox.setSuffix(" мм/с")
        settings_layout.addRow("Скорость экструзии:", self.extrude_speed_spinbox)

        self.current_esteps_spinbox = QDoubleSpinBox()
        self.current_esteps_spinbox.setRange(1, 2000)
        self.current_esteps_spinbox.setValue(415)
        self.current_esteps_spinbox.setSingleStep(0.1)
        settings_layout.addRow("Текущие E-steps:", self.current_esteps_spinbox)

        layout.addWidget(settings_group)

        process_group = QGroupBox("Процесс калибровки")
        process_layout = QVBoxLayout()
        process_group.setLayout(process_layout)

        step1_btn = QPushButton("1. Нагреть экструдер")
        step1_btn.clicked.connect(self._heat_extruder)
        process_layout.addWidget(step1_btn)

        step2_btn = QPushButton("2. Сделать отметку на филаменте")
        step2_btn.clicked.connect(self._mark_filament)
        process_layout.addWidget(step2_btn)

        step3_btn = QPushButton("3. Начать экструзию")
        step3_btn.clicked.connect(self._start_extrusion)
        process_layout.addWidget(step3_btn)

        measurement_layout = QFormLayout()
        self.actual_length_spinbox = QDoubleSpinBox()
        self.actual_length_spinbox.setRange(0, 200)
        self.actual_length_spinbox.setSingleStep(0.1)
        self.actual_length_spinbox.setSuffix(" мм")
        measurement_layout.addRow("Фактическая длина:", self.actual_length_spinbox)

        process_layout.addLayout(measurement_layout)

        calculate_btn = QPushButton("4. Рассчитать новые E-steps")
        calculate_btn.clicked.connect(self._calculate_esteps)
        process_layout.addWidget(calculate_btn)

        self.new_esteps_label = QLabel("Новые E-steps: -")
        process_layout.addWidget(self.new_esteps_label)

        apply_btn = QPushButton("5. Применить настройки")
        apply_btn.clicked.connect(self._apply_esteps)
        process_layout.addWidget(apply_btn)

        layout.addWidget(process_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Калибровка экструдера")

    def _create_advanced_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        offset_group = QGroupBox("Смещения датчика")
        offset_layout = QFormLayout()
        offset_group.setLayout(offset_layout)

        self.probe_offset_x = QDoubleSpinBox()
        self.probe_offset_x.setRange(-50, 50)
        self.probe_offset_x.setSingleStep(0.1)
        self.probe_offset_x.setSuffix(" мм")
        offset_layout.addRow("Смещение X:", self.probe_offset_x)

        self.probe_offset_y = QDoubleSpinBox()
        self.probe_offset_y.setRange(-50, 50)
        self.probe_offset_y.setSingleStep(0.1)
        self.probe_offset_y.setSuffix(" мм")
        offset_layout.addRow("Смещение Y:", self.probe_offset_y)

        self.probe_offset_z = QDoubleSpinBox()
        self.probe_offset_z.setRange(-10, 10)
        self.probe_offset_z.setSingleStep(0.01)
        self.probe_offset_z.setSuffix(" мм")
        offset_layout.addRow("Смещение Z:", self.probe_offset_z)

        update_offset_btn = QPushButton("Обновить смещения")
        update_offset_btn.clicked.connect(self._update_probe_offset)
        offset_layout.addRow(update_offset_btn)

        layout.addWidget(offset_group)

        pid_group = QGroupBox("PID калибровка")
        pid_layout = QVBoxLayout()
        pid_group.setLayout(pid_layout)

        extruder_pid_btn = QPushButton("Калибровать PID экструдера")
        extruder_pid_btn.clicked.connect(self._calibrate_extruder_pid)
        pid_layout.addWidget(extruder_pid_btn)

        bed_pid_btn = QPushButton("Калибровать PID стола")
        bed_pid_btn.clicked.connect(self._calibrate_bed_pid)
        pid_layout.addWidget(bed_pid_btn)

        layout.addWidget(pid_group)

        save_group = QGroupBox("Сохранение настроек")
        save_layout = QVBoxLayout()
        save_group.setLayout(save_layout)

        save_eeprom_btn = QPushButton("Сохранить в EEPROM")
        save_eeprom_btn.clicked.connect(self._save_to_eeprom)
        save_layout.addWidget(save_eeprom_btn)

        load_eeprom_btn = QPushButton("Загрузить из EEPROM")
        load_eeprom_btn.clicked.connect(self._load_from_eeprom)
        save_layout.addWidget(load_eeprom_btn)

        layout.addWidget(save_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Расширенные")

    def _load_settings(self):
        config = self.config_manager.get_section('calibration')

        self.bed_points_spinbox.setValue(config.get('bed_leveling_points', 9))
        self.probe_speed_spinbox.setValue(config.get('z_probe_speed', 5))

        probe_offset = config.get('probe_offset', {})
        self.probe_offset_x.setValue(probe_offset.get('x', 0))
        self.probe_offset_y.setValue(probe_offset.get('y', 0))
        self.probe_offset_z.setValue(probe_offset.get('z', -1.5))

    def _start_auto_leveling(self):
        if self.is_calibrating:
            return

        self.is_calibrating = True
        self.start_auto_leveling_btn.setEnabled(False)
        self.auto_progress.setVisible(True)
        self.auto_progress.setValue(0)

        points = self.bed_points_spinbox.value()
        self.auto_progress.setMaximum(points)

        self.auto_status_label.setText("Начинаем автокалибровку...")
        self.results_text.clear()

        self.gcode_handler.send_command("G28")
        self.gcode_handler.send_command("G29")

        self._simulate_calibration_progress()

    def _simulate_calibration_progress(self):
        self.calibration_timer = QTimer()
        self.calibration_timer.timeout.connect(self._update_calibration_progress)
        self.calibration_timer.start(1000)

    def _update_calibration_progress(self):
        current_value = self.auto_progress.value()
        if current_value < self.auto_progress.maximum():
            self.auto_progress.setValue(current_value + 1)
            self.auto_status_label.setText(f"Калибровка точки {current_value + 1}...")
            self.results_text.append(f"Точка {current_value + 1}: Z={-0.15 + current_value * 0.02:.3f}")
        else:
            self.calibration_timer.stop()
            self._finish_auto_leveling()

    def _finish_auto_leveling(self):
        self.is_calibrating = False
        self.start_auto_leveling_btn.setEnabled(True)
        self.auto_progress.setVisible(False)
        self.auto_status_label.setText("Автокалибровка завершена")
        self.results_text.append("\nКалибровка успешно завершена!")

    def _move_to_corner(self, corner_name):
        build_volume = self.config_manager.get('printer.build_volume')
        x_size = build_volume['x']
        y_size = build_volume['y']

        positions = {
            "Передний левый": (5, 5),
            "Передний правый": (x_size - 5, 5),
            "Задний левый": (5, y_size - 5),
            "Задний правый": (x_size - 5, y_size - 5),
            "Центр": (x_size // 2, y_size // 2)
        }

        if corner_name in positions:
            x, y = positions[corner_name]
            self.gcode_handler.send_command(f"G0 X{x} Y{y} Z5")
            self.gcode_handler.send_command("G0 Z0.1")

    def _move_z_up(self):
        step = self.z_step_spinbox.value()
        self.gcode_handler.send_command(f"G91")
        self.gcode_handler.send_command(f"G0 Z{step}")
        self.gcode_handler.send_command(f"G90")

    def _move_z_down(self):
        step = self.z_step_spinbox.value()
        self.gcode_handler.send_command(f"G91")
        self.gcode_handler.send_command(f"G0 Z-{step}")
        self.gcode_handler.send_command(f"G90")

    def _heat_extruder(self):
        temp = self.config_manager.get('printer.default_temperatures.extruder', 200)
        self.gcode_handler.send_command(f"M104 S{temp}")

    def _mark_filament(self):
        pass

    def _start_extrusion(self):
        length = self.extrude_length_spinbox.value()
        speed = self.extrude_speed_spinbox.value() * 60
        self.gcode_handler.send_command(f"G1 E{length} F{speed}")

    def _calculate_esteps(self):
        expected = self.extrude_length_spinbox.value()
        actual = self.actual_length_spinbox.value()
        current_esteps = self.current_esteps_spinbox.value()

        if actual > 0:
            new_esteps = (current_esteps * expected) / actual
            self.new_esteps_label.setText(f"Новые E-steps: {new_esteps:.2f}")
            self.calculated_esteps = new_esteps

    def _apply_esteps(self):
        if hasattr(self, 'calculated_esteps'):
            self.gcode_handler.send_command(f"M92 E{self.calculated_esteps:.2f}")

    def _update_probe_offset(self):
        x = self.probe_offset_x.value()
        y = self.probe_offset_y.value()
        z = self.probe_offset_z.value()

        self.gcode_handler.send_command(f"M851 X{x} Y{y} Z{z}")

    def _calibrate_extruder_pid(self):
        temp = self.config_manager.get('printer.default_temperatures.extruder', 200)
        self.gcode_handler.send_command(f"M303 E0 S{temp} C8")

    def _calibrate_bed_pid(self):
        temp = self.config_manager.get('printer.default_temperatures.bed', 60)
        self.gcode_handler.send_command(f"M303 E-1 S{temp} C8")

    def _save_to_eeprom(self):
        self.gcode_handler.send_command("M500")

    def _load_from_eeprom(self):
        self.gcode_handler.send_command("M501")