import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from main_window import MainWindow
from core.config_manager import ConfigManager

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("3D Printer Control")
    app.setApplicationVersion("2.2")
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
            app.setStyleSheet(f.read())
    
    window = MainWindow(config_manager)
    window.show()
    
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())

