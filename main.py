import sys, os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QInputDialog, QListWidget, QLabel
from window_frame import CustomWindow

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Hub")
        self.resize(350, 500)
        lay = QVBoxLayout(self)
        self.list = QListWidget()
        self.refresh()
        
        btn_open = QPushButton("Open Project Window")
        btn_new = QPushButton("Create New Project")
        
        lay.addWidget(QLabel("<b>EXISTING PROJECTS</b>"))
        lay.addWidget(self.list)
        lay.addWidget(btn_open)
        lay.addWidget(btn_new)

        btn_new.clicked.connect(self.new_win)
        btn_open.clicked.connect(self.open_win)
        self.active = []

    def refresh(self):
        self.list.clear()
        if os.path.exists("projects"):
            # We list folders inside the projects directory
            projects = [d for d in os.listdir("projects") if os.path.isdir(os.path.join("projects", d))]
            self.list.addItems(projects)

    def new_win(self):
        n, ok = QInputDialog.getText(self, "New Project", "Window Name:")
        if ok and n:
            # Create project directory immediately
            os.makedirs(os.path.join("projects", n), exist_ok=True)
            w = CustomWindow(n)
            w.show()
            self.active.append(w)
            self.refresh()

    def open_win(self):
        it = self.list.currentItem()
        if it:
            w = CustomWindow(it.text())
            w.show()
            self.active.append(w)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    d = Dashboard()
    d.show()
    sys.exit(app.exec())