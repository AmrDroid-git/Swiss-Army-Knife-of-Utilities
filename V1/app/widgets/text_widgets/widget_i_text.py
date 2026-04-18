from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QMenu, QInputDialog
from PySide6.QtCore import Qt
from app.widgets.base_widget import BaseComponent

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
        self.entry.setPlaceholderText("INPUT TEXT")
        self.layout.addWidget(self.entry)

    def contextMenuEvent(self, event):
        """ Allows setting default values and importantly, the Argument Order. """
        if not self.is_edit_mode:
            menu = QMenu(self)
            clear_act = menu.addAction("Clear Content")
            if menu.exec(event.globalPos()) == clear_act:
                self.set_value("")
            return
            
        menu = QMenu(self)
        
        edit_act = menu.addAction("Edit Default Value")
        # Determines what position this argument will hold when sending to Python index
        order_act = menu.addAction(f"Set Arg Order ({self.arg_order})")
        font_act, res_act, del_act = self.add_base_actions(menu)
        
        action = menu.exec(event.globalPos())
        
        if action == edit_act:
            t, ok = QInputDialog.getText(self, "Edit", "Default Value:", text=self.entry.text())
            if ok: self.entry.setText(t)
        elif action == order_act:
            val, ok = QInputDialog.getInt(self, "Order", "Arg Index:", self.arg_order, 0, 100)
            if ok: self.arg_order = val
            
        self.handle_base_actions(action, font_act, res_act, del_act)

    def apply_font(self, font):
        self.entry.setFont(font)

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
