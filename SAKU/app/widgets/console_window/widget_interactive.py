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
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        # Output Terminal Screen
        self.console_output = QPlainTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet(
            "QPlainTextEdit { "
            "background-color: #050505; "
            "color: #00FF00; "
            "border: 1px solid #6b7280; "
            "border-radius: 4px; "
            "padding: 6px; "
            "}"
        )
        self.layout.addWidget(self.console_output)
        
        # User Input Bar (STDIN)
        self.console_input = QLineEdit()
        self.console_input.setPlaceholderText(t("console_input_placeholder"))
        self.console_input.setStyleSheet(
            "QLineEdit { "
            "background-color: #111827; "
            "color: white; "
            "border: 1px solid #6b7280; "
            "border-radius: 4px; "
            "padding: 6px; "
            "}"
        )
        
        # When user presses Enter, broadcast the text
        self.console_input.returnPressed.connect(self.submit_input)
        self.layout.addWidget(self.console_input)

    def contextMenuEvent(self, event):
        """Adds clear in run mode, and shared resize/delete actions in edit mode."""
        if not self.is_edit_mode:
            menu = QMenu(self)
            clear_act = menu.addAction(t("clear_console"))
            if menu.exec(event.globalPos()) == clear_act:
                self.clear_text()
            return

        menu = QMenu(self)

        font_act, res_act, del_act = self.add_base_actions(menu, include_font=False)

        action = menu.exec(event.globalPos())
        self.handle_base_actions(action, font_act, res_act, del_act)

    def apply_font(self, font):
        """
        For interactive console, only change font size, NOT font family.
        This preserves the console's appearance and background colors.
        """
        # Only apply font size to output, keep the original font family
        output_font = self.console_output.font()
        output_font.setPointSize(font.pointSize())
        self.console_output.setFont(output_font)
        
        # Only apply font size to input, keep the original font family
        input_font = self.console_input.font()
        input_font.setPointSize(font.pointSize())
        self.console_input.setFont(input_font)
        
        # Keep the visible console border/background while changing the size.
        self.console_output.setStyleSheet(
            f"QPlainTextEdit {{ "
            f"background-color: #050505; "
            f"color: #00FF00; "
            f"border: 1px solid #6b7280; "
            f"border-radius: 4px; "
            f"padding: 6px; "
            f"font-size: {font.pointSize()}pt; "
            f"}}"
        )
        self.console_input.setStyleSheet(
            f"QLineEdit {{ "
            f"background-color: #111827; "
            f"color: white; "
            f"border: 1px solid #6b7280; "
            f"border-radius: 4px; "
            f"padding: 6px; "
            f"font-size: {font.pointSize()}pt; "
            f"}}"
        )

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
