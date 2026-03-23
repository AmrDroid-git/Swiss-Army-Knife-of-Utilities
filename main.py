import sys
from PySide6.QtWidgets import QApplication
from dashboard import Dashboard

def main():
    # Initialize the high-level application object
    app = QApplication(sys.argv)
    
    # Create and show the dashboard
    gui = Dashboard()
    gui.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()