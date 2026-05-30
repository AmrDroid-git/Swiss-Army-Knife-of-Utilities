import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Theme Stylesheets
# Simple, neutral Qt styles inspired by standard Windows/Linux desktop apps.
# The goal is readability: normal system font, low contrast borders, no purple.
# ---------------------------------------------------------------------------

LIGHT_STYLESHEET = """
QWidget {
    background-color: #f6f6f6;
    color: #202020;
}
QMainWindow, QDialog {
    background-color: #f6f6f6;
}
QMenuBar {
    background-color: #f3f3f3;
    color: #202020;
    border-bottom: 1px solid #d0d0d0;
    padding: 2px;
}
QMenuBar::item {
    padding: 5px 10px;
    background: transparent;
}
QMenuBar::item:selected {
    background-color: #e5e5e5;
    color: #000000;
}
QMenu {
    background-color: #ffffff;
    color: #202020;
    border: 1px solid #c8c8c8;
    padding: 3px;
}
QMenu::item {
    padding: 6px 22px;
}
QMenu::item:selected {
    background-color: #e5e5e5;
    color: #000000;
}
QMenu::separator {
    height: 1px;
    background: #d0d0d0;
    margin: 4px 8px;
}
QPushButton {
    background-color: #eeeeee;
    color: #202020;
    border: 1px solid #b8b8b8;
    border-radius: 3px;
    padding: 5px 10px;
    font-weight: normal;
}
QPushButton:hover {
    background-color: #e2e2e2;
    border-color: #9a9a9a;
}
QPushButton:pressed, QPushButton:checked {
    background-color: #d6d6d6;
    border-color: #7a7a7a;
}
QPushButton:disabled {
    background-color: #f2f2f2;
    color: #9a9a9a;
    border-color: #d0d0d0;
}
QPushButton#browseButton {
    min-width: 30px;
    max-width: 34px;
    padding: 0px;
    font-weight: normal;
}
QTreeWidget {
    background-color: #ffffff;
    color: #202020;
    border: 1px solid #c8c8c8;
    border-radius: 3px;
    padding: 2px;
    outline: none;
}
QTreeWidget::item {
    padding: 5px 3px;
}
QTreeWidget::item:selected {
    background-color: #dcdcdc;
    color: #000000;
}
QTreeWidget::item:hover {
    background-color: #eeeeee;
}
QHeaderView::section {
    background-color: #eeeeee;
    color: #202020;
    padding: 5px;
    border: none;
    border-bottom: 1px solid #c8c8c8;
    font-weight: normal;
}
QLabel {
    color: #202020;
    background: transparent;
}
QLineEdit {
    background-color: #ffffff;
    color: #202020;
    border: 1px solid #b8b8b8;
    border-radius: 3px;
    padding: 5px 7px;
    selection-background-color: #cfe8ff;
    selection-color: #000000;
}
QLineEdit:focus {
    border-color: #707070;
}
QLineEdit:read-only {
    background-color: #f2f2f2;
    color: #404040;
}
QTextEdit, QTextBrowser, QPlainTextEdit {
    background-color: #ffffff;
    color: #202020;
    border: 1px solid #b8b8b8;
    border-radius: 3px;
    padding: 5px;
    selection-background-color: #cfe8ff;
    selection-color: #000000;
}
QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #707070;
}
QComboBox {
    background-color: #ffffff;
    color: #202020;
    border: 1px solid #b8b8b8;
    border-radius: 3px;
    padding: 4px 8px;
    min-height: 26px;
}
QComboBox:focus {
    border-color: #707070;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #202020;
    border: 1px solid #b8b8b8;
    selection-background-color: #dcdcdc;
    selection-color: #000000;
    padding: 3px;
}
QScrollBar:vertical {
    background: #f0f0f0;
    border: none;
    width: 12px;
}
QScrollBar::handle:vertical {
    background: #c2c2c2;
    min-height: 28px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #a8a8a8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #f0f0f0;
    border: none;
    height: 12px;
}
QScrollBar::handle:horizontal {
    background: #c2c2c2;
    min-width: 28px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background: #a8a8a8;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QScrollArea {
    border: 1px solid #c8c8c8;
    border-radius: 3px;
    background-color: #f6f6f6;
}
QMessageBox {
    background-color: #ffffff;
    color: #202020;
}
EditorCanvas {
    background-color: #ffffff;
}
"""

