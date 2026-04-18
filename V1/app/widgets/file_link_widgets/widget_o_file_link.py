from PySide6.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QMenu, QFileDialog
from PySide6.QtCore import Qt
from app.widgets.base_widget import BaseComponent

class WidgetOFileLink(BaseComponent):
    """
    Specifies a destination folder location for any dynamically created output files.
    Python scripts will push generated files toward the folder defined by this output path.
    """
    def __init__(self, parent, pos):
        super().__init__(parent, "widget_o_file_link", pos)
        self.field_type = "file_field"
        
        # Read by button; instructs automation script where to deposit created items
        self.mode = "output" 
        
        self.resize(220, 45)
        self.layout = QHBoxLayout(self)
        
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("OUTPUT DIRECTORY")
        self.entry.setReadOnly(True)
        self.layout.addWidget(self.entry)
        
        self.browse_btn = QPushButton("...")
        self.browse_btn.setFixedWidth(30)
        self.browse_btn.clicked.connect(self.browse)
        self.layout.addWidget(self.browse_btn)

    def contextMenuEvent(self, event):
        if not self.is_edit_mode:
            menu = QMenu(self)
            clear_act = menu.addAction("Clear Content")
            if menu.exec(event.globalPos()) == clear_act:
                self.set_value("")
            return
            
        menu = QMenu(self)
        res_act, del_act = self.add_base_actions(menu)
        action = menu.exec(event.globalPos())
        self.handle_base_actions(action, res_act, del_act)

    def browse(self):
        """ Output needs a DIRECTORY, not a single file selection. """
        if self.is_edit_mode: return
        
        path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if path: self.entry.setText(path)

    def get_value(self): 
        """ Passed into script logic to define intended generated-file destination. """
        return self.entry.text()

    def set_value(self, val): 
        self.entry.setText(val)
