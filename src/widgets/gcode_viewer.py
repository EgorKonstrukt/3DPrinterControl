import os
import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTextEdit, QProgressBar, QFileDialog,
                             QGroupBox, QGridLayout, QSpinBox, QCheckBox,
                             QTabWidget, QListWidget, QListWidgetItem,
                             QSplitter, QFrame, QSlider)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QMutex
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat


class GCodeAnalyzer:
    def __init__(self):
        self.reset()

    def reset(self):
        self.total_lines = 0
        self.print_time_estimate = 0
        self.filament_length = 0.0
        self.layer_count = 0
        self.max_temp_extruder = 0
        self.max_temp_bed = 0
        self.print_bounds = {
            'min_x': float('inf'), 'max_x': float('-inf'),
            'min_y': float('inf'), 'max_y': float('-inf'),
            'min_z': float('inf'), 'max_z': float('-inf')
        }
        self.layers = []
        self.path_data = []
        self.center_offset = [0.0, 0.0, 0.0]

    def analyze_gcode(self, gcode_lines):
        self.reset()
        self.total_lines = len(gcode_lines)

        current_layer = 0
        current_z = 0
        current_pos = [0, 0, 0, 0]

        for line_num, line in enumerate(gcode_lines):
            line = line.strip()
            if not line or line.startswith(';'):
                continue

            self._analyze_line(line, current_pos)

            if line.startswith('G1') or line.startswith('G0'):
                self._process_movement(line, current_pos)
            elif line.startswith('G1') and 'Z' in line:
                z_match = re.search(r'Z(\d+\.?\d*)', line)
                if z_match:
                    new_z = float(z_match.group(1))
                    if new_z > current_z:
                        current_layer += 1
                        current_z = new_z

        self.layer_count = current_layer

        # Calculate center offset
        if self.print_bounds["min_x"] != float("inf"):
            center_x = (self.print_bounds["min_x"] + self.print_bounds["max_x"]) / 2
            center_y = (self.print_bounds["min_y"] + self.print_bounds["max_y"]) / 2
            center_z = (self.print_bounds["min_z"] + self.print_bounds["max_z"]) / 2
            self.center_offset = [-center_x, -center_y, -center_z]

        # Apply offset to path data
        for i in range(len(self.path_data)):
            self.path_data[i][0] += self.center_offset[0]
            self.path_data[i][1] += self.center_offset[1]
            self.path_data[i][2] += self.center_offset[2]

        return {
            'total_lines': self.total_lines,
            'layer_count': self.layer_count,
            'print_time': self.print_time_estimate,
            'filament_length': self.filament_length,
            'max_temp_extruder': self.max_temp_extruder,
            'max_temp_bed': self.max_temp_bed,
            'bounds': self.print_bounds,
            'path_data': self.path_data
        }

    def _analyze_line(self, line, current_pos):
        if line.startswith('M104') or line.startswith('M109'):
            temp_match = re.search(r'S(\d+)', line)
            if temp_match:
                temp = int(temp_match.group(1))
                self.max_temp_extruder = max(self.max_temp_extruder, temp)

        elif line.startswith('M140') or line.startswith('M190'):
            temp_match = re.search(r'S(\d+)', line)
            if temp_match:
                temp = int(temp_match.group(1))
                self.max_temp_bed = max(self.max_temp_bed, temp)

    def _process_movement(self, line, current_pos):
        x_match = re.search(r'X(-?\d+\.?\d*)', line)
        y_match = re.search(r'Y(-?\d+\.?\d*)', line)
        z_match = re.search(r'Z(-?\d+\.?\d*)', line)
        e_match = re.search(r'E(-?\d+\.?\d*)', line)

        new_pos = current_pos.copy()

        if x_match:
            new_pos[0] = float(x_match.group(1))
            self.print_bounds['min_x'] = min(self.print_bounds['min_x'], new_pos[0])
            self.print_bounds['max_x'] = max(self.print_bounds['max_x'], new_pos[0])

        if y_match:
            new_pos[1] = float(y_match.group(1))
            self.print_bounds['min_y'] = min(self.print_bounds['min_y'], new_pos[1])
            self.print_bounds['max_y'] = max(self.print_bounds['max_y'], new_pos[1])

        if z_match:
            new_pos[2] = float(z_match.group(1))
            self.print_bounds['min_z'] = min(self.print_bounds['min_z'], new_pos[2])
            self.print_bounds['max_z'] = max(self.print_bounds['max_z'], new_pos[2])

        if e_match:
            new_pos[3] = float(e_match.group(1))
            if new_pos[3] > current_pos[3]:
                self.filament_length += new_pos[3] - current_pos[3]

        self.path_data.append(new_pos.copy())
        current_pos[:] = new_pos


