# Entry point to launch the application
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase
from app.ui.dashboard import Dashboard

def main():
    app = QApplication(sys.argv)
    
    # Register purely downloaded GUI fonts natively into the system
    font_path = os.path.join(os.path.dirname(__file__), "app", "assets", "fonts", "Outfit.ttf")
    if os.path.exists(font_path):
        QFontDatabase.addApplicationFont(font_path)
    
    # Use Windows style for native look
    app.setStyle("Windows")
    
    # Add professional stylesheet for menus and dialogs
    stylesheet = """
        QDialog {
            background-color: #f0f0f0;
        }
        QLabel {
            color: #000000;
        }
        QListWidget {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #cccccc;
        }
        QListWidget::item:selected {
            background-color: #e8e8e8;
        }
        QComboBox {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #cccccc;
        }
        QSpinBox {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #cccccc;
        }
        QPushButton {
            background-color: #f0f0f0;
            color: #000000;
            border: 1px solid #cccccc;
            padding: 4px 16px;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        QMenu {
            background-color: #f0f0f0;
            color: #000000;
            border: 1px solid #d0d0d0;
        }
        QMenu::item:selected {
            background-color: #e8e8e8;
        }
    """
    app.setStyleSheet(stylesheet)
    
    dash = Dashboard()
    dash.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
