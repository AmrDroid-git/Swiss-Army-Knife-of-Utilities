from PySide6.QtWidgets import QLabel, QHBoxLayout, QMenu, QInputDialog
from PySide6.QtCore import Qt
from .base import BaseComponent

class DraggableLabel(BaseComponent):
    def __init__(self, parent, pos, text="Text Label"):
        super().__init__(parent, "label", pos)
        self.layout = QHBoxLayout(self)
        self.lbl = QLabel(text)
        self.layout.addWidget(self.lbl)

    def contextMenuEvent(self, event):
        if not self.is_edit_mode: return
        menu = QMenu(self)
        edit_act = menu.addAction("Edit Text")
        res_act, del_act = self.add_base_actions(menu)
        action = menu.exec(event.globalPos())
        if action == edit_act:
            t, ok = QInputDialog.getText(self, "Edit", "Text:", text=self.lbl.text())
            if ok: self.lbl.setText(t)
        self.handle_base_actions(action, res_act, del_act)