from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QGroupBox, QGridLayout)
from PyQt6.QtCore import pyqtSignal


class ConnectionWidget(QWidget):
    connection_changed = pyqtSignal(bool)

    def __init__(self, gcode_handler):
        super().__init__()
        self.gcode_handler = gcode_handler
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self._create_connection_group())
        layout.addWidget(self._create_emergency_group())
        layout.addStretch()
        self.setLayout(layout)

    def _create_connection_group(self):
        group = QGroupBox("Подключение к принтеру")
        layout = QGridLayout()

        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)

        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["115200", "250000", "500000", "1000000"])
        self.baudrate_combo.setCurrentText("115200")

        self.refresh_ports_btn = QPushButton("Обновить порты")
        self.connect_btn = QPushButton("Подключить")
        self.disconnect_btn = QPushButton("Отключить")
        self.disconnect_btn.setEnabled(False)

        self.connection_status = QLabel("Не подключен")
        self.connection_status.setStyleSheet("QLabel { color: red; font-weight: bold; }")

        layout.addWidget(QLabel("Порт:"), 0, 0)
        layout.addWidget(self.port_combo, 0, 1)
        layout.addWidget(self.refresh_ports_btn, 0, 2)
        layout.addWidget(QLabel("Скорость:"), 1, 0)
        layout.addWidget(self.baudrate_combo, 1, 1)
        layout.addWidget(QLabel("Статус:"), 2, 0)
        layout.addWidget(self.connection_status, 2, 1)
        layout.addWidget(self.connect_btn, 3, 0)
        layout.addWidget(self.disconnect_btn, 3, 1)

        group.setLayout(layout)
        return group

    def _create_emergency_group(self):
        group = QGroupBox("Аварийные команды")
        layout = QHBoxLayout()

        self.emergency_stop_btn = QPushButton("АВАРИЙНАЯ ОСТАНОВКА")
        self.emergency_stop_btn.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; font-weight: bold; font-size: 14px; }"
        )

        self.reset_btn = QPushButton("Сброс")
        self.pause_btn = QPushButton("Пауза")

        layout.addWidget(self.emergency_stop_btn)
        layout.addWidget(self.reset_btn)
        layout.addWidget(self.pause_btn)

        group.setLayout(layout)
        return group

    def connect_signals(self):
        self.refresh_ports_btn.clicked.connect(self.refresh_ports)
        self.connect_btn.clicked.connect(self.connect_printer)
        self.disconnect_btn.clicked.connect(self.disconnect_printer)
        self.emergency_stop_btn.clicked.connect(self.emergency_stop)
        self.reset_btn.clicked.connect(self.reset_printer)
        self.pause_btn.clicked.connect(self.pause_print)

    def refresh_ports(self):
        self.port_combo.clear()
        if hasattr(self.gcode_handler, 'serial_comm') and self.gcode_handler.serial_comm:
            ports = self.gcode_handler.serial_comm.list_available_ports()
            self.port_combo.addItems(ports)

    def connect_printer(self):
        port = self.port_combo.currentText()
        baudrate = int(self.baudrate_combo.currentText())
        if port and hasattr(self.gcode_handler, 'serial_comm'):
            if self.gcode_handler.serial_comm.connect(port, baudrate):
                self._update_connection_state(True)
                self.connection_changed.emit(True)

    def disconnect_printer(self):
        if hasattr(self.gcode_handler, 'serial_comm'):
            self.gcode_handler.serial_comm.disconnect()
            self._update_connection_state(False)
            self.connection_changed.emit(False)

    def _update_connection_state(self, connected):
        self.connect_btn.setEnabled(not connected)
        self.disconnect_btn.setEnabled(connected)

        if connected:
            self.connection_status.setText("Подключен")
            self.connection_status.setStyleSheet("QLabel { color: green; font-weight: bold; }")
        else:
            self.connection_status.setText("Не подключен")
            self.connection_status.setStyleSheet("QLabel { color: red; font-weight: bold; }")

    def emergency_stop(self):
        self.gcode_handler._send_command("M112")

    def reset_printer(self):
        self.gcode_handler._send_command("M999")

    def pause_print(self):
        self.gcode_handler._send_command("M25")