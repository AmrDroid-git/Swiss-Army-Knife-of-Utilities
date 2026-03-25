from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from canvas import EditorCanvas, ToolboxItem
import persistence

class CustomWindow(QWidget):
    def __init__(self, window_id):
        super().__init__()
        self.window_id = window_id
        self.setWindowTitle(f"Project: {window_id}")
        self.resize(1100, 750)
        self.layout = QVBoxLayout(self)
        
        # Navbar
        nav = QHBoxLayout()
        self.edit_btn = QPushButton("EDIT MODE")
        self.edit_btn.setCheckable(True)
        self.edit_btn.clicked.connect(self.toggle)
        save_btn = QPushButton("SAVE")
        save_btn.clicked.connect(lambda: persistence.save_window(self.window_id, self.canvas))
        
        nav.addWidget(QLabel(f"<b>{window_id.upper()}</b>"))
        nav.addStretch()
        nav.addWidget(self.edit_btn)
        nav.addWidget(save_btn)
        self.layout.addLayout(nav)

        # Content
        self.content = QHBoxLayout()
        self.canvas = EditorCanvas()
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(180)
        s_lay = QVBoxLayout(self.sidebar)
        s_lay.addWidget(ToolboxItem("Script Button", "script"))
        s_lay.addWidget(ToolboxItem("Text Label", "label"))
        s_lay.addWidget(ToolboxItem("Text Input/Output", "text"))
        s_lay.addWidget(ToolboxItem("File Input/Output", "file"))
        s_lay.addWidget(ToolboxItem("Folder Input/Output", "folder"))
        s_lay.addStretch()
        
        self.content.addWidget(self.canvas)
        self.content.addWidget(self.sidebar)
        self.layout.addLayout(self.content)
        
        self.sidebar.hide()
        persistence.load_window(self.window_id, self.canvas)

    def toggle(self):
        state = self.edit_btn.isChecked()
        self.canvas.is_edit_mode = state
        self.sidebar.setVisible(state)
        from components import BaseComponent
        for c in self.canvas.findChildren(BaseComponent): c.set_edit_mode(state)

    def closeEvent(self, event):
        persistence.save_window(self.window_id, self.canvas)
        event.accept()