class GCodeViewer(QWidget):
    file_loaded = pyqtSignal(str)
    print_started = pyqtSignal()

    def __init__(self, gcode_handler):
        super().__init__()
        self.gcode_handler = gcode_handler
        self.gcode_commands = []
        self.current_file = ""
        self.analyzer = GCodeAnalyzer()
        self.analysis_data = {}

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        layout = QVBoxLayout()

        file_group = QGroupBox("Файл G-кода")
        file_layout = QHBoxLayout()

        self.load_file_btn = QPushButton("Загрузить файл")
        self.load_file_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")

        self.file_label = QLabel("Файл не загружен")
        self.file_label.setStyleSheet("QLabel { color: #888888; }")

        file_layout.addWidget(self.load_file_btn)
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        tab_widget = QTabWidget()

        preview_tab = self.create_preview_tab()
        tab_widget.addTab(preview_tab, "Предпросмотр")

        analysis_tab = self.create_analysis_tab()
        tab_widget.addTab(analysis_tab, "Анализ")

        control_tab = self.create_control_tab()
        tab_widget.addTab(control_tab, "Управление печатью")

        layout.addWidget(tab_widget)

        self.setLayout(layout)

    def create_preview_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        controls_layout = QHBoxLayout()

        self.line_numbers_checkbox = QCheckBox("Номера строк")
        self.line_numbers_checkbox.setChecked(True)

        self.highlight_moves_checkbox = QCheckBox("Подсветка движений")
        self.highlight_moves_checkbox.setChecked(True)

        self.filter_comments_checkbox = QCheckBox("Скрыть комментарии")

        controls_layout.addWidget(self.line_numbers_checkbox)
        controls_layout.addWidget(self.highlight_moves_checkbox)
        controls_layout.addWidget(self.filter_comments_checkbox)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        self.gcode_text = QTextEdit()
        self.gcode_text.setReadOnly(True)
        self.gcode_text.setFont(QFont("Consolas", 9))
        self.gcode_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #3399ff;
            }
        """)

        layout.addWidget(self.gcode_text)

        navigation_layout = QHBoxLayout()

        self.goto_line_btn = QPushButton("Перейти к строке")
        self.search_btn = QPushButton("Поиск")

        navigation_layout.addWidget(self.goto_line_btn)
        navigation_layout.addWidget(self.search_btn)
        navigation_layout.addStretch()

        layout.addLayout(navigation_layout)

        widget.setLayout(layout)
        return widget

    def create_analysis_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        info_group = QGroupBox("Информация о файле")
        info_layout = QGridLayout()

        self.total_lines_label = QLabel("0")
        self.layer_count_label = QLabel("0")
        self.print_time_label = QLabel("Неизвестно")
        self.filament_length_label = QLabel("0.0 м")

        info_layout.addWidget(QLabel("Всего строк:"), 0, 0)
        info_layout.addWidget(self.total_lines_label, 0, 1)
        info_layout.addWidget(QLabel("Слоев:"), 1, 0)
        info_layout.addWidget(self.layer_count_label, 1, 1)
        info_layout.addWidget(QLabel("Время печати:"), 2, 0)
        info_layout.addWidget(self.print_time_label, 2, 1)
        info_layout.addWidget(QLabel("Длина филамента:"), 3, 0)
        info_layout.addWidget(self.filament_length_label, 3, 1)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        temp_group = QGroupBox("Температуры")
        temp_layout = QGridLayout()

        self.max_extruder_temp_label = QLabel("0°C")
        self.max_bed_temp_label = QLabel("0°C")

        temp_layout.addWidget(QLabel("Макс. экструдер:"), 0, 0)
        temp_layout.addWidget(self.max_extruder_temp_label, 0, 1)
        temp_layout.addWidget(QLabel("Макс. стол:"), 1, 0)
        temp_layout.addWidget(self.max_bed_temp_label, 1, 1)

        temp_group.setLayout(temp_layout)
        layout.addWidget(temp_group)

        bounds_group = QGroupBox("Размеры модели")
        bounds_layout = QGridLayout()

        self.bounds_x_label = QLabel("0.0 мм")
        self.bounds_y_label = QLabel("0.0 мм")
        self.bounds_z_label = QLabel("0.0 мм")

        bounds_layout.addWidget(QLabel("Размер X:"), 0, 0)
        bounds_layout.addWidget(self.bounds_x_label, 0, 1)
        bounds_layout.addWidget(QLabel("Размер Y:"), 1, 0)
        bounds_layout.addWidget(self.bounds_y_label, 1, 1)
        bounds_layout.addWidget(QLabel("Высота Z:"), 2, 0)
        bounds_layout.addWidget(self.bounds_z_label, 2, 1)

        bounds_group.setLayout(bounds_layout)
        layout.addWidget(bounds_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_control_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        print_controls_group = QGroupBox("Управление печатью")
        print_controls_layout = QGridLayout()

        self.start_print_btn = QPushButton("Начать печать")
        self.start_print_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.start_print_btn.setEnabled(False)

        self.pause_print_btn = QPushButton("Пауза")
        self.pause_print_btn.setEnabled(False)

        self.resume_print_btn = QPushButton("Продолжить")
        self.resume_print_btn.setEnabled(False)

        self.stop_print_btn = QPushButton("Остановить")
        self.stop_print_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        self.stop_print_btn.setEnabled(False)

        print_controls_layout.addWidget(self.start_print_btn, 0, 0)
        print_controls_layout.addWidget(self.pause_print_btn, 0, 1)
        print_controls_layout.addWidget(self.resume_print_btn, 1, 0)
        print_controls_layout.addWidget(self.stop_print_btn, 1, 1)

        print_controls_group.setLayout(print_controls_layout)
        layout.addWidget(print_controls_group)

        progress_group = QGroupBox("Прогресс печати")
        progress_layout = QVBoxLayout()

        self.print_progress = QProgressBar()
        self.print_progress.setRange(0, 100)
        self.print_progress.setValue(0)

        self.progress_label = QLabel("Готов к печати")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.print_progress)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        layer_group = QGroupBox("Управление слоями")
        layer_layout = QVBoxLayout()

        self.layer_slider = QSlider(Qt.Orientation.Horizontal)
        self.layer_slider.setRange(0, 0)
        self.layer_slider.setValue(0)

        self.current_layer_label = QLabel("Слой: 0 / 0")

        layer_layout.addWidget(self.current_layer_label)
        layer_layout.addWidget(self.layer_slider)

        layer_group.setLayout(layer_layout)
        layout.addWidget(layer_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def connect_signals(self):
        self.load_file_btn.clicked.connect(self.load_file)

        self.line_numbers_checkbox.toggled.connect(self.update_preview)
        self.highlight_moves_checkbox.toggled.connect(self.update_preview)
        self.filter_comments_checkbox.toggled.connect(self.update_preview)

        self.start_print_btn.clicked.connect(self.start_print)
        self.pause_print_btn.clicked.connect(self.pause_print)
        self.resume_print_btn.clicked.connect(self.resume_print)
        self.stop_print_btn.clicked.connect(self.stop_print)

        self.layer_slider.valueChanged.connect(self.update_layer_display)

        if self.gcode_handler:
            self.gcode_handler.print_progress.connect(self.update_print_progress)
            self.gcode_handler.print_status_changed.connect(self.update_print_status)

    def load_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить G-код файл",
            "",
            "G-code Files (*.gcode *.g);;All Files (*)"
        )

        if filename:
            self.load_gcode_file(filename)

    def load_gcode_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            self.gcode_commands = []
            for i, line in enumerate(lines):
                self.gcode_commands.append({
                    'line_number': i + 1,
                    'original': line.strip(),
                    'command': self.parse_gcode_line(line.strip())
                })

            self.current_file = filename
            self.file_label.setText(f"Загружен: {os.path.basename(filename)}")
            self.file_label.setStyleSheet("QLabel { color: #4CAF50; font-weight: bold; }")

            self.analyze_file()
            self.update_preview()
            self.update_controls()

            self.file_loaded.emit(filename)

        except Exception as e:
            self.file_label.setText(f"Ошибка загрузки: {str(e)}")
            self.file_label.setStyleSheet("QLabel { color: #f44336; font-weight: bold; }")

    def parse_gcode_line(self, line):
        line = line.split(';')[0].strip()
        if not line:
            return None

        parts = line.split()
        if not parts:
            return None

        command = {
            'type': parts[0],
            'parameters': {}
        }

        for part in parts[1:]:
            if len(part) >= 2:
                param = part[0]
                try:
                    value = float(part[1:])
                    command['parameters'][param] = value
                except ValueError:
                    command['parameters'][param] = part[1:]

        return command

    def analyze_file(self):
        if not self.gcode_commands:
            return

        lines = [cmd['original'] for cmd in self.gcode_commands]
        self.analysis_data = self.analyzer.analyze_gcode(lines)

        self.total_lines_label.setText(str(self.analysis_data['total_lines']))
        self.layer_count_label.setText(str(self.analysis_data['layer_count']))
        self.filament_length_label.setText(f"{self.analysis_data['filament_length']:.2f} м")

        self.max_extruder_temp_label.setText(f"{self.analysis_data['max_temp_extruder']}°C")
        self.max_bed_temp_label.setText(f"{self.analysis_data['max_temp_bed']}°C")

        bounds = self.analysis_data['bounds']
        size_x = bounds['max_x'] - bounds['min_x']
        size_y = bounds['max_y'] - bounds['min_y']
        size_z = bounds['max_z'] - bounds['min_z']

        self.bounds_x_label.setText(f"{size_x:.1f} мм")
        self.bounds_y_label.setText(f"{size_y:.1f} мм")
        self.bounds_z_label.setText(f"{size_z:.1f} мм")

        self.layer_slider.setRange(0, max(0, self.analysis_data['layer_count'] - 1))
        self.update_layer_display(0)

    def update_preview(self):
        if not self.gcode_commands:
            return

        self.gcode_text.clear()

        show_line_numbers = self.line_numbers_checkbox.isChecked()
        highlight_moves = self.highlight_moves_checkbox.isChecked()
        filter_comments = self.filter_comments_checkbox.isChecked()

        cursor = self.gcode_text.textCursor()

        for cmd in self.gcode_commands[:1000]:
            line = cmd['original']

            if filter_comments and line.startswith(';'):
                continue

            format = QTextCharFormat()

            if highlight_moves and (line.startswith('G0') or line.startswith('G1')):
                format.setForeground(QColor("#00ff00"))
            elif line.startswith('M'):
                format.setForeground(QColor("#ffaa00"))
            elif line.startswith('G'):
                format.setForeground(QColor("#00aaff"))
            elif line.startswith(';'):
                format.setForeground(QColor("#888888"))
            else:
                format.setForeground(QColor("#ffffff"))

            cursor.setCharFormat(format)

            if show_line_numbers:
                text = f"{cmd['line_number']:4d}: {line}\n"
            else:
                text = f"{line}\n"

            cursor.insertText(text)

        if len(self.gcode_commands) > 1000:
            cursor.insertText(f"\n... и еще {len(self.gcode_commands) - 1000} строк")

    def update_controls(self):
        has_file = bool(self.gcode_commands)
        self.start_print_btn.setEnabled(has_file)

    def start_print(self):
        if self.gcode_commands and self.gcode_handler:
            if self.gcode_handler.start_print(self.gcode_commands):
                self.start_print_btn.setEnabled(False)
                self.pause_print_btn.setEnabled(True)
                self.stop_print_btn.setEnabled(True)
                self.progress_label.setText("Печать...")
                self.print_started.emit()

    def pause_print(self):
        if self.gcode_handler:
            self.gcode_handler.pause_print()
            self.pause_print_btn.setEnabled(False)
            self.resume_print_btn.setEnabled(True)
            self.progress_label.setText("Пауза")

    def resume_print(self):
        if self.gcode_handler:
            self.gcode_handler.resume_print()
            self.pause_print_btn.setEnabled(True)
            self.resume_print_btn.setEnabled(False)
            self.progress_label.setText("Печать...")

    def stop_print(self):
        if self.gcode_handler:
            self.gcode_handler.stop_print()
            self.start_print_btn.setEnabled(True)
            self.pause_print_btn.setEnabled(False)
            self.resume_print_btn.setEnabled(False)
            self.stop_print_btn.setEnabled(False)
            self.progress_label.setText("Остановлено")
            self.print_progress.setValue(0)

    def update_print_progress(self, progress):
        self.print_progress.setValue(progress)
        self.progress_label.setText(f"Печать... {progress}%")

    def update_print_status(self, status):
        status_messages = {
            'printing': 'Печать...',
            'paused': 'Пауза',
            'finished': 'Завершено',
            'stopped': 'Остановлено'
        }

        message = status_messages.get(status, status)
        self.progress_label.setText(message)

        if status == 'finished':
            self.start_print_btn.setEnabled(True)
            self.pause_print_btn.setEnabled(False)
            self.resume_print_btn.setEnabled(False)
            self.stop_print_btn.setEnabled(False)
            self.print_progress.setValue(100)
        elif status == 'stopped':
            self.start_print_btn.setEnabled(True)
            self.pause_print_btn.setEnabled(False)
            self.resume_print_btn.setEnabled(False)
            self.stop_print_btn.setEnabled(False)
            self.print_progress.setValue(0)

    def update_layer_display(self, layer):
        total_layers = self.analysis_data.get('layer_count', 0)
        self.current_layer_label.setText(f"Слой: {layer + 1} / {total_layers}")

    def get_analysis_data(self):
        return self.analysis_data

    def get_path_data(self):
        return self.analysis_data.get('path_data', [])