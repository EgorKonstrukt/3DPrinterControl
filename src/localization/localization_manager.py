import json
import os
from PyQt6.QtCore import QObject, pyqtSignal


class LocalizationManager(QObject):
    language_changed = pyqtSignal(str)

    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.current_language = 'ru'
        self.translations = {}
        self.localization_dir = 'localization'

        self.load_language(self.config_manager.get('ui.language', 'ru'))

    def load_language(self, language_code):
        try:
            file_path = os.path.join(self.localization_dir, f'{language_code}.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
                self.current_language = language_code
                self.language_changed.emit(language_code)
                return True
        except Exception as e:
            print(f"Error loading language {language_code}: {e}")
        return False

    def get_text(self, key, default=None):
        return self.translations.get(key, default or key)

    def tr(self, key, default=None):
        return self.get_text(key, default)

    def get_available_languages(self):
        languages = []
        if os.path.exists(self.localization_dir):
            for file in os.listdir(self.localization_dir):
                if file.endswith('.json'):
                    lang_code = file[:-5]
                    languages.append(lang_code)
        return languages

    def set_language(self, language_code):
        if self.load_language(language_code):
            self.config_manager.set('ui.language', language_code)
            return True
        return False

    def get_current_language(self):
        return self.current_language