from PySide6.QtWidgets import QWidget, QInputDialog
from PySide6.QtCore import Qt, QPoint
from app.translator import t

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
        
        self._resize_dir = None         # Tracking which edge is being dragged
        
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
        self.setMouseTracking(enabled) # Magic: Unlocks cursor tracking when no button is physically held
        
        # Reset cursor and drag/resize state when exiting edit mode
        if not enabled:
            self.setCursor(Qt.ArrowCursor)
            self._drag_pos = None
            self._resize_dir = None
        
        # Provide Word/PPT style visual bounding box outlines during Edit Mode
        if enabled:
            self.setAttribute(Qt.WA_StyledBackground, True)
            self.setStyleSheet("BaseComponent { border: 2px dashed #000000; border-radius: 4px; }")
        else:
            self.setStyleSheet("BaseComponent { border: none; }")
            
        for child in self.findChildren(QWidget):
            if child is not self:
                # Disables pointer events on inner items so the Base can be clicked and dragged
                child.setAttribute(Qt.WA_TransparentForMouseEvents, enabled)
                child.setFocusPolicy(Qt.NoFocus if enabled else Qt.StrongFocus)

    def mousePressEvent(self, event):
        """ Captures the exact initial click location to allow smooth drag-and-drop or start edge resizing. """
        if self.is_edit_mode and event.button() == Qt.LeftButton:
            margin = 8
            x = event.pos().x()
            y = event.pos().y()
            w = self.width()
            h = self.height()
            
            # Detect exactly which edge got grabbed (all 8 directions)
            self._resize_dir = None
            if x <= margin and y <= margin:
                self._resize_dir = 'nw'
            elif x >= w - margin and y <= margin:
                self._resize_dir = 'ne'
            elif x <= margin and y >= h - margin:
                self._resize_dir = 'sw'
            elif x >= w - margin and y >= h - margin:
                self._resize_dir = 'se'
            elif x <= margin:
                self._resize_dir = 'w'
            elif x >= w - margin:
                self._resize_dir = 'e'
            elif y <= margin:
                self._resize_dir = 'n'
            elif y >= h - margin:
                self._resize_dir = 's'
                
            # Only trigger move mode if we aren't perfectly on an edge
            if not self._resize_dir:
                self._drag_pos = event.pos()
            else:
                self._drag_pos = None
                
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """ Modifies the widget's physical location, dynamically scales boundaries, or swaps cursors intelligently. """
        if self.is_edit_mode:
            
            # 1. Provide visual feedback if we are just HOVERING without clicking
            if not getattr(self, '_drag_pos', None) and not getattr(self, '_resize_dir', None):
                margin = 8
                x = event.pos().x()
                y = event.pos().y()
                w = self.width()
                h = self.height()
                
                # Check zones and intelligently swap the OS cursor visually like Microsoft Word!
                if (x <= margin and y <= margin) or (x >= w - margin and y >= h - margin):
                    self.setCursor(Qt.SizeFDiagCursor)
                elif (x >= w - margin and y <= margin) or (x <= margin and y >= h - margin):
                    self.setCursor(Qt.SizeBDiagCursor)
                elif x <= margin or x >= w - margin:
                    self.setCursor(Qt.SizeHorCursor)
                elif y <= margin or y >= h - margin:
                    self.setCursor(Qt.SizeVerCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)
                    
            # 2. Resizing actively (Button Held!)
            elif getattr(self, '_resize_dir', None):
                new_x = self.x()
                new_y = self.y()
                new_w = self.width()
                new_h = self.height()
                pos = event.pos()
                
                if self._resize_dir == 'se':
                    new_w = max(40, pos.x())
                    new_h = max(20, pos.y())
                elif self._resize_dir == 'sw':
                    new_x = self.x() + pos.x()
                    new_w = max(40, self.width() - pos.x())
                    new_h = max(20, pos.y())
                elif self._resize_dir == 'ne':
                    new_y = self.y() + pos.y()
                    new_w = max(40, pos.x())
                    new_h = max(20, self.height() - pos.y())
                elif self._resize_dir == 'nw':
                    new_x = self.x() + pos.x()
                    new_y = self.y() + pos.y()
                    new_w = max(40, self.width() - pos.x())
                    new_h = max(20, self.height() - pos.y())
                elif self._resize_dir == 'e':
                    new_w = max(40, pos.x())
                elif self._resize_dir == 'w':
                    new_x = self.x() + pos.x()
                    new_w = max(40, self.width() - pos.x())
                elif self._resize_dir == 's':
                    new_h = max(20, pos.y())
                elif self._resize_dir == 'n':
                    new_y = self.y() + pos.y()
                    new_h = max(20, self.height() - pos.y())
                
                # Apply the organic geometry natively! The elements adapt inside seamlessly
                self.setGeometry(new_x, new_y, new_w, new_h)
                
            # 3. Moving actively (Button Held!)
            elif self._drag_pos:
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
            self._resize_dir = None
            self.setCursor(Qt.ArrowCursor)
            self.update_relative_geometry() # Anchor the new location securely via mathematical proportions instantly
        super().mouseReleaseEvent(event)

    def add_base_actions(self, menu):
        """ Appends standard actions (Resize, Delete, Font) to any widget's custom right-click menu. """
        menu.addSeparator()
        font_act = menu.addAction(t("change_font"))
        resize_act = menu.addAction(t("resize"))
        delete_act = menu.addAction(t("delete"))
        return font_act, resize_act, delete_act

    def handle_base_actions(self, action, font_act, res_act, del_act):
        """ Executes the logic for the precise standard resize, font styling, and delete context actions. """
        if action == font_act:
            from PySide6.QtWidgets import QFontDialog
            from PySide6.QtGui import QFont
            
            # Use current chosen widget font as default selection index
            current_font = self.font()
            if "custom_font" in self.properties:
                current_font.fromString(self.properties["custom_font"])
                
            ok, font = QFontDialog.getFont(current_font, self)
            if ok:
                # Save purely mathematical abstract font string representing size/family/weight
                self.properties["custom_font"] = font.toString()
                self.apply_font(font)
                
        elif action == res_act:
            w, ok1 = QInputDialog.getInt(self, t("width_dialog_title"), t("width_dialog_prompt"), self.width())
            h, ok2 = QInputDialog.getInt(self, t("height_dialog_title"), t("height_dialog_prompt"), self.height())
            if ok1 and ok2: 
                self.resize(w, h)
                self.update_relative_geometry()
        elif action == del_act:
            self.deleteLater() # Safely destroys the widget and cleans up memory

    def apply_font(self, font):
        """ Can be deeply overridden by specific UI widgets to hook onto child QText layers purely. """
        self.setFont(font)

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
        
        # Hydrate dynamic typography layers identically
        if "custom_font" in self.properties:
            from PySide6.QtGui import QFont
            f = QFont()
            f.fromString(self.properties["custom_font"])
            self.apply_font(f)
        
        # Schedule geometric scale mapping softly on load
        from PySide6.QtCore import QTimer
        QTimer.singleShot(200, self.update_relative_geometry)
