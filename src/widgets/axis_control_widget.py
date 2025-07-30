from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSpinBox, QDoubleSpinBox, QGroupBox, QGridLayout)
from PyQt6.QtCore import pyqtSignal


class AxisControlWidget(QWidget):
    position_changed = pyqtSignal(float, float, float)

    def __init__(self, gcode_handler):
        super().__init__()
        self.gcode_handler = gcode_handler
        self.current_pos = [0.0, 0.0, 0.0]
        self.step_sizes = [0.1, 1.0, 10.0, 50.0]
        self.current_step_index = 1
        self.current_feedrate = 3000
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self._create_step_group())
        layout.addWidget(self._create_position_group())
        layout.addWidget(self._create_control_group())
        layout.addWidget(self._create_feedrate_group())
        layout.addWidget(self._create_manual_group())
        layout.addWidget(self._create_home_group())
        self.setLayout(layout)

    def _create_step_group(self):
        group = QGroupBox("Размер шага")
        layout = QHBoxLayout()

        self.step_buttons = []
        for i, step in enumerate(self.step_sizes):
            btn = QPushButton(f"{step} мм")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self.set_step_size(idx))
            self.step_buttons.append(btn)
            layout.addWidget(btn)

        self.step_buttons[self.current_step_index].setChecked(True)
        group.setLayout(layout)
        return group

    def _create_position_group(self):
        group = QGroupBox("Текущая позиция")
        layout = QGridLayout()

        self.x_pos_label = QLabel("0.00")
        self.y_pos_label = QLabel("0.00")
        self.z_pos_label = QLabel("0.00")

        layout.addWidget(QLabel("X:"), 0, 0)
        layout.addWidget(self.x_pos_label, 0, 1)
        layout.addWidget(QLabel("мм"), 0, 2)
        layout.addWidget(QLabel("Y:"), 1, 0)
        layout.addWidget(self.y_pos_label, 1, 1)
        layout.addWidget(QLabel("мм"), 1, 2)
        layout.addWidget(QLabel("Z:"), 2, 0)
        layout.addWidget(self.z_pos_label, 2, 1)
        layout.addWidget(QLabel("мм"), 2, 2)

        group.setLayout(layout)
        return group

    def _create_control_group(self):
        group = QGroupBox("Управление осями")
        layout = QGridLayout()

        self.x_minus_btn = QPushButton("X-")
        self.x_plus_btn = QPushButton("X+")
        self.y_minus_btn = QPushButton("Y-")
        self.y_plus_btn = QPushButton("Y+")
        self.z_minus_btn = QPushButton("Z-")
        self.z_plus_btn = QPushButton("Z+")
        self.home_btn = QPushButton("HOME")

        layout.addWidget(self.y_plus_btn, 0, 1)
        layout.addWidget(self.x_minus_btn, 1, 0)
        layout.addWidget(self.home_btn, 1, 1)
        layout.addWidget(self.x_plus_btn, 1, 2)
        layout.addWidget(self.y_minus_btn, 2, 1)
        layout.addWidget(self.z_plus_btn, 0, 3)
        layout.addWidget(self.z_minus_btn, 2, 3)

        group.setLayout(layout)
        return group

    def _create_feedrate_group(self):
        group = QGroupBox("Скорость перемещения")
        layout = QHBoxLayout()

        self.feedrate_spinbox = QSpinBox()
        self.feedrate_spinbox.setRange(1, 60000)
        self.feedrate_spinbox.setValue(self.current_feedrate)
        self.feedrate_spinbox.setSuffix(" мм/мин")

        layout.addWidget(self.feedrate_spinbox)
        group.setLayout(layout)
        return group

    def _create_manual_group(self):
        group = QGroupBox("Ручное позиционирование")
        layout = QGridLayout()

        self.x_input = QDoubleSpinBox()
        self.x_input.setRange(-1000, 1000)
        self.x_input.setDecimals(2)
        self.x_input.setSuffix(" мм")

        self.y_input = QDoubleSpinBox()
        self.y_input.setRange(-1000, 1000)
        self.y_input.setDecimals(2)
        self.y_input.setSuffix(" мм")

        self.z_input = QDoubleSpinBox()
        self.z_input.setRange(0, 500)
        self.z_input.setDecimals(2)
        self.z_input.setSuffix(" мм")

        self.move_btn = QPushButton("Переместить")
        self.move_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")

        layout.addWidget(QLabel("X:"), 0, 0)
        layout.addWidget(self.x_input, 0, 1)
        layout.addWidget(QLabel("Y:"), 1, 0)
        layout.addWidget(self.y_input, 1, 1)
        layout.addWidget(QLabel("Z:"), 2, 0)
        layout.addWidget(self.z_input, 2, 1)
        layout.addWidget(self.move_btn, 3, 0, 1, 2)

        group.setLayout(layout)
        return group

    def _create_home_group(self):
        group = QGroupBox("Калибровка осей")
        layout = QGridLayout()

        self.home_all_btn = QPushButton("HOME Все")
        self.home_x_btn = QPushButton("HOME X")
        self.home_y_btn = QPushButton("HOME Y")
        self.home_z_btn = QPushButton("HOME Z")
        self.disable_steppers_btn = QPushButton("Отключить моторы")
        self.enable_steppers_btn = QPushButton("Включить моторы")

        layout.addWidget(self.home_all_btn, 0, 0, 1, 2)
        layout.addWidget(self.home_x_btn, 1, 0)
        layout.addWidget(self.home_y_btn, 1, 1)
        layout.addWidget(self.home_z_btn, 2, 0)
        layout.addWidget(self.disable_steppers_btn, 3, 0)
        layout.addWidget(self.enable_steppers_btn, 3, 1)

        group.setLayout(layout)
        return group

    def connect_signals(self):
        self.x_minus_btn.clicked.connect(lambda: self.move_axis('X', -self.get_current_step()))
        self.x_plus_btn.clicked.connect(lambda: self.move_axis('X', self.get_current_step()))
        self.y_minus_btn.clicked.connect(lambda: self.move_axis('Y', -self.get_current_step()))
        self.y_plus_btn.clicked.connect(lambda: self.move_axis('Y', self.get_current_step()))
        self.z_minus_btn.clicked.connect(lambda: self.move_axis('Z', -self.get_current_step()))
        self.z_plus_btn.clicked.connect(lambda: self.move_axis('Z', self.get_current_step()))

        self.move_btn.clicked.connect(self.move_to_position)
        self.home_btn.clicked.connect(self.home_all)

        self.home_all_btn.clicked.connect(self.home_all)
        self.home_x_btn.clicked.connect(lambda: self.home_axis('X'))
        self.home_y_btn.clicked.connect(lambda: self.home_axis('Y'))
        self.home_z_btn.clicked.connect(lambda: self.home_axis('Z'))

        self.disable_steppers_btn.clicked.connect(self.disable_steppers)
        self.enable_steppers_btn.clicked.connect(self.enable_steppers)
        self.feedrate_spinbox.valueChanged.connect(self.set_feedrate)

    def set_step_size(self, index):
        for i, btn in enumerate(self.step_buttons):
            btn.setChecked(i == index)
        self.current_step_index = index

    def get_current_step(self):
        return self.step_sizes[self.current_step_index]

    def set_feedrate(self, value):
        self.current_feedrate = value

    def move_axis(self, axis, distance):
        if axis == 'X':
            self.current_pos[0] += distance
        elif axis == 'Y':
            self.current_pos[1] += distance
        elif axis == 'Z':
            self.current_pos[2] += distance

        self.gcode_handler.move_relative(axis, distance, self.current_feedrate)
        self.update_position_display()
        self.position_changed.emit(self.current_pos[0], self.current_pos[1], self.current_pos[2])

    def move_to_position(self):
        x = self.x_input.value()
        y = self.y_input.value()
        z = self.z_input.value()

        self.current_pos = [x, y, z]
        self.gcode_handler.move_to_position(x, y, z, self.current_feedrate)
        self.update_position_display()
        self.position_changed.emit(x, y, z)

    def home_all(self):
        self.gcode_handler.home_all()
        self.current_pos = [0.0, 0.0, 0.0]
        self.update_position_display()
        self.position_changed.emit(0, 0, 0)

    def home_axis(self, axis):
        self.gcode_handler.home_axis(axis)
        if axis == 'X':
            self.current_pos[0] = 0.0
        elif axis == 'Y':
            self.current_pos[1] = 0.0
        elif axis == 'Z':
            self.current_pos[2] = 0.0
        self.update_position_display()
        self.position_changed.emit(self.current_pos[0], self.current_pos[1], self.current_pos[2])

    def disable_steppers(self):
        self.gcode_handler._send_command("M84")

    def enable_steppers(self):
        self.gcode_handler._send_command("M17")

    def update_position_display(self):
        self.x_pos_label.setText(f"{self.current_pos[0]:.2f}")
        self.y_pos_label.setText(f"{self.current_pos[1]:.2f}")
        self.z_pos_label.setText(f"{self.current_pos[2]:.2f}")

        self.x_input.setValue(self.current_pos[0])
        self.y_input.setValue(self.current_pos[1])
        self.z_input.setValue(self.current_pos[2])

    def update_position_from_3d(self, x, y, z):
        self.current_pos = [x, y, z]
        self.update_position_display()