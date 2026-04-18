from PySide6.QtWidgets import QWidget, QInputDialog
from PySide6.QtCore import Qt, QPoint

class BaseComponent(QWidget):
    """
    The BaseComponent is the foundation for all widgets in the application.
    It contains the core logic for dragging, resizing, json-serialization, 
    and handles the Edit Mode / Run Mode states.
    """
    def __init__(self, parent, comp_type, pos=QPoint(0,0)):
        super().__init__(parent)
        self.comp_type = comp_type      # Identifier for JSON (e.g., 'widget_button')
        self.is_edit_mode = True        # Toggles drag/editing versus normal interaction
        self.is_template = False        # If True, dragging spawns a ghost clone (Toolbar mode)
        self.arg_order = 0              # Determines argument order passed to scripts
        self.properties = {}            # Dictionary catching custom JSON attributes
        self.move(pos)                  # Initial spawn position
        self._drag_pos = None           # Internal tracker for mouse dragging
        
        # Geometrical mapping percentages!
        self._rel_x = 0.0
        self._rel_y = 0.0
        self._rel_w = 0.0
        self._rel_h = 0.0
        
        self.show()                     # Make widget visible on instantiation

    def update_relative_geometry(self):
        """ Computes float-based proportions referencing the parent EditorCanvas heavily. """
        p = self.parent()
        if not p or p.width() == 0 or p.height() == 0: return
        self._rel_x = self.x() / p.width()
        self._rel_y = self.y() / p.height()
        self._rel_w = self.width() / p.width()
        self._rel_h = self.height() / p.height()

    def set_edit_mode(self, enabled):
        """
        Locks or unlocks the widget for the user. 
        In Edit Mode (True): UI captures transparent mouse events for drag/drop.
        In Run Mode (False): User interacts with the UI normally.
        """
        self.is_edit_mode = enabled
        for child in self.findChildren(QWidget):
            if child is not self:
                # Disables pointer events on inner items so the Base can be clicked and dragged
                child.setAttribute(Qt.WA_TransparentForMouseEvents, enabled)
                child.setFocusPolicy(Qt.NoFocus if enabled else Qt.StrongFocus)

    def mousePressEvent(self, event):
        """ Captures the exact initial click location to allow smooth drag-and-drop. """
        if self.is_edit_mode and event.button() == Qt.LeftButton:
            self._drag_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """ Modifies the widget's physical location or initiates a clone drag from the toolbar. """
        if self.is_edit_mode and self._drag_pos:
            # Check if this widget is sitting in the toolbar (it shouldn't move itself)
            if getattr(self, 'is_template', False):
                from PySide6.QtWidgets import QApplication
                # Make sure the user dragged far enough to count as a real drag
                if (event.pos() - self._drag_pos).manhattanLength() >= QApplication.startDragDistance():
                    from PySide6.QtGui import QDrag
                    from PySide6.QtCore import QMimeData
                    
                    drag = QDrag(self)
                    mime_data = QMimeData()
                    
                    # Pack the widget type so the Canvas knows exactly what to spawn on Drop
                    mime_data.setData("application/x-widget-template", self.comp_type.encode('utf-8'))
                    drag.setMimeData(mime_data)
                    
                    # MAGIC HAPPENS HERE: Take a visual snapshot (ghost image) that follows the mouse
                    drag.setPixmap(self.grab())
                    drag.setHotSpot(self._drag_pos)
                    
                    drag.exec(Qt.CopyAction)
            else:
                # Normal movement across the canvas for already-placed widgets
                self.move(self.mapToParent(event.pos() - self._drag_pos))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """ Clears the drag state once the user drops the widget precisely like Qt Designer. """
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
            self.update_relative_geometry() # Anchor the new location immediately
        super().mouseReleaseEvent(event)

    def add_base_actions(self, menu):
        """ Appends standard actions (Resize, Delete) to any widget's custom right-click menu. """
        menu.addSeparator()
        resize_act = menu.addAction("Resize")
        delete_act = menu.addAction("Delete")
        return resize_act, delete_act

    def handle_base_actions(self, action, res_act, del_act):
        """ Executes the logic for the standard resize and delete context actions. """
        if action == res_act:
            w, ok1 = QInputDialog.getInt(self, "Width", "Width:", self.width())
            h, ok2 = QInputDialog.getInt(self, "Height", "Height:", self.height())
            if ok1 and ok2: 
                self.resize(w, h)
                self.update_relative_geometry()
        elif action == del_act:
            self.deleteLater() # Safely destroys the widget and cleans up memory

    def to_dict(self):
        """ Serializes core widget properties into a Python dictionary for easy saving to config.json. """
        return {
            "comp_type": self.comp_type,
            "x": self.x(),
            "y": self.y(),
            "width": self.width(),
            "height": self.height(),
            "arg_order": self.arg_order,
            "properties": self.properties
        }

    def from_dict(self, data):
        """ Restores the widget's location, size, and custom properties from a JSON dictionary. """
        self.move(data.get("x", 0), data.get("y", 0))
        if "width" in data and "height" in data:
            self.resize(data["width"], data["height"])
        self.arg_order = data.get("arg_order", 0)
        self.properties = data.get("properties", {})
        
        # Schedule geometric scale mapping softly on load
        from PySide6.QtCore import QTimer
        QTimer.singleShot(200, self.update_relative_geometry)
