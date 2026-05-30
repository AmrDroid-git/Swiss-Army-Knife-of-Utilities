# Entry point to launch the application
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont
from app.ui.dashboard import Dashboard
from app.core.theme_manager import get_theme_manager

def main():
    # Suppress Windows font warnings
    os.environ['QT_QPA_FONTDIR'] = ''
    os.environ['QT_LOGGING_RULES'] = 'qt.qpa.fonts=false'
    
    app = QApplication(sys.argv)
    
    # Use the operating system default UI font instead of a bundled custom font.
    # This keeps the application looking closer to normal Windows/Linux apps.
    default_font = QFontDatabase.systemFont(QFontDatabase.GeneralFont)
    if not default_font.family():
        default_font = QFont("Segoe UI", 10)
    default_font.setPointSize(10)
    default_font.setStyleStrategy(QFont.PreferAntialias | QFont.PreferQuality)
    app.setFont(default_font)
    
    # Use Fusion style — cross-platform, clean, and fully customisable via Qt stylesheets
    app.setStyle("Fusion")
    
    # Load the saved theme and apply it at the application level.
    # This single call covers ALL windows (dashboard + every project window).
    tm = get_theme_manager()
    app.setStyleSheet(tm.get_stylesheet())
    
    dash = Dashboard()
    dash.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
