import json
import os
from typing import Any, Dict
from PyQt6.QtCore import QObject, pyqtSignal


class ConfigManager(QObject):
    config_changed = pyqtSignal(str, object)

    def __init__(self):
        super().__init__()
        self.config_file = "config.json"
        self.layout_file = "layout.dat"
        self.config_data = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "printer": {
                "build_volume": {"x": 220, "y": 220, "z": 250},
                "max_feedrate": {"x": 500, "y": 500, "z": 5, "e": 25},
                "max_acceleration": {"x": 3000, "y": 3000, "z": 100, "e": 10000},
                "default_temperatures": {"extruder": 200, "bed": 60}
            },
            "serial": {
                "port": "AUTO",
                "baudrate": 115200,
                "timeout": 1.0,
                "auto_connect": False
            },
            "ui": {
                "theme": "dark",
                "language": "ru",
                "show_grid": True,
                "show_axes": True,
                "show_build_plate": True,
                "show_layers": True,
                "lighting_enabled": True,
                "smooth_movement": True,
                "auto_scroll_console": True,
                "console_max_lines": 1000,
                "visualization_quality": "high"
            },
            "gcode": {
                "auto_load_preview": True,
                "show_toolpath": True,
                "animation_speed": 1.0,
                "highlight_current_line": True
            },
            "calibration": {
                "bed_leveling_points": 9,
                "probe_offset": {"x": 0, "y": 0, "z": -1.5},
                "z_probe_speed": 5
            }
        }

    def load_config(self) -> bool:
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self._merge_config(loaded_config)
                return True
        except Exception as e:
            print(f"Error loading config: {e}")
        return False

    def save_config(self) -> bool:
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def _merge_config(self, loaded_config: Dict[str, Any]):
        def merge_dict(default: Dict, loaded: Dict) -> Dict:
            for key, value in loaded.items():
                if key in default:
                    if isinstance(default[key], dict) and isinstance(value, dict):
                        default[key] = merge_dict(default[key], value)
                    else:
                        default[key] = value
            return default

        self.config_data = merge_dict(self.config_data, loaded_config)

    def get(self, path: str, default=None):
        try:
            keys = path.split('.')
            value = self.config_data
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, path: str, value: Any):
        keys = path.split('.')
        config = self.config_data

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value
        self.config_changed.emit(path, value)

    def get_section(self, section: str) -> Dict[str, Any]:
        return self.config_data.get(section, {})

    def save_layout(self, geometry: bytes, state: bytes) -> bool:
        try:
            layout_data = {
                'geometry': geometry.hex(),
                'state': state.hex()
            }
            with open(self.layout_file, 'w', encoding='utf-8') as f:
                json.dump(layout_data, f)
            return True
        except Exception as e:
            print(f"Error saving layout: {e}")
            return False

    def load_layout(self) -> tuple:
        try:
            if os.path.exists(self.layout_file):
                with open(self.layout_file, 'r', encoding='utf-8') as f:
                    layout_data = json.load(f)
                    geometry = bytes.fromhex(layout_data['geometry'])
                    state = bytes.fromhex(layout_data['state'])
                    return geometry, state
        except Exception as e:
            print(f"Error loading layout: {e}")
        return None, None