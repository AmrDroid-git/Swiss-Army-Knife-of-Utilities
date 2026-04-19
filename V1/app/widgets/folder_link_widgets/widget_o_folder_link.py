from PySide6.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QMenu, QFileDialog
from PySide6.QtCore import Qt
from app.widgets.base_widget import BaseComponent
from app.translator import t

class WidgetOFolderLink(BaseComponent):
    """
    Provides an interface to select a master output directory for script operations.
    Acts identically to an Output-File link.
    """
    def __init__(self, parent, pos):
        super().__init__(parent, "widget_o_folder_link", pos)
        self.field_type = "folder_field"
        self.mode = "output"
        
        self.resize(220, 45)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.entry = QLineEdit()
        self.entry.setPlaceholderText(t("output_folder"))
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
        self.entry.setFont(font)

    def browse(self):
        if self.is_edit_mode: return
        path = QFileDialog.getExistingDirectory(self, t("select_output_folder_dialog"))
        if path: self.entry.setText(path)

    def get_value(self): return self.entry.text()
    def set_value(self, val): self.entry.setText(val)
