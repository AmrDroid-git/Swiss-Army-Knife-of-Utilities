from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QMimeData, QByteArray, QDataStream, QIODevice, QPoint
from PySide6.QtGui import QDrag, QPixmap
from PySide6.QtCore import QSize

class ToolboxItem(QLabel):
    """
    These are the visual buttons residing inside the Edit Mode Toolbar.
    They initiate Drag and Drop QDrag events exactly like Qt Designer.
    """
    def __init__(self, text, type_id):
        super().__init__(text)
        self.type_id = type_id
        
        # Premium dark styling
        self.setStyleSheet("""
            background: #2c3e50; 
            color: white; 
            padding: 12px; 
            border-radius: 4px; 
            margin: 2px;
            font-weight: bold;
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(50)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            
            # Pack exactly what widget we intend to create inside the drop stream
            mime.setData("application/x-widget-template", self.type_id.encode('utf-8'))
            drag.setMimeData(mime)
            
            # Create a visual pixmap of this button to show while dragging
            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
            
            drag.exec(Qt.CopyAction)
