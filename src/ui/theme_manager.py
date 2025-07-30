import os
from PyQt6.QtWidgets import QApplication


class ThemeManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.themes_path = os.path.join(os.path.dirname(__file__), "..", "styles")

    def apply_theme(self, theme_name):
        style_path = os.path.join(self.themes_path, f"{theme_name}.qss")

        if os.path.exists(style_path):
            try:
                with open(style_path, 'r', encoding='utf-8') as f:
                    stylesheet = f.read()
                QApplication.instance().setStyleSheet(stylesheet)
                return True
            except Exception as e:
                print(f"Error loading theme {theme_name}: {e}")
                return False
        else:
            self._create_default_themes()
            return self.apply_theme(theme_name)

    def _create_default_themes(self):
        os.makedirs(self.themes_path, exist_ok=True)

        dark_theme = """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }

        QDockWidget {
            background-color: #353535;
            color: #ffffff;
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }

        QDockWidget::title {
            background-color: #404040;
            padding: 3px;
            border: 1px solid #555555;
        }

        QMenuBar {
            background-color: #353535;
            color: #ffffff;
            border-bottom: 1px solid #555555;
        }

        QMenuBar::item:selected {
            background-color: #4a4a4a;
        }

        QMenu {
            background-color: #353535;
            color: #ffffff;
            border: 1px solid #555555;
        }

        QMenu::item:selected {
            background-color: #4a4a4a;
        }

        QToolBar {
            background-color: #404040;
            border: 1px solid #555555;
            spacing: 2px;
        }

        QStatusBar {
            background-color: #353535;
            color: #ffffff;
            border-top: 1px solid #555555;
        }

        QPushButton {
            background-color: #4a4a4a;
            color: #ffffff;
            border: 1px solid #666666;
            padding: 5px;
            border-radius: 3px;
        }

        QPushButton:hover {
            background-color: #5a5a5a;
        }

        QPushButton:pressed {
            background-color: #3a3a3a;
        }

        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #4a4a4a;
            color: #ffffff;
            border: 1px solid #666666;
            padding: 3px;
            border-radius: 2px;
        }

        QTextEdit, QPlainTextEdit {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
        }

        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #353535;
        }

        QTabBar::tab {
            background-color: #404040;
            color: #ffffff;
            padding: 5px 10px;
            border: 1px solid #555555;
            border-bottom: none;
        }

        QTabBar::tab:selected {
            background-color: #353535;
        }

        QGroupBox {
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }

        QCheckBox {
            color: #ffffff;
        }

        QCheckBox::indicator {
            width: 13px;
            height: 13px;
        }

        QCheckBox::indicator:unchecked {
            background-color: #4a4a4a;
            border: 1px solid #666666;
        }

        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 1px solid #0078d4;
        }

        QSlider::groove:horizontal {
            border: 1px solid #555555;
            height: 8px;
            background: #4a4a4a;
            border-radius: 4px;
        }

        QSlider::handle:horizontal {
            background: #0078d4;
            border: 1px solid #0078d4;
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }
        """

        light_theme = """
        QMainWindow {
            background-color: #f0f0f0;
            color: #000000;
        }

        QDockWidget {
            background-color: #ffffff;
            color: #000000;
        }

        QDockWidget::title {
            background-color: #e0e0e0;
            padding: 3px;
            border: 1px solid #c0c0c0;
        }

        QMenuBar {
            background-color: #f0f0f0;
            color: #000000;
            border-bottom: 1px solid #c0c0c0;
        }

        QMenuBar::item:selected {
            background-color: #e0e0e0;
        }

        QMenu {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #c0c0c0;
        }

        QMenu::item:selected {
            background-color: #e0e0e0;
        }

        QToolBar {
            background-color: #f0f0f0;
            border: 1px solid #c0c0c0;
        }

        QStatusBar {
            background-color: #f0f0f0;
            color: #000000;
            border-top: 1px solid #c0c0c0;
        }

        QPushButton {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #c0c0c0;
            padding: 5px;
            border-radius: 3px;
        }

        QPushButton:hover {
            background-color: #f0f0f0;
        }

        QPushButton:pressed {
            background-color: #e0e0e0;
        }

        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #c0c0c0;
            padding: 3px;
            border-radius: 2px;
        }

        QTextEdit, QPlainTextEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #c0c0c0;
        }

        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: #ffffff;
        }

        QTabBar::tab {
            background-color: #f0f0f0;
            color: #000000;
            padding: 5px 10px;
            border: 1px solid #c0c0c0;
            border-bottom: none;
        }

        QTabBar::tab:selected {
            background-color: #ffffff;
        }

        QGroupBox {
            color: #000000;
            border: 1px solid #c0c0c0;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }

        QCheckBox {
            color: #000000;
        }

        QSlider::groove:horizontal {
            border: 1px solid #c0c0c0;
            height: 8px;
            background: #f0f0f0;
            border-radius: 4px;
        }

        QSlider::handle:horizontal {
            background: #0078d4;
            border: 1px solid #0078d4;
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }
        """

        try:
            with open(os.path.join(self.themes_path, "dark.qss"), 'w', encoding='utf-8') as f:
                f.write(dark_theme)

            with open(os.path.join(self.themes_path, "light.qss"), 'w', encoding='utf-8') as f:
                f.write(light_theme)
        except Exception as e:
            print(f"Error creating default themes: {e}")