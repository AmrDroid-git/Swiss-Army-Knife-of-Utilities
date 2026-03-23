from PySide6.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QMenu, QFileDialog, QInputDialog
from .base import BaseComponent

class CustomField(BaseComponent):
    def __init__(self, parent, pos, field_type):
        super().__init__(parent, field_type, pos)
        self.setFixedSize(220, 45)
        self.mode = "input"
        self.layout = QHBoxLayout(self)
        self.entry = QLineEdit()
        self.layout.addWidget(self.entry)
        
        if field_type == "file_field":
            self.browse_btn = QPushButton("...")
            self.browse_btn.setFixedWidth(30)
            self.browse_btn.clicked.connect(self.browse)
            self.layout.addWidget(self.browse_btn)

    def contextMenuEvent(self, event):
        if not self.is_edit_mode: return
        menu = QMenu(self)
        mode_act = menu.addAction(f"Switch to {'OUTPUT' if self.mode == 'input' else 'INPUT'}")
        order_act = menu.addAction(f"Set Arg Order ({self.arg_order})")
        res_act, del_act = self.add_base_actions(menu)
        
        action = menu.exec(event.globalPos())
        if action == mode_act:
            self.mode = "output" if self.mode == "input" else "input"
            self.entry.setReadOnly(self.mode == "output")
            self.entry.setPlaceholderText(f"MODE: {self.mode.upper()}")
        elif action == order_act:
            val, ok = QInputDialog.getInt(self, "Order", "Arg Index:", self.arg_order, 0, 100)
            if ok: self.arg_order = val
        self.handle_base_actions(action, res_act, del_act)

    def browse(self):
        if self.is_edit_mode: return
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path: self.entry.setText(path)

    def get_value(self): return self.entry.text()
    def set_value(self, val): self.entry.setText(val)