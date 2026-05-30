import json
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Theme Stylesheets — defined in Python for readability and no JSON escaping
# ---------------------------------------------------------------------------

LIGHT_STYLESHEET = """
QWidget {
    background-color: #f0f2f5;
    color: #1a1a2e;
}
QMainWindow, QDialog {
    background-color: #f0f2f5;
}
QMenuBar {
    background-color: #ffffff;
    color: #1a1a2e;
    border-bottom: 1px solid #d8dde6;
    padding: 2px;
}
QMenuBar::item {
    padding: 5px 10px;
    border-radius: 4px;
}
QMenuBar::item:selected {
    background-color: #e8eaf6;
    color: #4f46e5;
}
QMenu {
    background-color: #ffffff;
    color: #1a1a2e;
    border: 1px solid #d8dde6;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #e8eaf6;
    color: #4f46e5;
}
QMenu::separator {
    height: 1px;
    background: #d8dde6;
    margin: 4px 8px;
}
QPushButton {
    background-color: #4f46e5;
    color: #ffffff;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #4338ca;
}
QPushButton:pressed {
    background-color: #3730a3;
}
QPushButton:checked {
    background-color: #dc2626;
    color: #ffffff;
}
QPushButton:checked:hover {
    background-color: #b91c1c;
}
QPushButton:disabled {
    background-color: #c7cbd4;
    color: #9ca3af;
}
QTreeWidget {
    background-color: #ffffff;
    color: #1a1a2e;
    border: 1px solid #d8dde6;
    border-radius: 8px;
    padding: 4px;
    outline: none;
}
QTreeWidget::item {
    padding: 7px 4px;
    border-radius: 4px;
}
QTreeWidget::item:selected {
    background-color: #e8eaf6;
    color: #4f46e5;
}
QTreeWidget::item:hover {
    background-color: #f3f4f6;
}
QHeaderView::section {
    background-color: #f8f9fa;
    color: #6b7280;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #d8dde6;
    font-weight: 600;
    font-size: 12px;
}
QLabel {
    color: #1a1a2e;
    background: transparent;
}
QLineEdit {
    background-color: #ffffff;
    color: #1a1a2e;
    border: 1.5px solid #d8dde6;
    border-radius: 5px;
    padding: 6px 10px;
    selection-background-color: #e8eaf6;
    selection-color: #4f46e5;
}
QLineEdit:focus {
    border-color: #4f46e5;
}
QLineEdit:read-only {
    background-color: #f3f4f6;
    color: #374151;
}
QTextEdit, QTextBrowser {
    background-color: #ffffff;
    color: #1a1a2e;
    border: 1.5px solid #d8dde6;
    border-radius: 5px;
    padding: 6px;
    selection-background-color: #e8eaf6;
}
QTextEdit:focus {
    border-color: #4f46e5;
}
QComboBox {
    background-color: #ffffff;
    color: #1a1a2e;
    border: 1.5px solid #d8dde6;
    border-radius: 5px;
    padding: 5px 10px;
    min-height: 28px;
}
QComboBox:focus {
    border-color: #4f46e5;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1a1a2e;
    border: 1px solid #d8dde6;
    selection-background-color: #e8eaf6;
    selection-color: #4f46e5;
    padding: 4px;
}
QScrollBar:vertical {
    background: #f0f2f5;
    border: none;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #c7cbd4;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #9ca3af;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #f0f2f5;
    border: none;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #c7cbd4;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: #9ca3af;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QScrollArea {
    border: 1px solid #d8dde6;
    border-radius: 6px;
    background-color: #f8f9fa;
}
QMessageBox {
    background-color: #ffffff;
}
EditorCanvas {
    background-color: #ffffff;
}
"""

DARK_STYLESHEET = """
QWidget {
    background-color: #0f1117;
    color: #e2e8f0;
}
QMainWindow, QDialog {
    background-color: #0f1117;
}
QMenuBar {
    background-color: #1a1d27;
    color: #e2e8f0;
    border-bottom: 1px solid #2d3148;
    padding: 2px;
}
QMenuBar::item {
    padding: 5px 10px;
    border-radius: 4px;
}
QMenuBar::item:selected {
    background-color: #2d3148;
    color: #818cf8;
}
QMenu {
    background-color: #1a1d27;
    color: #e2e8f0;
    border: 1px solid #2d3148;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #2d3148;
    color: #818cf8;
}
QMenu::separator {
    height: 1px;
    background: #2d3148;
    margin: 4px 8px;
}
QPushButton {
    background-color: #4f46e5;
    color: #ffffff;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #6366f1;
}
QPushButton:pressed {
    background-color: #3730a3;
}
QPushButton:checked {
    background-color: #dc2626;
    color: #ffffff;
}
QPushButton:checked:hover {
    background-color: #ef4444;
}
QPushButton:disabled {
    background-color: #2d3148;
    color: #64748b;
}
QTreeWidget {
    background-color: #1a1d27;
    color: #e2e8f0;
    border: 1px solid #2d3148;
    border-radius: 8px;
    padding: 4px;
    outline: none;
}
QTreeWidget::item {
    padding: 7px 4px;
    border-radius: 4px;
}
QTreeWidget::item:selected {
    background-color: #2d3148;
    color: #818cf8;
}
QTreeWidget::item:hover {
    background-color: #21253a;
}
QHeaderView::section {
    background-color: #1a1d27;
    color: #64748b;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #2d3148;
    font-weight: 600;
    font-size: 12px;
}
QLabel {
    color: #e2e8f0;
    background: transparent;
}
QLineEdit {
    background-color: #1e2231;
    color: #e2e8f0;
    border: 1.5px solid #2d3148;
    border-radius: 5px;
    padding: 6px 10px;
    selection-background-color: #4f46e5;
    selection-color: #ffffff;
}
QLineEdit:focus {
    border-color: #6366f1;
}
QLineEdit:read-only {
    background-color: #161924;
    color: #94a3b8;
}
QTextEdit, QTextBrowser {
    background-color: #1e2231;
    color: #e2e8f0;
    border: 1.5px solid #2d3148;
    border-radius: 5px;
    padding: 6px;
    selection-background-color: #4f46e5;
}
QTextEdit:focus {
    border-color: #6366f1;
}
QComboBox {
    background-color: #1e2231;
    color: #e2e8f0;
    border: 1.5px solid #2d3148;
    border-radius: 5px;
    padding: 5px 10px;
    min-height: 28px;
}
QComboBox:focus {
    border-color: #6366f1;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #1e2231;
    color: #e2e8f0;
    border: 1px solid #2d3148;
    selection-background-color: #2d3148;
    selection-color: #818cf8;
    padding: 4px;
}
QScrollBar:vertical {
    background: #0f1117;
    border: none;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #2d3148;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #4b5280;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #0f1117;
    border: none;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #2d3148;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: #4b5280;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QScrollArea {
    border: 1px solid #2d3148;
    border-radius: 6px;
    background-color: #1a1d27;
}
QMessageBox {
    background-color: #1a1d27;
    color: #e2e8f0;
}
EditorCanvas {
    background-color: #161924;
}
"""