DARK_STYLESHEET = """
QWidget {
    background-color: #202020;
    color: #eeeeee;
}
QMainWindow, QDialog {
    background-color: #202020;
}
QMenuBar {
    background-color: #252525;
    color: #eeeeee;
    border-bottom: 1px solid #404040;
    padding: 2px;
}
QMenuBar::item {
    padding: 5px 10px;
    background: transparent;
}
QMenuBar::item:selected {
    background-color: #353535;
    color: #ffffff;
}
QMenu {
    background-color: #252525;
    color: #eeeeee;
    border: 1px solid #555555;
    padding: 3px;
}
QMenu::item {
    padding: 6px 22px;
}
QMenu::item:selected {
    background-color: #3a3a3a;
    color: #ffffff;
}
QMenu::separator {
    height: 1px;
    background: #444444;
    margin: 4px 8px;
}
QPushButton {
    background-color: #333333;
    color: #eeeeee;
    border: 1px solid #666666;
    border-radius: 3px;
    padding: 5px 10px;
    font-weight: normal;
}
QPushButton:hover {
    background-color: #3f3f3f;
    border-color: #808080;
}
QPushButton:pressed, QPushButton:checked {
    background-color: #4a4a4a;
    border-color: #909090;
}
QPushButton:disabled {
    background-color: #282828;
    color: #777777;
    border-color: #444444;
}
QPushButton#browseButton {
    min-width: 30px;
    max-width: 34px;
    padding: 0px;
    font-weight: normal;
}
QTreeWidget {
    background-color: #252525;
    color: #eeeeee;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 2px;
    outline: none;
}
QTreeWidget::item {
    padding: 5px 3px;
}
QTreeWidget::item:selected {
    background-color: #3a3a3a;
    color: #ffffff;
}
QTreeWidget::item:hover {
    background-color: #303030;
}
QHeaderView::section {
    background-color: #2c2c2c;
    color: #eeeeee;
    padding: 5px;
    border: none;
    border-bottom: 1px solid #555555;
    font-weight: normal;
}
QLabel {
    color: #eeeeee;
    background: transparent;
}
QLineEdit {
    background-color: #2a2a2a;
    color: #eeeeee;
    border: 1px solid #666666;
    border-radius: 3px;
    padding: 5px 7px;
    selection-background-color: #5a5a5a;
    selection-color: #ffffff;
}
QLineEdit:focus {
    border-color: #9a9a9a;
}
QLineEdit:read-only {
    background-color: #303030;
    color: #d0d0d0;
}
QTextEdit, QTextBrowser, QPlainTextEdit {
    background-color: #2a2a2a;
    color: #eeeeee;
    border: 1px solid #666666;
    border-radius: 3px;
    padding: 5px;
    selection-background-color: #5a5a5a;
    selection-color: #ffffff;
}
QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #9a9a9a;
}
QComboBox {
    background-color: #2a2a2a;
    color: #eeeeee;
    border: 1px solid #666666;
    border-radius: 3px;
    padding: 4px 8px;
    min-height: 26px;
}
QComboBox:focus {
    border-color: #9a9a9a;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #2a2a2a;
    color: #eeeeee;
    border: 1px solid #666666;
    selection-background-color: #3a3a3a;
    selection-color: #ffffff;
    padding: 3px;
}
QScrollBar:vertical {
    background: #242424;
    border: none;
    width: 12px;
}
QScrollBar::handle:vertical {
    background: #555555;
    min-height: 28px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #707070;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #242424;
    border: none;
    height: 12px;
}
QScrollBar::handle:horizontal {
    background: #555555;
    min-width: 28px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background: #707070;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QScrollArea {
    border: 1px solid #555555;
    border-radius: 3px;
    background-color: #202020;
}
QMessageBox {
    background-color: #252525;
    color: #eeeeee;
}
EditorCanvas {
    background-color: #252525;
}
"""

