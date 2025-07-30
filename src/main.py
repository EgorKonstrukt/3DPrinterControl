#!/usr/bin/env python3

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QIcon
from main_window import MainWindow
from core.config_manager import ConfigManager

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("3D Printer Control")
    app.setApplicationVersion("2.1")
    app.setOrganizationName("LayDigital")
    app.setOrganizationDomain("LayDigital.local")
    
    icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    config_manager = ConfigManager()
    config_manager.load_config()
    
    settings = QSettings()
    style_file = settings.value("style/theme", "dark")
    
    style_path = os.path.join(os.path.dirname(__file__), "..", "styles", f"{style_file}.qss")
    if os.path.exists(style_path):
        with open(style_path, 'r') as f:
            pass
            app.setStyleSheet(f.read())
    
    window = MainWindow(config_manager)
    window.show()
    
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())

