from PyQt6.QtWidgets import QStatusBar, QLabel

class StatusManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.main_window.setStatusBar(self.status_bar)

        self.connection_label = QLabel("Не подключен")
        self.connection_label.setStyleSheet("color: red; font-weight: bold;")
        self.status_bar.addWidget(self.connection_label)

        self.status_bar.addPermanentWidget(QLabel("|"))

        self.position_label = QLabel("X: 0.00 Y: 0.00 Z: 0.00")
        self.status_bar.addPermanentWidget(self.position_label)

        self.status_bar.addPermanentWidget(QLabel("|"))

        self.temperature_label = QLabel("E: 0°C B: 0°C")
        self.status_bar.addPermanentWidget(self.temperature_label)

        self.status_bar.showMessage("Готов к работе")

    def update_status(self):
        pass

    def update_position_display(self, x, y, z):
        self.position_label.setText(f"X: {x:.2f} Y: {y:.2f} Z: {z:.2f}")

    def update_temperature_display(self, heater, current, target):
        if heater == 'extruder':
            current_text = self.temperature_label.text()
            parts = current_text.split(' B: ')
            bed_temp = parts[1] if len(parts) > 1 else "0°C"
            self.temperature_label.setText(f"E: {current:.0f}°C B: {bed_temp}")
        elif heater == 'bed':
            current_text = self.temperature_label.text()
            parts = current_text.split(' B: ')
            extruder_temp = parts[0].replace('E: ', '') if len(parts) > 0 else "0°C"
            self.temperature_label.setText(f"E: {extruder_temp} B: {current:.0f}°C")

    def update_print_status(self, status):
        status_messages = {
            'printing': 'Печать...',
            'paused': 'Пауза',
            'finished': 'Печать завершена',
            'stopped': 'Печать остановлена'
        }
        message = status_messages.get(status, status)
        self.status_bar.showMessage(message)

    def update_connection_status(self, connected):
        if connected:
            self.connection_label.setText("Подключен")
            self.connection_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.connection_label.setText("Не подключен")
            self.connection_label.setStyleSheet("color: red; font-weight: bold;")

    def show_message(self, message):
        self.status_bar.showMessage(message)