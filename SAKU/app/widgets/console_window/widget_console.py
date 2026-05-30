from PySide6.QtWidgets import QPlainTextEdit, QHBoxLayout, QMenu
from PySide6.QtCore import Qt
from app.widgets.base_widget import BaseComponent
from app.translator import t

class WidgetConsole(BaseComponent):
    """
    Acts as the default system terminal for a window.
    The script_engine.py routes standard output strings (STDOUT) to this widget.
    """
    def __init__(self, parent, pos):
        super().__init__(parent, "widget_console", pos)
        self.resize(400, 200)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Setting up a read-only terminal-like text box
        self.console_output = QPlainTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("background-color: black; color: #00FF00;")
        self.layout.addWidget(self.console_output)

    def contextMenuEvent(self, event):
        """ Adds standard deletion/resize functionality if right-clicked (NO font change option). """
        if not self.is_edit_mode:
            menu = QMenu(self)
            clear_act = menu.addAction(t("clear_console"))
            if menu.exec(event.globalPos()) == clear_act:
                self.clear_text()
            return
            
        menu = QMenu(self)
        # Add only resize and delete actions (NO font action for console)
        menu.addSeparator()
        res_act = menu.addAction(t("resize"))
        del_act = menu.addAction(t("delete"))
        
        action = menu.exec(event.globalPos())
        if action == res_act:
            self.enable_resize_mode()
        elif action == del_act:
            self.delete_widget()

    def apply_font(self, font):
        """
        For console output, only change font size, NOT font family.
        This preserves the console's appearance and background colors.
        """
        # Only apply font size, keep the original font family
        current_font = self.console_output.font()
        current_font.setPointSize(font.pointSize())
        self.console_output.setFont(current_font)
        # Use stylesheet ONLY for font-size with !important, no font-family
        self.console_output.setStyleSheet(f"QPlainTextEdit {{font-size: {font.pointSize()}pt !important;}}")

    def append_text(self, text):
        """ Helper method for script engine to pump python stdout into the UI. """
        self.console_output.appendPlainText(text)
        
    def clear_text(self):
        """ Clears existing output strings (usually when starting a new run). """
        self.console_output.clear()