HACKING_STYLESHEET = """
QWidget {
    background-color: #030a03;
    color: #00ff41;
}
QMainWindow, QDialog {
    background-color: #030a03;
}
QMenuBar {
    background-color: #071007;
    color: #00ff41;
    border-bottom: 1px solid #003b00;
    padding: 2px;
}
QMenuBar::item {
    padding: 5px 10px;
    border-radius: 0px;
}
QMenuBar::item:selected {
    background-color: #003b00;
    color: #00ff41;
}
QMenu {
    background-color: #071007;
    color: #00ff41;
    border: 1px solid #003b00;
    border-radius: 0px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
}
QMenu::item:selected {
    background-color: #003b00;
    color: #00ff41;
}
QMenu::separator {
    height: 1px;
    background: #003b00;
    margin: 4px 8px;
}
QPushButton {
    background-color: #003b00;
    color: #00ff41;
    border: 1px solid #00ff41;
    padding: 8px 16px;
    border-radius: 2px;
    font-weight: bold;
    font-size: 13px;
    font-family: 'Courier New', monospace;
}
QPushButton:hover {
    background-color: #005700;
}
QPushButton:pressed {
    background-color: #00ff41;
    color: #030a03;
}
QPushButton:checked {
    background-color: #ff0000;
    color: #030a03;
    border-color: #ff0000;
}
QPushButton:checked:hover {
    background-color: #cc0000;
}
QPushButton:disabled {
    background-color: #071007;
    color: #005700;
    border-color: #003b00;
}
QTreeWidget {
    background-color: #071007;
    color: #00ff41;
    border: 1px solid #003b00;
    border-radius: 0px;
    padding: 4px;
    outline: none;
}
QTreeWidget::item {
    padding: 7px 4px;
}
QTreeWidget::item:selected {
    background-color: #003b00;
    color: #00ff41;
}
QTreeWidget::item:hover {
    background-color: #0a1a0a;
}
QHeaderView::section {
    background-color: #030a03;
    color: #007a20;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #003b00;
    font-weight: bold;
}
QLabel {
    color: #00ff41;
    background: transparent;
}
QLineEdit {
    background-color: #071007;
    color: #00ff41;
    border: 1px solid #003b00;
    border-radius: 2px;
    padding: 6px 10px;
    selection-background-color: #003b00;
    selection-color: #00ff41;
}
QLineEdit:focus {
    border-color: #00ff41;
}
QLineEdit:read-only {
    background-color: #030a03;
    color: #007a20;
}
QTextEdit, QTextBrowser {
    background-color: #071007;
    color: #00ff41;
    border: 1px solid #003b00;
    border-radius: 2px;
    padding: 6px;
    selection-background-color: #003b00;
}
QTextEdit:focus {
    border-color: #00ff41;
}
QComboBox {
    background-color: #071007;
    color: #00ff41;
    border: 1px solid #003b00;
    border-radius: 2px;
    padding: 5px 10px;
    min-height: 28px;
}
QComboBox:focus {
    border-color: #00ff41;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #071007;
    color: #00ff41;
    border: 1px solid #003b00;
    selection-background-color: #003b00;
    selection-color: #00ff41;
    padding: 4px;
}
QScrollBar:vertical {
    background: #030a03;
    border: none;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #003b00;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #00ff41;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #030a03;
    border: none;
    height: 8px;
}
QScrollBar::handle:horizontal {
    background: #003b00;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: #00ff41;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QScrollArea {
    border: 1px solid #003b00;
    background-color: #071007;
}
QMessageBox {
    background-color: #071007;
    color: #00ff41;
}
EditorCanvas {
    background-color: #030a03;
}
"""

# Map theme IDs to their stylesheets
THEME_STYLESHEETS = {
    "white": LIGHT_STYLESHEET,
    "dark": DARK_STYLESHEET,
    "hacking": HACKING_STYLESHEET,
}


class ThemeManager:
    """Manages application themes - loading, applying, and switching between themes."""
    
    THEMES_DIR = Path(__file__).parent.parent / "themes"
    CONFIG_DIR = Path(__file__).parent.parent.parent / "user_workspaces"
    CONFIG_FILE = CONFIG_DIR / "app_settings.json"
    AVAILABLE_THEMES = ["white", "dark", "hacking"]
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
