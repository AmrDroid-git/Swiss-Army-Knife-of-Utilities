from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QMimeData, QPoint
from PySide6.QtGui import QDrag, QPixmap, QColor, QPainter
from PySide6.QtCore import QSize

class ToolboxItem(QLabel):
    """
    These are the visual buttons residing inside the Edit Mode Toolbar.
    They initiate Drag and Drop QDrag events exactly like Qt Designer.
    Styling is intentionally kept neutral so the active theme controls appearance.
    """
    def __init__(self, text, type_id):
        emoji_map = {
            "widget_button": "▶️",
            "widget_label": "🏷️",
            "widget_i_text": "🔤",
            "widget_o_text": "📝",
            "widget_select": "🔽",
            "widget_i_file_link": "📄",
            "widget_o_file_link": "💾",
            "widget_i_folder_link": "📁",
            "widget_o_folder_link": "📂",
            "widget_console": "🖥️",
            "widget_interactive_console": "⌨️",
            "widget_requirements_link": "📦",
        }
        display_text = f"{emoji_map.get(type_id, '•')}  {text}"
        super().__init__(display_text)
        self.type_id = type_id
        
        # Use a subtle accent border to make items visually distinct without
        # hardcoding colors — the theme's QLabel rule handles text/background.
        self.setStyleSheet("""
            QLabel {
                padding: 10px 12px;
                border-radius: 5px;
                margin: 2px;
                font-weight: 600;
                border: 1px solid rgba(128, 128, 128, 0.25);
            }
            QLabel:hover {
                border-color: rgba(128, 128, 128, 0.6);
            }
        """)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setMinimumHeight(44)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            
            # Pack exactly what widget we intend to create inside the drop stream
            mime.setData("application/x-widget-template", self.type_id.encode('utf-8'))
            drag.setMimeData(mime)
            
            # Create a minimal pixmap (nearly invisible) to avoid the ghost image glitch
            # Just a tiny semi-transparent dot
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.fillRect(pixmap.rect(), QColor(100, 100, 100, 60))
            painter.end()
            
            drag.setPixmap(pixmap)
            drag.setHotSpot(QPoint(12, 12))
            
            drag.exec(Qt.CopyAction)

