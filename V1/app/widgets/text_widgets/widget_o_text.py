from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QMenu
from PySide6.QtCore import Qt
from app.widgets.base_widget import BaseComponent
from app.translator import t

class WidgetOText(BaseComponent):
    """
    A strictly output-only text field. Scripts can update this field 
    to visually return short form strings to the user without using a full console.
    """
    def __init__(self, parent, pos):
        super().__init__(parent, "widget_o_text", pos)
        self.field_type = "text_field"
        self.mode = "output" # Read-only target output for Python return sequences
        
        self.resize(220, 45)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.entry = QLineEdit()
        self.entry.setReadOnly(True) # Block user interference
        self.entry.setPlaceholderText(t("output_text"))
        self.layout.addWidget(self.entry)

    def contextMenuEvent(self, event):
        """ Generic right click for outputs; no argument index needed. """
        if not self.is_edit_mode:
            menu = QMenu(self)
            clear_act = menu.addAction(t("clear_content"))
            if menu.exec(event.globalPos()) == clear_act:
                self.set_value("")
            return
            
        menu = QMenu(self)
        font_act, res_act, del_act = self.add_base_actions(menu)
        action = menu.exec(event.globalPos())
        self.handle_base_actions(action, font_act, res_act, del_act)

    def apply_font(self, font):
        self.entry.setFont(font)

    def get_value(self): 
        return self.entry.text()

    def set_value(self, val): 
        """ Called rapidly by script engine when return/crash data generates """
        self.entry.setText(val)
