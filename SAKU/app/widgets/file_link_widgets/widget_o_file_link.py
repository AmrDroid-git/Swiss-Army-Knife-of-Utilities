from PySide6.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QMenu, QFileDialog
from PySide6.QtCore import Qt
from app.widgets.base_widget import BaseComponent
from app.translator import t

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
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.entry = QLineEdit()
        self.entry.setPlaceholderText(t("output_directory"))
        self.entry.setReadOnly(True)
        self.layout.addWidget(self.entry)
        
        self.browse_btn = QPushButton(t("browse_button"))
        self.browse_btn.setFixedWidth(30)
        self.browse_btn.clicked.connect(self.browse)
        self.layout.addWidget(self.browse_btn)

    def contextMenuEvent(self, event):
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
        font_str = f"{font.family()}, Arial, sans-serif"
        self.entry.setFont(font)
        self.entry.setStyleSheet(f"QLineEdit {{font-family: '{font_str}'; font-size: {font.pointSize()}pt !important;}}")

    def browse(self):
        """ Output needs a DIRECTORY, not a single file selection. """
        if self.is_edit_mode: return
        
        path = QFileDialog.getExistingDirectory(self, t("select_output_folder_dialog"))
        if path: self.entry.setText(path)

    def get_value(self): 
        """ Passed into script logic to define intended generated-file destination. """
        return self.entry.text()

    def set_value(self, val): 
        self.entry.setText(val)
