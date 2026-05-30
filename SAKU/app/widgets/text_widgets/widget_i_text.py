from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QMenu, QInputDialog
from PySide6.QtCore import Qt
from app.widgets.base_widget import BaseComponent
from app.translator import t

class WidgetIText(BaseComponent):
    """
    A simple input text field. Usually passed to python scripts as an argument.
    """
    def __init__(self, parent, pos):
        super().__init__(parent, "widget_i_text", pos)
        self.field_type = "text_field"  # Identifier used by script scraper
        self.mode = "input"             # Will be scraped to feed sys.argv sequence
        
        self.resize(220, 45)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.entry = QLineEdit()
        self.entry.setPlaceholderText(t("input_text"))
        self.layout.addWidget(self.entry)

    def contextMenuEvent(self, event):
        """ Allows setting default values and importantly, the Argument Order. """
        if not self.is_edit_mode:
            menu = QMenu(self)
            clear_act = menu.addAction(t("clear_content"))
            if menu.exec(event.globalPos()) == clear_act:
                self.set_value("")
            return
            
        menu = QMenu(self)
        
        edit_act = menu.addAction(t("edit_default_value"))
        # Determines what position this argument will hold when sending to Python index
        order_act = menu.addAction(t("set_arg_order").format(order=self.arg_order))
        font_act, res_act, del_act = self.add_base_actions(menu)
        
        action = menu.exec(event.globalPos())
        
        if action == edit_act:
            text_val, ok = QInputDialog.getText(self, t("edit_dialog_title"), t("edit_dialog_prompt"), text=self.entry.text())
            if ok: self.entry.setText(text_val)
        elif action == order_act:
            val, ok = QInputDialog.getInt(self, t("order_dialog_title"), t("order_dialog_prompt"), self.arg_order, 0, 100)
            if ok: self.arg_order = val
            
        self.handle_base_actions(action, font_act, res_act, del_act)

    def apply_font(self, font):
        font_str = f"{font.family()}, Arial, sans-serif"
        self.entry.setFont(font)
        self.entry.setStyleSheet(f"QLineEdit {{font-family: '{font_str}'; font-size: {font.pointSize()}pt !important;}}")

    def get_value(self): 
        """ Called by the button execution sequence to fetch the text data """
        return self.entry.text()

    def set_value(self, val): 
        self.entry.setText(val)
    
    def to_dict(self):
        """ Store field contents to json state. """
        data = super().to_dict()
        data["value"] = self.entry.text()
        return data

    def from_dict(self, data):
        """ Restore field content from json state. """
        super().from_dict(data)
        self.entry.setText(data.get("value", ""))
