from PySide6.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QMenu, QFileDialog, QInputDialog
from PySide6.QtCore import Qt
from app.widgets.base_widget import BaseComponent
from app.translator import t

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
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.entry = QLineEdit()
        self.entry.setPlaceholderText(t("input_file"))
        self.layout.addWidget(self.entry)
        
        # Visual File Browser trigger
        self.browse_btn = QPushButton(t("browse_button"))
        self.browse_btn.setFixedWidth(30)
        self.browse_btn.clicked.connect(self.browse)
        self.layout.addWidget(self.browse_btn)

    def contextMenuEvent(self, event):
        """ Context menu supports altering default arg and default string logic. """
        if not self.is_edit_mode:
            menu = QMenu(self)
        clear_act = menu.addAction(t("clear_content"))
        if menu.exec(event.globalPos()) == clear_act:
            self.set_value("")
            return
            
        menu = QMenu(self)
        
        edit_act = menu.addAction(t("edit_default_value"))
        order_act = menu.addAction(t("set_arg_order").format(order=self.arg_order))
        font_act, res_act, del_act = self.add_base_actions(menu)
        
        action = menu.exec(event.globalPos())
        
        if action == edit_act:
            text_val, ok = QInputDialog.getText(self, t("edit_dialog_title"), t("edit_dialog_prompt"), text=self.entry.text())
            if ok: self.entry.setText(text_val)
        elif action == order_act:
            val, ok = QInputDialog.getInt(self, t("order_dialog_title"), t("order_dialog_prompt"), self.arg_order, 0, 100)
            
        self.handle_base_actions(action, font_act, res_act, del_act)

    def apply_font(self, font):
        self.entry.setFont(font)

    def browse(self):
        """ Triggered by the "..." button. Pulls a file path context dialog. """
        if self.is_edit_mode: return # Disabled while editing interface layout
        
        path, _ = QFileDialog.getOpenFileName(self, t("select_input_file_dialog"))
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
