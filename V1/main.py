# Entry point to launch the application
import sys
from PySide6.QtWidgets import QApplication
from app.ui.dashboard import Dashboard

def main():
    app = QApplication(sys.argv)
    
    # Optional: Set global App-level styling here if needed
    app.setStyle("Fusion")
    
    dash = Dashboard()
    dash.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
