from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtSignal


class BaseWidget(QWidget):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self._setup_config_connections()

    def _setup_config_connections(self):
        if self.config_manager:
            self.config_manager.config_changed.connect(self._on_config_changed)

    def _on_config_changed(self, path, value):
        pass

    def get_config(self, path, default=None):
        if self.config_manager:
            return self.config_manager.get(path, default)
        return default

    def set_config(self, path, value):
        if self.config_manager:
            self.config_manager.set(path, value)