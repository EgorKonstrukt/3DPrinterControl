from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QAction

class ToolbarManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def create_toolbar(self):
        toolbar = QToolBar("Основная панель", self.main_window)
        toolbar.setMovable(True)
        toolbar.setFloatable(True)
        self.main_window.addToolBar(toolbar)

        self._add_connection_actions(toolbar)
        toolbar.addSeparator()
        self._add_control_actions(toolbar)
        toolbar.addSeparator()
        self._add_gcode_actions(toolbar)

    def _add_connection_actions(self, toolbar):
        connect_action = QAction("Подключить", self.main_window)
        connect_action.triggered.connect(self.main_window.quick_connect)
        toolbar.addAction(connect_action)

        disconnect_action = QAction("Отключить", self.main_window)
        disconnect_action.triggered.connect(self.main_window.quick_disconnect)
        toolbar.addAction(disconnect_action)

    def _add_control_actions(self, toolbar):
        home_action = QAction("HOME", self.main_window)
        home_action.triggered.connect(self.main_window.quick_home)
        toolbar.addAction(home_action)

        emergency_action = QAction("СТОП", self.main_window)
        emergency_action.triggered.connect(self.main_window.emergency_stop)
        toolbar.addAction(emergency_action)

    def _add_gcode_actions(self, toolbar):
        load_gcode_action = QAction("Загрузить G-код", self.main_window)
        load_gcode_action.triggered.connect(self.main_window.load_gcode_file)
        toolbar.addAction(load_gcode_action)

        start_print_action = QAction("Начать печать", self.main_window)
        start_print_action.triggered.connect(self.main_window.start_print)
        toolbar.addAction(start_print_action)