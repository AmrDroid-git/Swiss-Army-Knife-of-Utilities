from PySide6.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QMenu, QFileDialog, QInputDialog
from PySide6.QtCore import Qt
from .base import BaseComponent

class CustomField(BaseComponent):
    def __init__(self, parent, pos, field_type):
        super().__init__(parent, field_type, pos)
        self.field_type = field_type  
        self.setFixedSize(220, 45)
        self.mode = "input"
        self.layout = QHBoxLayout(self)
        self.entry = QLineEdit()
        self.layout.addWidget(self.entry)
        
        # ADDED: Show the browse button for both files AND folders
        if field_type in ["file_field", "folder_field"]:
            self.browse_btn = QPushButton("...")
            self.browse_btn.setFixedWidth(30)
            self.browse_btn.clicked.connect(self.browse)
            self.layout.addWidget(self.browse_btn)

    def contextMenuEvent(self, event):
        if not self.is_edit_mode: return
        menu = QMenu(self)
        edit_act = menu.addAction("Edit Default Value")
        mode_act = menu.addAction(f"Switch to {'OUTPUT' if self.mode == 'input' else 'INPUT'}")
        order_act = menu.addAction(f"Set Arg Order ({self.arg_order})")
        res_act, del_act = self.add_base_actions(menu)
        
        action = menu.exec(event.globalPos())
        if action == edit_act:
            t, ok = QInputDialog.getText(self, "Edit", "Default Value:", text=self.entry.text())
            if ok: self.entry.setText(t)
        elif action == mode_act:
            self.mode = "output" if self.mode == "input" else "input"
            self.entry.setReadOnly(self.mode == "output")
            self.entry.setPlaceholderText(f"MODE: {self.mode.upper()}")
        elif action == order_act:
            val, ok = QInputDialog.getInt(self, "Order", "Arg Index:", self.arg_order, 0, 100)
            if ok: self.arg_order = val
        self.handle_base_actions(action, res_act, del_act)

    def browse(self):
        if self.is_edit_mode: return
        
        # UPDATED LOGIC: If it's an output OR a folder field, ask for a Directory!
        if self.mode == "output" or self.field_type == "folder_field":
            path = QFileDialog.getExistingDirectory(self, "Select Folder")
        else:
            # Otherwise, ask for a File
            path, _ = QFileDialog.getOpenFileName(self, "Select File")
            
        if path: self.entry.setText(path)

    def get_value(self): return self.entry.text()
    def set_value(self, val): self.entry.setText(val)