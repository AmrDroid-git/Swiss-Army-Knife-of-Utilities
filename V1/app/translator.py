"""
Translation Manager: Handles language switching and translations for the entire application.
"""

import json
import os
from PySide6.QtCore import QObject, Signal

TRANSLATIONS_FILE = os.path.join(os.path.dirname(__file__), "translations.json")
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "user_workspaces", "app_settings.json")


class LanguageChangeSignal(QObject):
    """Signal emitter for language changes."""
    language_changed = Signal(str)  # Emits language code when changed


_language_signal = LanguageChangeSignal()


class TranslationManager:
    """Singleton for managing application translations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TranslationManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.translations = {}
        self.current_language = "en"
        self.available_languages = []
        
        self._load_translations()
        self._load_settings()
    
    def _load_translations(self):
        """Load translations from JSON file."""
        try:
            with open(TRANSLATIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.translations = data.get("translations", {})
                self.available_languages = data.get("languages", ["English", "Français", "العربية"])
                self.language_codes = data.get("language_codes", {})
        except Exception as e:
            print(f"Error loading translations: {e}")
            self.translations = {}
            self.available_languages = ["English", "Français", "العربية"]
    
    def _load_settings(self):
        """Load saved language preference."""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    lang_code = data.get("language", "en")
                    self.set_language_by_code(lang_code)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def _save_settings(self):
        """Save language preference."""
        try:
            os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
            data = {"language": self.current_language}
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key, default=""):
        """Get translated string for the current language."""
        if self.current_language in self.translations:
            return self.translations[self.current_language].get(key, default)
        return default
    
    def set_language(self, language_name):
        """Set language by display name (e.g., 'Français')."""
        if language_name in self.language_codes:
            self.current_language = self.language_codes[language_name]
            self._save_settings()
            # Emit signal for language change
            _language_signal.language_changed.emit(self.current_language)
            return True
        return False
    
    def set_language_by_code(self, language_code):
        """Set language by code (e.g., 'fr')."""
        if language_code in self.translations:
            self.current_language = language_code
            self._save_settings()
            return True
        return False
    
    def get_current_language_name(self):
        """Get current language display name."""
        for name, code in self.language_codes.items():
            if code == self.current_language:
                return name
        return "English"

# Global translation manager instance
_translator = TranslationManager()

def t(key, default=""):
    """Shorthand function to get translated string."""
    return _translator.get(key, default)

def get_translator():
    """Get the global translator instance."""
    return _translator

def get_language_signal():
    """Get the language change signal."""
    return _language_signal.language_changed
