import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QDockWidget, QMessageBox, QFileDialog, QApplication, QSplitter, QAction
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence

from core.serial_comm import SerialComm
from core.gcode_handler import GCodeHandler
from widgets.visualization_3d import Advanced3DVisualizationWidget
from widgets.temperature_widget import TemperatureWidget
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
from localization.localization_manager import LocalizationManager


class MainWindow(QMainWindow):
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.localization_manager = LocalizationManager(self.config_manager)

        self._init_core_components()
        self._init_ui()
        self._init_managers()
        self._restore_settings()
        self._connect_signals()
        self._start_status_timer()

    def _init_core_components(self):
        self.serial_comm = SerialComm()
        self.gcode_handler = GCodeHandler(self.serial_comm)

    def _init_ui(self):
        self.setWindowTitle(self.localization_manager.tr("app_title"))
        self.setMinimumSize(1400, 1000)

        self._create_central_widget()
        self._create_dock_widgets()
        self._setup_dock_options()

    def _create_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)

        self.visualization_3d = Advanced3DVisualizationWidget(self.config_manager, self.localization_manager)
        main_splitter.addWidget(self.visualization_3d)

        main_splitter.setSizes([1000, 400])

    def _create_dock_widgets(self):
        self.printer_control_dock = QDockWidget(self.localization_manager.tr("printer_control"), self)
        self.printer_control_widget = PrinterControl(gcode_handler=self.gcode_handler,
                                                     localization_manager=self.localization_manager,
                                                     config_manager=self.config_manager)
        self.printer_control_dock.setWidget(self.printer_control_widget)
        self._setup_dock_features(self.printer_control_dock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.printer_control_dock)

        self.temperature_dock = QDockWidget(self.localization_manager.tr("temperature_control"), self)
        self.temperature_widget = TemperatureWidget(gcode_handler=self.gcode_handler,
                                                    config_manager=self.config_manager,
                                                    localization_manager=self.localization_manager)
        self.temperature_dock.setWidget(self.temperature_widget)
        self._setup_dock_features(self.temperature_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.temperature_dock)

        self.gcode_dock = QDockWidget(self.localization_manager.tr("gcode_viewer"), self)
        self.gcode_widget = GCodeViewer(self.gcode_handler)
        self.gcode_dock.setWidget(self.gcode_widget)
        self._setup_dock_features(self.gcode_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.gcode_dock)


        self.console_dock = QDockWidget(self.localization_manager.tr("console"), self)
        self.console_widget = ConsoleWidget(self.serial_comm)
        self.console_dock.setWidget(self.console_widget)
        self._setup_dock_features(self.console_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)


    def _setup_dock_features(self, dock):
            dock.setFeatures(
                QDockWidget.DockWidgetMovable |
                QDockWidget.DockWidgetFloatable |
                QDockWidget.DockWidgetClosable
            )

    def _setup_dock_options(self):
        self.setDockOptions(
            QMainWindow.AllowNestedDocks |
            QMainWindow.AllowTabbedDocks |
            QMainWindow.AnimatedDocks
        )

    def _init_managers(self):
        self.menu_manager = MenuManager(self, localization_manager=self.localization_manager)
        self.toolbar_manager = ToolbarManager(self)
        self.status_manager = StatusManager(self)
        self.theme_manager = ThemeManager(self.config_manager)

        self.menu_manager.create_menus()
        self.toolbar_manager.create_toolbar()
        self.status_manager.create_status_bar()

    def _connect_signals(self):
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
        self.gcode_handler.temperature_changed.connect(
            self.temperature_widget.update_temperatures
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
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.status_manager.update_status)
        self.status_timer.start(1000)

    def _on_3d_position_clicked(self, x, y, z):
        if hasattr(self.printer_control_widget, 'update_position_from_3d'):
            self.printer_control_widget.update_position_from_3d(x, y, z)

    def _on_config_changed(self, path, value):
        if path.startswith('ui.theme'):
            self.theme_manager.apply_theme(value)

    def load_gcode_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.localization_manager.tr("file_load_gcode"),
            "",
            "G-code Files (*.gcode *.g *.nc);;All Files (*)"
        )
        if filename:
            self.gcode_widget.load_gcode_file(filename)
            self.status_manager.show_message(f"{self.localization_manager.tr('message_gcode_loaded')} {os.path.basename(filename)}")

    def start_print(self):
        if hasattr(self.gcode_widget, 'start_print'):
            self.gcode_widget.start_print()

    def quick_connect(self):
        if hasattr(self.printer_control_widget, 'connect_printer'):
            self.printer_control_widget.connect_printer()

    def quick_disconnect(self):
        if hasattr(self.printer_control_widget, 'disconnect_printer'):
            self.printer_control_widget.disconnect_printer()

    def quick_home(self):
        self.gcode_handler.home_all()
        self.status_manager.show_message(self.localization_manager.tr("status_home_all"))

    def emergency_stop(self):
        self.gcode_handler.send_command("M112")
        self.status_manager.show_message(self.localization_manager.tr("status_emergency_stop"))
        QMessageBox.critical(self, self.localization_manager.tr("status_emergency_stop"), self.localization_manager.tr("message_emergency_stop_critical"))

    def open_calibration(self):
        dialog = CalibrationDialog(self.gcode_handler, self.config_manager, self)
        dialog.exec_()

    def open_macros(self):
        dialog = MacroDialog(self.gcode_handler, self.config_manager, self)
        dialog.exec_()

    def open_settings(self):
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec_() == dialog.Accepted:
            self._apply_settings()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def reset_layout(self):
        self.addDockWidget(Qt.LeftDockWidgetArea, self.printer_control_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.gcode_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

        for dock in [self.printer_control_dock, self.gcode_dock, self.console_dock, self.temperature_dock]:
            dock.show()

    def reset_3d_view(self):
        self.visualization_3d.visualization.reset_camera()
        self.status_manager.show_message(self.localization_manager.tr("status_3d_view_reset"))

    def toggle_grid(self):
        self.visualization_3d.visualization.toggle_grid()

    def toggle_axes(self):
        self.visualization_3d.visualization.toggle_axes()

    def toggle_build_plate(self):
        self.visualization_3d.visualization.toggle_build_plate()

    def toggle_lighting(self):
        self.visualization_3d.visualization.toggle_lighting()

    def clear_trail(self):
        self.visualization_3d.clear_trail()
        self.status_manager.show_message(self.localization_manager.tr("view_3d_clear_trail"))

    def _apply_settings(self):
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
        geometry, state = self.config_manager.load_layout()
        if geometry and state:
            self.restoreGeometry(geometry)
            self.restoreState(state)

        self._apply_settings()

    def save_settings(self):
        self.config_manager.save_layout(self.saveGeometry(), self.saveState())
        self.config_manager.save_config()
        self.status_manager.show_message(self.localization_manager.tr("message_settings_saved"))

    def show_about(self):
        QMessageBox.about(
            self,
            self.localization_manager.tr("about_title"),
            self.localization_manager.tr("about_content")
        )

    def closeEvent(self, event):
        self.save_settings()

        if self.serial_comm.is_connected:
            reply = QMessageBox.question(
                self,
                self.localization_manager.tr("message_confirm_exit_connected"),
                self.localization_manager.tr("message_confirm_exit_connected"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.serial_comm.disconnect()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
