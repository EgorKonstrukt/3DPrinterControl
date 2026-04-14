from PyQt5.QtWidgets import QMessageBox, QAction
from PyQt5.QtGui import QKeySequence


class MenuManager:
    def __init__(self, main_window, localization_manager):
        self.main_window = main_window
        self.localization_manager = localization_manager

    def create_menus(self):
        menubar = self.main_window.menuBar()

        self._create_file_menu(menubar)
        self._create_view_menu(menubar)
        self._create_tools_menu(menubar)
        self._create_help_menu(menubar)

    def _create_file_menu(self, menubar):
        file_menu = menubar.addMenu(self.localization_manager.tr("file_menu"))

        load_gcode_action = QAction(self.localization_manager.tr("file_load_gcode"), self.main_window)
        load_gcode_action.setShortcut(QKeySequence.StandardKey.Open)
        load_gcode_action.triggered.connect(self.main_window.load_gcode_file)
        file_menu.addAction(load_gcode_action)

        save_settings_action = QAction(self.localization_manager.tr("file_save_settings"), self.main_window)
        save_settings_action.setShortcut(QKeySequence.StandardKey.Save)
        save_settings_action.triggered.connect(self.main_window.save_settings)
        file_menu.addAction(save_settings_action)

        file_menu.addSeparator()

        exit_action = QAction(self.localization_manager.tr("file_exit"), self.main_window)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.main_window.close)
        file_menu.addAction(exit_action)

    def _create_view_menu(self, menubar):
        view_menu = menubar.addMenu(self.localization_manager.tr("view_menu"))

        view_menu.addAction(self.main_window.printer_control_dock.toggleViewAction())
        view_menu.addAction(self.main_window.gcode_dock.toggleViewAction())
        view_menu.addAction(self.main_window.console_dock.toggleViewAction())

        view_menu.addSeparator()

        fullscreen_action = QAction(self.localization_manager.tr("view_fullscreen"), self.main_window)
        fullscreen_action.setShortcut(QKeySequence.StandardKey.FullScreen)
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self.main_window.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        reset_layout_action = QAction(self.localization_manager.tr("view_reset_layout"), self.main_window)
        reset_layout_action.triggered.connect(self.main_window.reset_layout)
        view_menu.addAction(reset_layout_action)

        theme_menu = view_menu.addMenu(self.localization_manager.tr("view_theme"))
        self._create_theme_menu(theme_menu)

    def _create_theme_menu(self, theme_menu):
        dark_theme_action = QAction(self.localization_manager.tr("theme_menu_dark"), self.main_window)
        dark_theme_action.setCheckable(False)
        # dark_theme_action.setChecked(True)
        dark_theme_action.triggered.connect(lambda: self._change_theme("dark"))
        theme_menu.addAction(dark_theme_action)

        light_theme_action = QAction(self.localization_manager.tr("theme_menu_light"), self.main_window)
        light_theme_action.setCheckable(False)
        light_theme_action.triggered.connect(lambda: self._change_theme("light"))
        theme_menu.addAction(light_theme_action)

    def _create_tools_menu(self, menubar):
        tools_menu = menubar.addMenu(self.localization_manager.tr("tools_menu_tools"))

        calibration_action = QAction(self.localization_manager.tr("tools_menu_calibration"), self.main_window)
        calibration_action.setShortcut("Ctrl+K")
        calibration_action.triggered.connect(self.main_window.open_calibration)
        tools_menu.addAction(calibration_action)

        macros_action = QAction(self.localization_manager.tr("tools_menu_macros"), self.main_window)
        macros_action.setShortcut("Ctrl+M")
        macros_action.triggered.connect(self.main_window.open_macros)
        tools_menu.addAction(macros_action)

        emergency_stop_action = QAction(self.localization_manager.tr("tools_menu_emergency"), self.main_window)
        emergency_stop_action.setShortcut("Ctrl+E")
        emergency_stop_action.triggered.connect(self.main_window.emergency_stop)
        tools_menu.addAction(emergency_stop_action)

        tools_menu.addSeparator()

        settings_action = QAction(self.localization_manager.tr("tools_menu_settings"), self.main_window)
        settings_action.triggered.connect(self.main_window.open_settings)
        tools_menu.addAction(settings_action)

    def _create_help_menu(self, menubar):
        help_menu = menubar.addMenu(self.localization_manager.tr("help_menu_help"))

        about_action = QAction(self.localization_manager.tr("help_menu_about"), self.main_window)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        shortcuts_action = QAction(self.localization_manager.tr("help_menu_hotkeys"), self.main_window)
        shortcuts_action.triggered.connect(self._show_shortcuts)
        help_menu.addAction(shortcuts_action)

    def _change_theme(self, theme_name):
        self.main_window.config_manager.set('ui.theme', theme_name)

    def _show_about(self):
        QMessageBox.about(
            self.main_window,
            "О программе",
            "3D Printer Control\n\n от LayDigital"
            "Продвинутое программное обеспечение для управления 3D-принтером\n"
            "с улучшенной 3D-визуализацией, расширенными функциями управления\n"
            "и пользовательским интерфейсом.\n\n"
            "Особенности:\n"
            "• 3D-визуализация в реальном времени\n"
            "• Управление курсором по 3D-сцене\n"
            "• Пошаговая калибровка\n"
        )

    def _show_shortcuts(self):
        QMessageBox.information(
            self.main_window,
            "Горячие клавиши",
            "Ctrl+O - Загрузить G-код файл\n"
            "Ctrl+S - Сохранить настройки\n"
            "Ctrl+Q - Выход\n"
            "Ctrl+K - Калибровка\n"
            "Ctrl+E - Аварийная остановка\n"
            "F11 - Полноэкранный режим\n\n"
            "3D-визуализация:\n"
            "ПКМ + перетаскивание - Поворот камеры\n"
            "СКМ + перетаскивание - Перемещение камеры\n"
            "Колесо мыши - Масштабирование\n"
            "Ctrl+ЛКМ - Переместить головку в точку"
        )