from PySide6.QtWidgets import QLabel, QHBoxLayout, QMenu, QInputDialog
from PySide6.QtCore import Qt
from app.widgets.base_widget import BaseComponent

class WidgetLabel(BaseComponent):
    """
    A simple draggable text label. It is used to label inputs or title the window.
    """
    def __init__(self, parent, pos, text="Text Label"):
        super().__init__(parent, "widget_label", pos)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create and setup the internal QLabel
        self.lbl = QLabel(text)
        self.layout.addWidget(self.lbl)

    def contextMenuEvent(self, event):
        """ Provides right-click functionality to edit the displayed label text. """
        if not self.is_edit_mode: return
        menu = QMenu(self)
        
        edit_act = menu.addAction("Edit Text")
        font_act, res_act, del_act = self.add_base_actions(menu)
        
        action = menu.exec(event.globalPos())
        
        if action == edit_act:
            t, ok = QInputDialog.getText(self, "Edit", "Text:", text=self.lbl.text())
            if ok: self.lbl.setText(t)
            
        self.handle_base_actions(action, font_act, res_act, del_act)

    def apply_font(self, font):
        self.lbl.setFont(font)

    def to_dict(self):
        """ Include the label text when saving the widget layout. """
        data = super().to_dict()
        data["text"] = self.lbl.text()
        return data

    def from_dict(self, data):
        """ Restore the label text when loading the layout. """
        super().from_dict(data)
        self.lbl.setText(data.get("text", "Text Label"))
