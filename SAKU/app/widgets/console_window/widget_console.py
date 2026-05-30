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
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        # Setting up a read-only terminal-like text box
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
        For console output, only change font size, NOT font family.
        This preserves the console's appearance and background colors.
        """
        # Only apply font size, keep the original font family
        current_font = self.console_output.font()
        current_font.setPointSize(font.pointSize())
        self.console_output.setFont(current_font)
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

    def append_text(self, text):
        """ Helper method for script engine to pump python stdout into the UI. """
        self.console_output.appendPlainText(text)
        
    def clear_text(self):
        """ Clears existing output strings (usually when starting a new run). """
        self.console_output.clear()