# Map theme IDs to their stylesheets
THEME_STYLESHEETS = {
    "white": LIGHT_STYLESHEET,
    "dark": DARK_STYLESHEET,
}


class ThemeManager:
    """Manages application themes - loading, applying, and switching between themes."""
    
    THEMES_DIR = Path(__file__).parent.parent / "themes"
    CONFIG_DIR = Path(__file__).parent.parent.parent / "user_workspaces"
    CONFIG_FILE = CONFIG_DIR / "app_settings.json"
    AVAILABLE_THEMES = ["white", "dark"]
    DEFAULT_THEME = "white"
    
    def __init__(self):
        """Initialize theme manager and load saved theme preference."""
        self.current_theme = self.DEFAULT_THEME
        self.themes_cache = {}
        self._load_all_themes()
        self._load_saved_theme()
    
    def _load_all_themes(self):
        """Load all available themes into cache."""
        for theme_name in self.AVAILABLE_THEMES:
            self.themes_cache[theme_name] = self._load_theme_file(theme_name)
    
    def _load_theme_file(self, theme_name):
        """Load a single theme file and return its data (merges JSON metadata with Python stylesheet).
        
        Args:
            theme_name: Name of the theme (without .json extension)
            
        Returns:
            dict: Theme data containing name, colors, and stylesheet
        """
        theme_path = self.THEMES_DIR / f"{theme_name}.json"
        
        data = {}
        if theme_path.exists():
            try:
                with open(theme_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                print(f"Warning: Could not load theme metadata for {theme_name}: {e}")
        else:
            # Provide a fallback name if the JSON doesn't exist
            data = {"name": theme_name.capitalize()}
        
        # Always inject the Python-defined stylesheet (reliable, no JSON escaping issues)
        data["stylesheet"] = THEME_STYLESHEETS.get(theme_name, "")
        return data
    
    def get_theme(self, theme_name):
        """Get theme data by name."""
        if theme_name not in self.themes_cache:
            raise ValueError(f"Unknown theme: {theme_name}")
        return self.themes_cache[theme_name]
    
    def get_stylesheet(self, theme_name=None):
        """Get the stylesheet for a theme.
        
        Args:
            theme_name: Name of the theme (uses current if None)
            
        Returns:
            str: Qt stylesheet
        """
        if theme_name is None:
            theme_name = self.current_theme
        
        theme_data = self.get_theme(theme_name)
        return theme_data.get("stylesheet", "")
    
    def get_colors(self, theme_name=None):
        """Get the colors dictionary for a theme."""
        if theme_name is None:
            theme_name = self.current_theme
        theme_data = self.get_theme(theme_name)
        return theme_data.get("colors", {})
    
    def set_current_theme(self, theme_name):
        """Set the current active theme."""
        if theme_name not in self.themes_cache:
            raise ValueError(f"Unknown theme: {theme_name}")
        self.current_theme = theme_name
    
    def get_theme_name(self, theme_id):
        """Get display name of a theme."""
        theme_data = self.get_theme(theme_id)
        return theme_data.get("name", theme_id)
    
    def list_themes(self):
        """Get list of available themes."""
        return self.AVAILABLE_THEMES.copy()
    
    def list_themes_with_names(self):
        """Get list of available themes with their display names."""
        return [(theme_id, self.get_theme_name(theme_id)) 
                for theme_id in self.AVAILABLE_THEMES]
    
    def _load_saved_theme(self):
        """Load the saved theme preference from app_settings.json."""
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    saved_theme = settings.get("theme", self.DEFAULT_THEME)
                    if saved_theme in self.AVAILABLE_THEMES:
                        self.current_theme = saved_theme
        except Exception as e:
            print(f"Could not load saved theme preference: {e}")
            self.current_theme = self.DEFAULT_THEME
    
    def save_theme_preference(self):
        """Save the current theme preference to app_settings.json."""
        try:
            self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            
            settings = {}
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            settings["theme"] = self.current_theme
            
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Could not save theme preference: {e}")


# Singleton instance
_theme_manager_instance = None

def get_theme_manager():
    """Get or create the global theme manager instance."""
    global _theme_manager_instance
    if _theme_manager_instance is None:
        _theme_manager_instance = ThemeManager()
    return _theme_manager_instance
