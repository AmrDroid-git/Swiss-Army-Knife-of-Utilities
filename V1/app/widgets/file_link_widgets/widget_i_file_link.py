from PySide6.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QMenu, QFileDialog, QInputDialog
from PySide6.QtCore import Qt
from app.widgets.base_widget import BaseComponent

class WidgetIFileLink(BaseComponent):
    """
    Provides an input path selector for a single specific file.
    Gives a browse prompt for files ("...") which fills the textbox.
    """
    def __init__(self, parent, pos):
        super().__init__(parent, "widget_i_file_link", pos)
        self.field_type = "file_field"
        self.mode = "input"
        
        self.resize(220, 45)
        self.layout = QHBoxLayout(self)
        
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("INPUT FILE")
        self.layout.addWidget(self.entry)
        
        # Visual File Browser trigger
        self.browse_btn = QPushButton("...")
        self.browse_btn.setFixedWidth(30)
        self.browse_btn.clicked.connect(self.browse)
        self.layout.addWidget(self.browse_btn)

    def contextMenuEvent(self, event):
        """ Context menu supports altering default arg and default string logic. """
        if not self.is_edit_mode:
            menu = QMenu(self)
            clear_act = menu.addAction("Clear Content")
            if menu.exec(event.globalPos()) == clear_act:
                self.set_value("")
            return
            
        menu = QMenu(self)
        
        edit_act = menu.addAction("Edit Default Value")
        order_act = menu.addAction(f"Set Arg Order ({self.arg_order})")
        res_act, del_act = self.add_base_actions(menu)
        
        action = menu.exec(event.globalPos())
        
        if action == edit_act:
            t, ok = QInputDialog.getText(self, "Edit", "Default Value:", text=self.entry.text())
            if ok: self.entry.setText(t)
        elif action == order_act:
            val, ok = QInputDialog.getInt(self, "Order", "Arg Index:", self.arg_order, 0, 100)
            if ok: self.arg_order = val
            
        self.handle_base_actions(action, res_act, del_act)

    def browse(self):
        """ Triggered by the "..." button. Pulls a file path context dialog. """
        if self.is_edit_mode: return # Disabled while editing interface layout
        
        path, _ = QFileDialog.getOpenFileName(self, "Select Input File")
        if path: self.entry.setText(path)

    def get_value(self): 
        # Scraped by button Execution
        return self.entry.text()

    def set_value(self, val): 
        self.entry.setText(val)
    
    def to_dict(self):
        data = super().to_dict()
        data["value"] = self.entry.text()
        return data

    def from_dict(self, data):
        super().from_dict(data)
        self.entry.setText(data.get("value", ""))
