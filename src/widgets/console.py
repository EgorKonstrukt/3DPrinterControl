import sys
import re
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTextEdit, QLineEdit, QComboBox, QCheckBox, 
                             QGroupBox, QSplitter, QTabWidget, QLabel,
                             QSpinBox, QFileDialog, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat, QPalette

class AdvancedConsole(QWidget):
    command_sent = pyqtSignal(str)
    
    def __init__(self, serial_comm):
        super().__init__()
        self.serial_comm = serial_comm
        self.command_history = []
        self.history_index = -1
        self.auto_scroll = True
        self.max_lines = 1000
        self.log_to_file = False
        self.log_file = None
        
        self.init_ui()
        self.setup_timer()
        
        if self.serial_comm:
            self.serial_comm.data_received.connect(self.add_response)
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        console_widget = self.create_console_widget()
        controls_widget = self.create_controls_widget()
        
        splitter.addWidget(console_widget)
        splitter.addWidget(controls_widget)
        splitter.setSizes([400, 200])
        
        self.setLayout(layout)
    
    def create_console_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        header_layout = QHBoxLayout()
        
        self.connection_status = QLabel("Не подключен")
        self.connection_status.setStyleSheet("QLabel { color: red; font-weight: bold; }")
        
        self.clear_btn = QPushButton("Очистить")
        self.save_log_btn = QPushButton("Сохранить лог")
        self.auto_scroll_checkbox = QCheckBox("Автопрокрутка")
        self.auto_scroll_checkbox.setChecked(True)
        
        header_layout.addWidget(QLabel("Статус:"))
        header_layout.addWidget(self.connection_status)
        header_layout.addStretch()
        header_layout.addWidget(self.auto_scroll_checkbox)
        header_layout.addWidget(self.clear_btn)
        header_layout.addWidget(self.save_log_btn)
        
        layout.addLayout(header_layout)
        
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setFont(QFont("Consolas", 10))
        self.console_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #3399ff;
            }
        """)
        
        layout.addWidget(self.console_text)
        
        input_layout = QHBoxLayout()
        
        self.command_input = QLineEdit()
        self.command_input.setFont(QFont("Consolas", 10))
        self.command_input.setPlaceholderText("Введите G-код команду...")
        
        self.send_btn = QPushButton("Отправить")
        self.send_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        
        input_layout.addWidget(QLabel("Команда:"))
        input_layout.addWidget(self.command_input)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        widget.setLayout(layout)
        
        self.connect_console_signals()
        return widget
    
    def create_controls_widget(self):
        widget = QWidget()
        layout = QHBoxLayout()
        
        quick_commands_group = QGroupBox("Быстрые команды")
        quick_layout = QVBoxLayout()
        
        commands_row1 = QHBoxLayout()
        self.m105_btn = QPushButton("M105 (Температура)")
        self.m114_btn = QPushButton("M114 (Позиция)")
        self.m119_btn = QPushButton("M119 (Концевики)")
        self.m500_btn = QPushButton("M500 (Save to EEPROM)")
        self.m500_btn.setStyleSheet("QPushButton { background-color: #32a834; color: white; font-weight: bold; font-size: 14px; }")
        
        commands_row1.addWidget(self.m105_btn)
        commands_row1.addWidget(self.m114_btn)
        commands_row1.addWidget(self.m119_btn)
        commands_row1.addWidget(self.m500_btn)
        
        commands_row2 = QHBoxLayout()
        self.g28_btn = QPushButton("G28 (Home)")
        self.m84_btn = QPushButton("M84 (Отключить моторы)")
        self.m112_btn = QPushButton("M112 (Аварийная остановка)")
        self.m112_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        
        commands_row2.addWidget(self.g28_btn)
        commands_row2.addWidget(self.m84_btn)
        commands_row2.addWidget(self.m112_btn)
        
        quick_layout.addLayout(commands_row1)
        quick_layout.addLayout(commands_row2)
        quick_commands_group.setLayout(quick_layout)
        
        settings_group = QGroupBox("Настройки")
        settings_layout = QVBoxLayout()
        
        self.log_checkbox = QCheckBox("Логирование в файл")
        self.timestamp_checkbox = QCheckBox("Временные метки")
        self.timestamp_checkbox.setChecked(True)
        
        max_lines_layout = QHBoxLayout()
        max_lines_layout.addWidget(QLabel("Макс. строк:"))
        self.max_lines_spinbox = QSpinBox()
        self.max_lines_spinbox.setRange(100, 10000)
        self.max_lines_spinbox.setValue(1000)
        max_lines_layout.addWidget(self.max_lines_spinbox)
        
        settings_layout.addWidget(self.log_checkbox)
        settings_layout.addWidget(self.timestamp_checkbox)
        settings_layout.addLayout(max_lines_layout)
        
        settings_group.setLayout(settings_layout)
        
        filter_group = QGroupBox("Фильтры")
        filter_layout = QVBoxLayout()
        
        self.filter_ok_checkbox = QCheckBox("Скрыть 'ok'")
        self.filter_temp_checkbox = QCheckBox("Скрыть температуру")
        self.filter_pos_checkbox = QCheckBox("Скрыть позицию")
        
        filter_layout.addWidget(self.filter_ok_checkbox)
        filter_layout.addWidget(self.filter_temp_checkbox)
        filter_layout.addWidget(self.filter_pos_checkbox)
        
        filter_group.setLayout(filter_layout)
        
        layout.addWidget(quick_commands_group)
        layout.addWidget(settings_group)
        layout.addWidget(filter_group)
        
        widget.setLayout(layout)
        
        self.connect_control_signals()
        return widget
    
    def connect_console_signals(self):
        self.send_btn.clicked.connect(self.send_command)
        self.command_input.returnPressed.connect(self.send_command)
        self.command_input.keyPressEvent = self.handle_key_press
        
        self.clear_btn.clicked.connect(self.clear_console)
        self.save_log_btn.clicked.connect(self.save_log)
        self.auto_scroll_checkbox.toggled.connect(self.toggle_auto_scroll)
    
    def connect_control_signals(self):
        self.m105_btn.clicked.connect(lambda: self.send_quick_command("M105"))
        self.m114_btn.clicked.connect(lambda: self.send_quick_command("M114"))
        self.m119_btn.clicked.connect(lambda: self.send_quick_command("M119"))
        self.g28_btn.clicked.connect(lambda: self.send_quick_command("G28"))
        self.m84_btn.clicked.connect(lambda: self.send_quick_command("M84"))
        self.m112_btn.clicked.connect(lambda: self.send_quick_command("M112"))
        self.m500_btn.clicked.connect(lambda: self.send_quick_command("M500"))
        
        self.log_checkbox.toggled.connect(self.toggle_logging)
        self.max_lines_spinbox.valueChanged.connect(self.update_max_lines)
    
    def handle_key_press(self, event):
        if event.key() == Qt.Key.Key_Up:
            self.navigate_history(-1)
        elif event.key() == Qt.Key.Key_Down:
            self.navigate_history(1)
        else:
            QLineEdit.keyPressEvent(self.command_input, event)
    
    def navigate_history(self, direction):
        if not self.command_history:
            return
        
        self.history_index += direction
        
        if self.history_index < 0:
            self.history_index = 0
        elif self.history_index >= len(self.command_history):
            self.history_index = len(self.command_history) - 1
        
        if 0 <= self.history_index < len(self.command_history):
            self.command_input.setText(self.command_history[self.history_index])
    
    def setup_timer(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_console)
        self.update_timer.start(100)
    
    def send_command(self):
        command = self.command_input.text().strip()
        if not command:
            return
        
        if command not in self.command_history:
            self.command_history.append(command)
            if len(self.command_history) > 50:
                self.command_history.pop(0)
        
        self.history_index = len(self.command_history)
        
        if self.serial_comm and self.serial_comm.send_command(command):
            self.add_command(command)
            self.command_sent.emit(command)
        else:
            self.add_error("Не удалось отправить команду: принтер не подключен")
        
        self.command_input.clear()
    
    def send_quick_command(self, command):
        self.command_input.setText(command)
        self.send_command()
    
    def add_command(self, command):
        timestamp = datetime.now().strftime("%H:%M:%S") if self.timestamp_checkbox.isChecked() else ""
        
        cursor = self.console_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        format = QTextCharFormat()
        format.setForeground(QColor("#00ff00"))
        cursor.setCharFormat(format)
        
        text = f"[{timestamp}] > {command}\n" if timestamp else f"> {command}\n"
        cursor.insertText(text)
        
        self.log_to_file_if_enabled(text)
        self.limit_console_lines()
        
        if self.auto_scroll:
            self.console_text.ensureCursorVisible()
    
    def add_response(self, response):
        if self.should_filter_response(response):
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S") if self.timestamp_checkbox.isChecked() else ""
        
        cursor = self.console_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        format = QTextCharFormat()
        if "error" in response.lower():
            format.setForeground(QColor("#ff4444"))
        elif "ok" in response.lower():
            format.setForeground(QColor("#44ff44"))
        elif re.search(r'T:\d+', response):
            format.setForeground(QColor("#ffaa00"))
        else:
            format.setForeground(QColor("#ffffff"))
        
        cursor.setCharFormat(format)
        
        text = f"[{timestamp}] < {response}\n" if timestamp else f"< {response}\n"
        cursor.insertText(text)
        
        self.log_to_file_if_enabled(text)
        self.limit_console_lines()
        
        if self.auto_scroll:
            self.console_text.ensureCursorVisible()
    
    def add_error(self, error_message):
        timestamp = datetime.now().strftime("%H:%M:%S") if self.timestamp_checkbox.isChecked() else ""
        
        cursor = self.console_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        format = QTextCharFormat()
        format.setForeground(QColor("#ff0000"))
        cursor.setCharFormat(format)
        
        text = f"[{timestamp}] ERROR: {error_message}\n" if timestamp else f"ERROR: {error_message}\n"
        cursor.insertText(text)
        
        self.log_to_file_if_enabled(text)
        self.limit_console_lines()
        
        if self.auto_scroll:
            self.console_text.ensureCursorVisible()
    
    def should_filter_response(self, response):
        response_lower = response.lower()
        
        if self.filter_ok_checkbox.isChecked() and response_lower.strip() == "ok":
            return True
        
        if self.filter_temp_checkbox.isChecked() and re.search(r't:\d+', response_lower):
            return True
        
        if self.filter_pos_checkbox.isChecked() and re.search(r'x:\d+', response_lower):
            return True
        
        return False
    
    def limit_console_lines(self):
        document = self.console_text.document()
        if document.blockCount() > self.max_lines:
            cursor = QTextCursor(document)
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor, 
                              document.blockCount() - self.max_lines)
            cursor.removeSelectedText()
    
    def clear_console(self):
        self.console_text.clear()
        self.add_system_message("Консоль очищена")
    
    def add_system_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S") if self.timestamp_checkbox.isChecked() else ""
        
        cursor = self.console_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        format = QTextCharFormat()
        format.setForeground(QColor("#888888"))
        cursor.setCharFormat(format)
        
        text = f"[{timestamp}] SYSTEM: {message}\n" if timestamp else f"SYSTEM: {message}\n"
        cursor.insertText(text)
        
        if self.auto_scroll:
            self.console_text.ensureCursorVisible()
    
    def save_log(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Сохранить лог консоли", 
            f"printer_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.console_text.toPlainText())
                self.add_system_message(f"Лог сохранен в {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить лог: {e}")
    
    def toggle_auto_scroll(self, enabled):
        self.auto_scroll = enabled
    
    def toggle_logging(self, enabled):
        self.log_to_file = enabled
        if enabled and not self.log_file:
            filename = f"printer_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            try:
                self.log_file = open(filename, 'w', encoding='utf-8')
                self.add_system_message(f"Логирование в файл {filename} включено")
            except Exception as e:
                self.log_checkbox.setChecked(False)
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать лог файл: {e}")
        elif not enabled and self.log_file:
            self.log_file.close()
            self.log_file = None
            self.add_system_message("Логирование в файл отключено")
    
    def log_to_file_if_enabled(self, text):
        if self.log_to_file and self.log_file:
            try:
                self.log_file.write(text)
                self.log_file.flush()
            except Exception as e:
                print(f"Ошибка записи в лог файл: {e}")
    
    def update_max_lines(self, value):
        self.max_lines = value
    
    def update_console(self):
        if self.serial_comm:
            if self.serial_comm.is_connected:
                self.connection_status.setText("Подключен")
                self.connection_status.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            else:
                self.connection_status.setText("Не подключен")
                self.connection_status.setStyleSheet("QLabel { color: red; font-weight: bold; }")
    
    def closeEvent(self, event):
        if self.log_file:
            self.log_file.close()
        event.accept()

class ConsoleWidget(QWidget):
    def __init__(self, serial_comm):
        super().__init__()
        self.init_ui(serial_comm)
    
    def init_ui(self, serial_comm):
        layout = QVBoxLayout()
        
        self.console = AdvancedConsole(serial_comm)
        layout.addWidget(self.console)
        
        self.setLayout(layout)
    
    def add_response(self, response):
        self.console.add_response(response)
    
    def add_command(self, command):
        self.console.add_command(command)

