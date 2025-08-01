import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QDockWidget, QMessageBox, QFileDialog, QApplication,
                             QSplitter)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence

from core.serial_comm import SerialComm
from core.gcode_handler import GCodeHandler
from widgets.visualization_3d import Advanced3DVisualizationWidget
from widgets.printer_control import PrinterControl
from widgets.console import ConsoleWidget
from widgets.gcode_viewer import GCodeViewer
from windows.calibration_dialog import CalibrationDialog
from windows.settings_dialog import SettingsDialog
from windows.macros import MacroDialog
from ui.menu_manager import MenuManager
from ui.toolbar_manager import ToolbarManager
from ui.status_manager import StatusManager
from ui.theme_manager import ThemeManager


class MainWindow(QMainWindow):
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager

        self._init_core_components()
        self._init_ui()
        self._init_managers()
        self._restore_settings()
        self._connect_signals()
        self._start_status_timer()

    def _init_core_components(self):
        """Инициализация основных компонентов"""
        self.serial_comm = SerialComm()
        self.gcode_handler = GCodeHandler(self.serial_comm)

    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("3D Printer Control - Улучшенная версия")
        self.setMinimumSize(1400, 1000)

        self._create_central_widget()
        self._create_dock_widgets()
        self._setup_dock_options()

    def _create_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)

        self.visualization_3d = Advanced3DVisualizationWidget(self.config_manager)
        main_splitter.addWidget(self.visualization_3d)

        main_splitter.setSizes([1000, 400])

    def _create_dock_widgets(self):
        """Создание док-виджетов"""
        self.printer_control_dock = QDockWidget("Управление принтером", self)
        self.printer_control_widget = PrinterControl(self.gcode_handler)
        self.printer_control_dock.setWidget(self.printer_control_widget)
        self._setup_dock_features(self.printer_control_dock)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.printer_control_dock)

        self.gcode_dock = QDockWidget("G-код", self)
        self.gcode_widget = GCodeViewer(self.gcode_handler)
        self.gcode_dock.setWidget(self.gcode_widget)
        self._setup_dock_features(self.gcode_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.gcode_dock)

        self.console_dock = QDockWidget("Консоль", self)
        self.console_widget = ConsoleWidget(self.serial_comm)
        self.console_dock.setWidget(self.console_widget)
        self._setup_dock_features(self.console_dock)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.console_dock)

    def _setup_dock_features(self, dock):
        """Настройка возможностей док-виджета"""
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )

    def _setup_dock_options(self):
        """Настройка опций док-виджетов"""
        self.setDockOptions(
            QMainWindow.DockOption.AllowNestedDocks |
            QMainWindow.DockOption.AllowTabbedDocks |
            QMainWindow.DockOption.AnimatedDocks
        )

    def _init_managers(self):
        """Инициализация менеджеров"""
        self.menu_manager = MenuManager(self)
        self.toolbar_manager = ToolbarManager(self)
        self.status_manager = StatusManager(self)
        self.theme_manager = ThemeManager(self.config_manager)

        self.menu_manager.create_menus()
        self.toolbar_manager.create_toolbar()
        self.status_manager.create_status_bar()

    def _connect_signals(self):
        """Подключение сигналов"""
        self.printer_control_widget.position_changed.connect(
            self.visualization_3d.update_position
        )

        self.visualization_3d.position_clicked.connect(
            self._on_3d_position_clicked
        )

        self.gcode_handler.position_changed.connect(
            self.status_manager.update_position_display
        )
        self.gcode_handler.temperature_changed.connect(
            self.status_manager.update_temperature_display
        )
        self.gcode_handler.print_status_changed.connect(
            self.status_manager.update_print_status
        )

        self.gcode_handler.gcode_loaded.connect(
            self.visualization_3d.load_gcode_path
        )
        self.gcode_handler.position_changed.connect(
            self.visualization_3d.update_position
        )

        self.gcode_widget.layer_selected.connect(
            self.visualization_3d.visualization.set_current_layer
        )

        self.serial_comm.connection_changed.connect(
            self.status_manager.update_connection_status
        )

        self.config_manager.config_changed.connect(self._on_config_changed)

    def _start_status_timer(self):
        """Запуск таймера обновления статуса"""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.status_manager.update_status)
        self.status_timer.start(1000)

    def _on_3d_position_clicked(self, x, y, z):
        """Обработка клика по 3D пространству"""
        if hasattr(self.printer_control_widget, 'update_position_from_3d'):
            self.printer_control_widget.update_position_from_3d(x, y, z)

    def _on_config_changed(self, path, value):
        """Обработка изменения конфигурации"""
        if path.startswith('ui.theme'):
            self.theme_manager.apply_theme(value)

    def load_gcode_file(self):
        """Загрузка G-code файла"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить G-код файл",
            "",
            "G-code Files (*.gcode *.g *.nc);;All Files (*)"
        )
        if filename:
            self.gcode_widget.load_gcode_file(filename)
            self.status_manager.show_message(f"Загружен файл: {os.path.basename(filename)}")

    def start_print(self):
        """Начало печати"""
        if hasattr(self.gcode_widget, 'start_print'):
            self.gcode_widget.start_print()

    def quick_connect(self):
        """Быстрое подключение"""
        if hasattr(self.printer_control_widget, 'connect_printer'):
            self.printer_control_widget.connect_printer()

    def quick_disconnect(self):
        """Быстрое отключение"""
        if hasattr(self.printer_control_widget, 'disconnect_printer'):
            self.printer_control_widget.disconnect_printer()

    def quick_home(self):
        """Быстрый возврат в исходное положение"""
        self.gcode_handler.home_all()
        self.status_manager.show_message("Выполняется HOME всех осей...")

    def emergency_stop(self):
        """Аварийная остановка"""
        self.gcode_handler.send_command("M112")
        self.status_manager.show_message("АВАРИЙНАЯ ОСТАНОВКА!")
        QMessageBox.critical(self, "Аварийная остановка", "Принтер остановлен аварийно!")

    def open_calibration(self):
        """Открытие диалога калибровки"""
        dialog = CalibrationDialog(self.gcode_handler, self.config_manager, self)
        dialog.exec()

    def open_macros(self):
        """Открытие диалога макросов"""
        dialog = MacroDialog(self.gcode_handler, self.config_manager, self)
        dialog.exec()

    def open_settings(self):
        """Открытие настроек"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._apply_settings()

    def toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def reset_layout(self):
        """Сброс расположения окон"""
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.printer_control_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.gcode_dock)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.console_dock)

        for dock in [self.printer_control_dock, self.gcode_dock, self.console_dock]:
            dock.show()

    def reset_3d_view(self):
        """Сброс 3D вида"""
        self.visualization_3d.visualization.reset_camera()
        self.status_manager.show_message("3D вид сброшен")

    def toggle_grid(self):
        """Переключение сетки"""
        self.visualization_3d.visualization.toggle_grid()

    def toggle_axes(self):
        """Переключение осей"""
        self.visualization_3d.visualization.toggle_axes()

    def toggle_build_plate(self):
        """Переключение платформы"""
        self.visualization_3d.visualization.toggle_build_plate()

    def toggle_lighting(self):
        """Переключение освещения"""
        self.visualization_3d.visualization.toggle_lighting()

    def clear_trail(self):
        """Очистка следа печатной головки"""
        self.visualization_3d.clear_trail()
        self.status_manager.show_message("След печатной головки очищен")

    def _apply_settings(self):
        """Применение настроек"""
        theme = self.config_manager.get('ui.theme', 'dark')
        self.theme_manager.apply_theme(theme)

        build_volume = self.config_manager.get('printer.build_volume')
        if build_volume:
            self.visualization_3d.visualization.set_build_volume(
                build_volume.get('x', 220),
                build_volume.get('y', 220),
                build_volume.get('z', 250)
            )

    def _restore_settings(self):
        """Восстановление настроек"""
        geometry, state = self.config_manager.load_layout()
        if geometry and state:
            self.restoreGeometry(geometry)
            self.restoreState(state)

        self._apply_settings()

    def save_settings(self):
        """Сохранение настроек"""
        self.config_manager.save_layout(self.saveGeometry(), self.saveState())
        self.config_manager.save_config()
        self.status_manager.show_message("Настройки сохранены")

    def show_about(self):
        """Показать информацию о программе"""
        QMessageBox.about(
            self,
            "О программе",
            """
            <h3>3D Printer Control - Улучшенная версия</h3>
            <p>Полноценное управление 3D принтером с улучшенной визуализацией G-code</p>
            <p><b>Управление камерой:</b></p>
            <ul>
                <li>Правая кнопка мыши - вращение</li>
                <li>Средняя кнопка мыши - панорамирование</li>
                <li>Колесо мыши - масштабирование</li>
                <li>Ctrl + левая кнопка - установка позиции</li>
            </ul>
            """
        )

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.save_settings()

        if self.serial_comm.is_connected:
            reply = QMessageBox.question(
                self,
                "Подтверждение выхода",
                "Принтер подключен. Отключить и выйти?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.serial_comm.disconnect()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

