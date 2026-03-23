from PySide6.QtWidgets import QWidget, QInputDialog
from PySide6.QtCore import Qt, QPoint

class BaseComponent(QWidget):
    def __init__(self, parent, comp_type, pos=QPoint(0,0)):
        super().__init__(parent)
        self.comp_type = comp_type
        self.is_edit_mode = True
        self.arg_order = 0
        self.move(pos)
        self._drag_pos = None
        self.show()

    def set_edit_mode(self, enabled):
        self.is_edit_mode = enabled

    def mousePressEvent(self, event):
        if self.is_edit_mode and event.button() == Qt.LeftButton:
            self._drag_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_edit_mode and self._drag_pos:
            self.move(self.mapToParent(event.pos() - self._drag_pos))
        super().mouseMoveEvent(event)

    def add_base_actions(self, menu):
        menu.addSeparator()
        resize_act = menu.addAction("Resize")
        delete_act = menu.addAction("Delete")
        return resize_act, delete_act

    def handle_base_actions(self, action, res_act, del_act):
        if action == res_act:
            w, ok1 = QInputDialog.getInt(self, "Width", "Width:", self.width())
            h, ok2 = QInputDialog.getInt(self, "Height", "Height:", self.height())
            if ok1 and ok2: self.setFixedSize(w, h)
        elif action == del_act:
            self.deleteLater()