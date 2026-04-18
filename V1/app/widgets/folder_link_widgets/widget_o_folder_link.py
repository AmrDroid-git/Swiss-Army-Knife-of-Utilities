from PySide6.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QMenu, QFileDialog
from PySide6.QtCore import Qt
from app.widgets.base_widget import BaseComponent

class WidgetOFolderLink(BaseComponent):
    """
    Provides an interface to select a master output directory for script operations.
    Acts identically to an Output-File link.
    """
    def __init__(self, parent, pos):
        super().__init__(parent, "widget_o_folder_link", pos)
        self.field_type = "folder_field"
        self.mode = "output"
        
        self.resize(220, 45)
        self.layout = QHBoxLayout(self)
        
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("OUTPUT FOLDER")
        self.entry.setReadOnly(True)
        self.layout.addWidget(self.entry)
        
        self.browse_btn = QPushButton("...")
        self.browse_btn.setFixedWidth(30)
        self.browse_btn.clicked.connect(self.browse)
        self.layout.addWidget(self.browse_btn)

    def contextMenuEvent(self, event):
        if not self.is_edit_mode:
            menu = QMenu(self)
            clear_act = menu.addAction("Clear Content")
            if menu.exec(event.globalPos()) == clear_act:
                self.set_value("")
            return
            
        menu = QMenu(self)
        res_act, del_act = self.add_base_actions(menu)
        action = menu.exec(event.globalPos())
        self.handle_base_actions(action, res_act, del_act)

    def browse(self):
        if self.is_edit_mode: return
        path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if path: self.entry.setText(path)

    def get_value(self): return self.entry.text()
    def set_value(self, val): self.entry.setText(val)
