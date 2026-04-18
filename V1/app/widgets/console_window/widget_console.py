from PySide6.QtWidgets import QPlainTextEdit, QHBoxLayout, QMenu
from PySide6.QtCore import Qt
from app.widgets.base_widget import BaseComponent

class WidgetConsole(BaseComponent):
    """
    Acts as the default system terminal for a window.
    The script_engine.py routes standard output strings (STDOUT) to this widget.
    """
    def __init__(self, parent, pos):
        super().__init__(parent, "widget_console", pos)
        self.resize(400, 200)
        self.layout = QHBoxLayout(self)
        
        # Setting up a read-only terminal-like text box
        self.console_output = QPlainTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("background-color: black; color: #00FF00; font-family: Consolas, monospace;")
        self.layout.addWidget(self.console_output)

    def contextMenuEvent(self, event):
        """ Adds standard deletion/resize functionality if right-clicked. """
        if not self.is_edit_mode:
            menu = QMenu(self)
            clear_act = menu.addAction("Clear Console Output")
            if menu.exec(event.globalPos()) == clear_act:
                self.clear_text()
            return
            
        menu = QMenu(self)
        res_act, del_act = self.add_base_actions(menu)
        action = menu.exec(event.globalPos())
        self.handle_base_actions(action, res_act, del_act)

    def append_text(self, text):
        """ Helper method for script engine to pump python stdout into the UI. """
        self.console_output.appendPlainText(text)
        
    def clear_text(self):
        """ Clears existing output strings (usually when starting a new run). """
        self.console_output.clear()
