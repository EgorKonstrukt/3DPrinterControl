import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QGridLayout, QTextEdit, QProgressBar, 
                             QWizard, QWizardPage, QCheckBox, QSlider, QFrame,
                             QTabWidget, QWidget, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPen, QColor

class CalibrationStep(QWizardPage):
    def __init__(self, title, description, gcode_handler):
        super().__init__()
        self.gcode_handler = gcode_handler
        self.setTitle(title)
        self.setSubTitle(description)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

class HomeCalibrationStep(CalibrationStep):
    def __init__(self, gcode_handler):
        super().__init__(
            "Калибровка Home позиций",
            "Настройка начальных позиций осей принтера",
            gcode_handler
        )
    
    def init_ui(self):
        super().init_ui()
        layout = self.layout()
        
        info_label = QLabel(
            "Этот шаг поможет настроить правильные позиции Home для всех осей.\n"
            "Убедитесь, что принтер подключен и готов к работе."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        controls_group = QGroupBox("Управление")
        controls_layout = QGridLayout()
        
        self.home_all_btn = QPushButton("HOME Все оси")
        self.home_x_btn = QPushButton("HOME X")
        self.home_y_btn = QPushButton("HOME Y")
        self.home_z_btn = QPushButton("HOME Z")
        
        self.test_move_btn = QPushButton("Тестовое движение")
        self.check_endstops_btn = QPushButton("Проверить концевики")
        
        controls_layout.addWidget(self.home_all_btn, 0, 0, 1, 2)
        controls_layout.addWidget(self.home_x_btn, 1, 0)
        controls_layout.addWidget(self.home_y_btn, 1, 1)
        controls_layout.addWidget(self.home_z_btn, 2, 0)
        controls_layout.addWidget(self.test_move_btn, 3, 0)
        controls_layout.addWidget(self.check_endstops_btn, 3, 1)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        status_group = QGroupBox("Статус")
        status_layout = QVBoxLayout()
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        
        status_layout.addWidget(self.status_text)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        self.connect_signals()
    
    def connect_signals(self):
        self.home_all_btn.clicked.connect(self.home_all)
        self.home_x_btn.clicked.connect(lambda: self.home_axis('X'))
        self.home_y_btn.clicked.connect(lambda: self.home_axis('Y'))
        self.home_z_btn.clicked.connect(lambda: self.home_axis('Z'))
        self.test_move_btn.clicked.connect(self.test_movement)
        self.check_endstops_btn.clicked.connect(self.check_endstops)
    
    def home_all(self):
        self.status_text.append("Выполняется HOME всех осей...")
        self.gcode_handler.home_all()
        self.status_text.append("HOME завершен.")
    
    def home_axis(self, axis):
        self.status_text.append(f"Выполняется HOME оси {axis}...")
        self.gcode_handler.home_axis(axis)
        self.status_text.append(f"HOME оси {axis} завершен.")
    
    def test_movement(self):
        self.status_text.append("Выполняется тестовое движение...")
        self.gcode_handler.move_to_position(10, 10, 10)
        self.status_text.append("Тестовое движение завершено.")
    
    def check_endstops(self):
        self.status_text.append("Проверка состояния концевиков...")
        self.gcode_handler.send_command("M119")
        self.status_text.append("Команда отправлена. Проверьте консоль для результатов.")

class BedLevelingStep(CalibrationStep):
    def __init__(self, gcode_handler):
        super().__init__(
            "Калибровка стола",
            "Выравнивание стола принтера для качественной печати",
            gcode_handler
        )
        self.calibration_points = [
            (20, 20, 0),    # Передний левый
            (200, 20, 0),   # Передний правый
            (200, 200, 0),  # Задний правый
            (20, 200, 0),   # Задний левый
            (110, 110, 0)   # Центр
        ]
        self.current_point = 0
    
    def init_ui(self):
        super().init_ui()
        layout = self.layout()
        
        info_label = QLabel(
            "Калибровка стола выполняется в 5 точках.\n"
            "Используйте лист бумаги для проверки зазора между соплом и столом."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        points_group = QGroupBox("Точки калибровки")
        points_layout = QVBoxLayout()
        
        self.current_point_label = QLabel("Текущая точка: 1/5 (Передний левый)")
        self.current_point_label.setStyleSheet("QLabel { font-weight: bold; font-size: 14px; }")
        points_layout.addWidget(self.current_point_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 5)
        self.progress_bar.setValue(0)
        points_layout.addWidget(self.progress_bar)
        
        points_group.setLayout(points_layout)
        layout.addWidget(points_group)
        
        controls_group = QGroupBox("Управление")
        controls_layout = QGridLayout()
        
        self.move_to_point_btn = QPushButton("Переместить к точке")
        self.next_point_btn = QPushButton("Следующая точка")
        self.prev_point_btn = QPushButton("Предыдущая точка")
        self.auto_level_btn = QPushButton("Автоуровень (G29)")
        
        self.z_up_btn = QPushButton("Z +0.1")
        self.z_down_btn = QPushButton("Z -0.1")
        self.z_up_fine_btn = QPushButton("Z +0.02")
        self.z_down_fine_btn = QPushButton("Z -0.02")
        
        controls_layout.addWidget(self.move_to_point_btn, 0, 0, 1, 2)
        controls_layout.addWidget(self.prev_point_btn, 1, 0)
        controls_layout.addWidget(self.next_point_btn, 1, 1)
        controls_layout.addWidget(self.auto_level_btn, 2, 0, 1, 2)
        
        controls_layout.addWidget(QLabel("Точная настройка Z:"), 3, 0, 1, 2)
        controls_layout.addWidget(self.z_up_btn, 4, 0)
        controls_layout.addWidget(self.z_down_btn, 4, 1)
        controls_layout.addWidget(self.z_up_fine_btn, 5, 0)
        controls_layout.addWidget(self.z_down_fine_btn, 5, 1)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        instructions_group = QGroupBox("Инструкции")
        instructions_layout = QVBoxLayout()
        
        instructions_text = QTextEdit()
        instructions_text.setMaximumHeight(120)
        instructions_text.setReadOnly(True)
        instructions_text.setText(
            "1. Нажмите 'Переместить к точке' для перехода к текущей точке\n"
            "2. Поместите лист бумаги между соплом и столом\n"
            "3. Используйте кнопки Z для настройки высоты\n"
            "4. Лист должен двигаться с небольшим сопротивлением\n"
            "5. Нажмите 'Следующая точка' для перехода к следующей позиции"
        )
        
        instructions_layout.addWidget(instructions_text)
        instructions_group.setLayout(instructions_layout)
        layout.addWidget(instructions_group)
        
        self.connect_signals()
    
    def connect_signals(self):
        self.move_to_point_btn.clicked.connect(self.move_to_current_point)
        self.next_point_btn.clicked.connect(self.next_point)
        self.prev_point_btn.clicked.connect(self.prev_point)
        self.auto_level_btn.clicked.connect(self.auto_level)
        
        self.z_up_btn.clicked.connect(lambda: self.adjust_z(0.1))
        self.z_down_btn.clicked.connect(lambda: self.adjust_z(-0.1))
        self.z_up_fine_btn.clicked.connect(lambda: self.adjust_z(0.02))
        self.z_down_fine_btn.clicked.connect(lambda: self.adjust_z(-0.02))
    
    def move_to_current_point(self):
        point = self.calibration_points[self.current_point]
        self.gcode_handler.move_to_position(point[0], point[1], 5)
        self.gcode_handler.move_to_position(point[0], point[1], point[2])
    
    def next_point(self):
        if self.current_point < len(self.calibration_points) - 1:
            self.current_point += 1
            self.update_point_display()
    
    def prev_point(self):
        if self.current_point > 0:
            self.current_point -= 1
            self.update_point_display()
    
    def update_point_display(self):
        point_names = ["Передний левый", "Передний правый", "Задний правый", "Задний левый", "Центр"]
        self.current_point_label.setText(f"Текущая точка: {self.current_point + 1}/5 ({point_names[self.current_point]})")
        self.progress_bar.setValue(self.current_point + 1)
    
    def adjust_z(self, offset):
        self.gcode_handler.move_relative('Z', offset, 300)
    
    def auto_level(self):
        reply = QMessageBox.question(
            self, 
            "Автоуровень", 
            "Запустить автоматическое выравнивание стола?\nЭто может занять несколько минут.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.gcode_handler.send_command("G29")

class ExtruderCalibrationStep(CalibrationStep):
    def __init__(self, gcode_handler):
        super().__init__(
            "Калибровка экструдера",
            "Настройка шагов экструдера для точной подачи филамента",
            gcode_handler
        )
    
    def init_ui(self):
        super().init_ui()
        layout = self.layout()
        
        info_label = QLabel(
            "Калибровка экструдера позволяет настроить точное количество подаваемого филамента.\n"
            "Для этого потребуется измерить реальную длину поданного филамента."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        preparation_group = QGroupBox("Подготовка")
        preparation_layout = QVBoxLayout()
        
        self.heat_extruder_btn = QPushButton("Нагреть экструдер до 200°C")
        self.mark_filament_btn = QPushButton("Отметить филамент на 120мм от экструдера")
        
        preparation_layout.addWidget(self.heat_extruder_btn)
        preparation_layout.addWidget(self.mark_filament_btn)
        
        preparation_group.setLayout(preparation_layout)
        layout.addWidget(preparation_group)
        
        test_group = QGroupBox("Тестовая экструзия")
        test_layout = QGridLayout()
        
        self.extrude_length = QSpinBox()
        self.extrude_length.setRange(50, 200)
        self.extrude_length.setValue(100)
        self.extrude_length.setSuffix(" мм")
        
        self.extrude_speed = QSpinBox()
        self.extrude_speed.setRange(50, 500)
        self.extrude_speed.setValue(100)
        self.extrude_speed.setSuffix(" мм/мин")
        
        self.extrude_btn = QPushButton("Выполнить экструзию")
        
        test_layout.addWidget(QLabel("Длина:"), 0, 0)
        test_layout.addWidget(self.extrude_length, 0, 1)
        test_layout.addWidget(QLabel("Скорость:"), 1, 0)
        test_layout.addWidget(self.extrude_speed, 1, 1)
        test_layout.addWidget(self.extrude_btn, 2, 0, 1, 2)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        measurement_group = QGroupBox("Измерение и расчет")
        measurement_layout = QGridLayout()
        
        self.actual_length = QDoubleSpinBox()
        self.actual_length.setRange(0.0, 200.0)
        self.actual_length.setDecimals(1)
        self.actual_length.setSuffix(" мм")
        
        self.current_steps = QSpinBox()
        self.current_steps.setRange(1, 2000)
        self.current_steps.setValue(93)
        self.current_steps.setSuffix(" шагов/мм")
        
        self.new_steps_label = QLabel("0 шагов/мм")
        self.calculate_btn = QPushButton("Рассчитать новые шаги")
        self.apply_steps_btn = QPushButton("Применить новые шаги")
        
        measurement_layout.addWidget(QLabel("Фактическая длина:"), 0, 0)
        measurement_layout.addWidget(self.actual_length, 0, 1)
        measurement_layout.addWidget(QLabel("Текущие шаги:"), 1, 0)
        measurement_layout.addWidget(self.current_steps, 1, 1)
        measurement_layout.addWidget(QLabel("Новые шаги:"), 2, 0)
        measurement_layout.addWidget(self.new_steps_label, 2, 1)
        measurement_layout.addWidget(self.calculate_btn, 3, 0)
        measurement_layout.addWidget(self.apply_steps_btn, 3, 1)
        
        measurement_group.setLayout(measurement_layout)
        layout.addWidget(measurement_group)
        
        self.connect_signals()
    
    def connect_signals(self):
        self.heat_extruder_btn.clicked.connect(self.heat_extruder)
        self.extrude_btn.clicked.connect(self.perform_extrusion)
        self.calculate_btn.clicked.connect(self.calculate_new_steps)
        self.apply_steps_btn.clicked.connect(self.apply_new_steps)
    
    def heat_extruder(self):
        self.gcode_handler.send_command("M104 S200")
        self.heat_extruder_btn.setText("Нагрев... Ожидайте")
        self.heat_extruder_btn.setEnabled(False)
        
        QTimer.singleShot(30000, self.enable_heat_button)
    
    def enable_heat_button(self):
        self.heat_extruder_btn.setText("Нагреть экструдер до 200°C")
        self.heat_extruder_btn.setEnabled(True)
    
    def perform_extrusion(self):
        length = self.extrude_length.value()
        speed = self.extrude_speed.value()
        
        self.gcode_handler.send_command("G91")
        self.gcode_handler.send_command(f"G1 E{length} F{speed}")
        self.gcode_handler.send_command("G90")
    
    def calculate_new_steps(self):
        requested = self.extrude_length.value()
        actual = self.actual_length.value()
        current_steps = self.current_steps.value()
        
        if actual > 0:
            new_steps = (requested / actual) * current_steps
            self.new_steps_label.setText(f"{new_steps:.1f} шагов/мм")
            self.new_steps = new_steps
        else:
            QMessageBox.warning(self, "Ошибка", "Введите фактическую длину больше 0")
    
    def apply_new_steps(self):
        if hasattr(self, 'new_steps'):
            self.gcode_handler.send_command(f"M92 E{self.new_steps:.1f}")
            self.gcode_handler.send_command("M500")
            QMessageBox.information(self, "Успех", "Новые шаги применены и сохранены в EEPROM")

class CalibrationWizard(QWizard):
    def __init__(self, gcode_handler, parent=None):
        super().__init__(parent)
        self.gcode_handler = gcode_handler
        self.setWindowTitle("Мастер калибровки принтера")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(600, 500)
        
        self.addPage(HomeCalibrationStep(gcode_handler))
        self.addPage(BedLevelingStep(gcode_handler))
        self.addPage(ExtruderCalibrationStep(gcode_handler))
        
        self.setButtonText(QWizard.WizardButton.NextButton, "Далее")
        self.setButtonText(QWizard.WizardButton.BackButton, "Назад")
        self.setButtonText(QWizard.WizardButton.FinishButton, "Завершить")
        self.setButtonText(QWizard.WizardButton.CancelButton, "Отмена")

class CalibrationDialog(QDialog):
    def __init__(self, gcode_handler, parent=None):
        super().__init__(parent)
        self.gcode_handler = gcode_handler
        self.setWindowTitle("Калибровка принтера")
        self.setMinimumSize(400, 300)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("Калибровка 3D-принтера")
        title_label.setStyleSheet("QLabel { font-size: 18px; font-weight: bold; }")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        description_label = QLabel(
            "Выберите тип калибровки для вашего принтера.\n"
            "Рекомендуется выполнять калибровку в указанном порядке."
        )
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description_label)
        
        buttons_layout = QVBoxLayout()
        
        self.wizard_btn = QPushButton("Полная калибровка (Мастер)")
        self.wizard_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        
        self.home_btn = QPushButton("Калибровка Home позиций")
        self.bed_btn = QPushButton("Калибровка стола")
        self.extruder_btn = QPushButton("Калибровка экструдера")
        self.pid_btn = QPushButton("PID калибровка")
        
        buttons_layout.addWidget(self.wizard_btn)
        buttons_layout.addWidget(self.home_btn)
        buttons_layout.addWidget(self.bed_btn)
        buttons_layout.addWidget(self.extruder_btn)
        buttons_layout.addWidget(self.pid_btn)
        
        layout.addLayout(buttons_layout)
        
        close_btn = QPushButton("Закрыть")
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        self.wizard_btn.clicked.connect(self.open_wizard)
        self.home_btn.clicked.connect(self.calibrate_home)
        self.bed_btn.clicked.connect(self.calibrate_bed)
        self.extruder_btn.clicked.connect(self.calibrate_extruder)
        self.pid_btn.clicked.connect(self.calibrate_pid)
        close_btn.clicked.connect(self.accept)
    
    def open_wizard(self):
        wizard = CalibrationWizard(self.gcode_handler, self)
        wizard.exec()
    
    def calibrate_home(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Калибровка Home")
        dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        step = HomeCalibrationStep(self.gcode_handler)
        layout.addWidget(step)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def calibrate_bed(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Калибровка стола")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        step = BedLevelingStep(self.gcode_handler)
        layout.addWidget(step)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def calibrate_extruder(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Калибровка экструдера")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        step = ExtruderCalibrationStep(self.gcode_handler)
        layout.addWidget(step)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def calibrate_pid(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("PID калибровка")
        dialog.setMinimumSize(400, 200)
        
        layout = QVBoxLayout()
        
        info_label = QLabel("PID калибровка настраивает регулятор температуры для стабильного нагрева.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        extruder_btn = QPushButton("Калибровать экструдер (M303 E0 S200 C8)")
        bed_btn = QPushButton("Калибровать стол (M303 E-1 S60 C8)")
        
        extruder_btn.clicked.connect(lambda: self.run_pid_calibration("M303 E0 S200 C8"))
        bed_btn.clicked.connect(lambda: self.run_pid_calibration("M303 E-1 S60 C8"))
        
        layout.addWidget(extruder_btn)
        layout.addWidget(bed_btn)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def run_pid_calibration(self, command):
        reply = QMessageBox.question(
            self, 
            "PID калибровка", 
            f"Запустить PID калибровку?\nКоманда: {command}\nЭто может занять 10-15 минут.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.gcode_handler.send_command(command)
            QMessageBox.information(
                self, 
                "Калибровка запущена", 
                "PID калибровка запущена. Следите за прогрессом в консоли.\n"
                "После завершения используйте M500 для сохранения настроек."
            )

