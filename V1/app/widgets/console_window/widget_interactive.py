from PySide6.QtWidgets import QPlainTextEdit, QLineEdit, QVBoxLayout, QMenu
from PySide6.QtCore import Qt, Signal
from app.widgets.base_widget import BaseComponent
from app.translator import t

class WidgetInteractiveConsole(BaseComponent):
    """
    Acts as an interactive system terminal.
    Displays output but also captures user keyboard input and pipes it via STDIN into running python processes.
    """
    
    # Custom signal to send data directly up to the Script Engine natively
    stdin_submitted = Signal(str)

    def __init__(self, parent, pos):
        super().__init__(parent, "widget_interactive_console", pos)
        self.resize(400, 250)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0) # Keep input attached directly to output visually without gaps
        self.layout.setContentsMargins(0,0,0,0)
        
        # Output Terminal Screen
        self.console_output = QPlainTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("background-color: #1e1e1e; color: #00FF00; border: none; padding: 5px;")
        self.layout.addWidget(self.console_output)
        
        # User Input Bar (STDIN)
        self.console_input = QLineEdit()
        self.console_input.setPlaceholderText(t("console_input_placeholder"))
        self.console_input.setStyleSheet("background-color: #2d2d2d; color: white; border: 1px solid #555; padding: 5px;")
        
        # When user presses Enter, broadcast the text
        self.console_input.returnPressed.connect(self.submit_input)
        self.layout.addWidget(self.console_input)

    def contextMenuEvent(self, event):
        if not self.is_edit_mode:
            menu = QMenu(self)
            clear_act = menu.addAction(t("clear_console"))
            if menu.exec(event.globalPos()) == clear_act:
                self.clear_text()
            return
            
        menu = QMenu(self)
        font_act, res_act, del_act = self.add_base_actions(menu)
        action = menu.exec(event.globalPos())
        self.handle_base_actions(action, font_act, res_act, del_act)

    def apply_font(self, font):
        self.console_output.setFont(font)
        self.console_input.setFont(font)

    def append_text(self, text):
        """ Appends strings physically returning from the running python script. """
        self.console_output.appendPlainText(text)
        
    def clear_text(self):
        self.console_output.clear()
        
    def submit_input(self):
        """ Fires natively when Enter is pressed in the QLineEdit. """
        if self.is_edit_mode: return # Disable interacting securely during UI design phase
        
        user_text = self.console_input.text()
        
        # Echo standard input locally in bold white so user knows what they visually typed
        self.console_output.appendPlainText(f"> {user_text}")
        
        # Send raw string to engine async
        self.stdin_submitted.emit(user_text)
        
        # Flush the physical input bar to visually reset
        self.console_input.clear()
