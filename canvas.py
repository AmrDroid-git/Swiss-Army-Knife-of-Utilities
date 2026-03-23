from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag
from components import ScriptButton, CustomField, DraggableLabel

class ToolboxItem(QLabel):
    def __init__(self, text, type_id):
        super().__init__(text)
        self.type_id = type_id
        self.setStyleSheet("background: #2c3e50; color: white; padding: 12px; border-radius: 4px; margin: 2px;")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.type_id)
            drag.setMimeData(mime)
            drag.exec(Qt.CopyAction)

class EditorCanvas(QFrame):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: #fdfdfd; border: 1px solid #ccc;")
        self.is_edit_mode = False

    def dragEnterEvent(self, event):
        if self.is_edit_mode: event.accept()

    def dropEvent(self, event):
        pos = event.position().toPoint()
        tid = event.mimeData().text()
        if tid == "script": ScriptButton(self, pos)
        elif tid == "label": DraggableLabel(self, pos)
        elif tid == "text":  CustomField(self, pos, "text_field")
        elif tid == "file":  CustomField(self, pos, "file_field")