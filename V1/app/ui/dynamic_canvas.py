import os
from PySide6.QtWidgets import (QFrame, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox,
                               QScrollArea, QApplication)
from PySide6.QtCore import Qt, QPoint
from app.widgets import (
    BaseComponent, WidgetButton, WidgetIText, WidgetOText,
    WidgetIFileLink, WidgetOFileLink, WidgetIFolderLink, WidgetOFolderLink,
    WidgetConsole, WidgetInteractiveConsole, WidgetLabel, WidgetRequirementsLink,
    WidgetSelect
)
from app.ui.edit_palette import ToolboxItem
from app.core import package_manager
from app.core.script_engine import ScriptEngine
from app.translator import t

class EditorCanvas(QFrame):
    def __init__(self, script_engine):
        super().__init__()
        self.setAcceptDrops(True)
        # Add basic grid line appearance for editing
        # Let the theme stylesheet handle the canvas background
        self.setStyleSheet("EditorCanvas { border: 2px dashed #9ca3af; border-radius: 8px; }")
        self.is_edit_mode = False
        self.script_engine = script_engine
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        cur_w = event.size().width()
        cur_h = event.size().height()
        if cur_w == 0 or cur_h == 0: return
        
        # Iterates across all active components proportionally mirroring the main window space
        for c in self.findChildren(BaseComponent):
            if hasattr(c, '_rel_x') and c._rel_w > 0:
                new_x = int(c._rel_x * cur_w)
                new_y = int(c._rel_y * cur_h)
                new_w = int(c._rel_w * cur_w)
                new_h = int(c._rel_h * cur_h)
                
                # Enforce minimum constraints so the UI never breaks into microscopic sizes
                new_w = max(40, new_w)
                new_h = max(20, new_h)
                
                c.setGeometry(new_x, new_y, new_w, new_h)
        
    def set_edit_mode(self, state):
        self.is_edit_mode = state
        if state:
            self.setStyleSheet("EditorCanvas { border: 2px dashed #6366f1; border-radius: 8px; }")
        else:
            # Reset canvas cursor when exiting edit mode
            from PySide6.QtCore import Qt
            self.setCursor(Qt.ArrowCursor)
            self.setStyleSheet("EditorCanvas { border: 2px dashed #9ca3af; border-radius: 8px; }")
            
        for c in self.findChildren(BaseComponent): 
            c.set_edit_mode(state)

    def dragEnterEvent(self, event):
        """ Allows dropping if the MIME format matches our proprietary builder standard """
        if self.is_edit_mode and event.mimeData().hasFormat("application/x-widget-template"): 
            event.acceptProposedAction()

    def contextMenuEvent(self, event):
        """ Right clicking the empty canvas safely zeroes out all output and input fields """
        if not self.is_edit_mode:
            from PySide6.QtWidgets import QMenu
            menu = QMenu(self)
            clear_act = menu.addAction(t("clear_all_fields"))
            if menu.exec(event.globalPos()) == clear_act:
                for c in self.findChildren(BaseComponent):
                    if hasattr(c, 'clear_text'): c.clear_text()
                    elif hasattr(c, 'set_value'): c.set_value("")

    def dropEvent(self, event):
        if not self.is_edit_mode: return
        pos = event.position().toPoint()
        
        # Read the widget type sent by base_widget ghost-clones OR ToolboxItem clones
        item_data = event.mimeData().data("application/x-widget-template")
        tid = bytes(item_data).decode('utf-8')
        
        obj = None
        if tid == "widget_button": 
            obj = WidgetButton(self, pos)
            # Link the new button immediately to the central window script engine!
            obj.run_script_requested.connect(self.script_engine.run_script)
        elif tid == "widget_label": obj = WidgetLabel(self, pos)
        elif tid == "widget_i_text": obj = WidgetIText(self, pos)
        elif tid == "widget_o_text": obj = WidgetOText(self, pos)
        elif tid == "widget_select": obj = WidgetSelect(self, pos)
        elif tid == "widget_i_file_link": obj = WidgetIFileLink(self, pos)
        elif tid == "widget_o_file_link": obj = WidgetOFileLink(self, pos)
        elif tid == "widget_i_folder_link": obj = WidgetIFolderLink(self, pos)
        elif tid == "widget_o_folder_link": obj = WidgetOFolderLink(self, pos)
        elif tid == "widget_console": 
            obj = WidgetConsole(self, pos)
            self.script_engine.stdout_emitted.connect(obj.append_text)
            self.script_engine.error_emitted.connect(obj.append_text)
        elif tid == "widget_interactive_console": 
            obj = WidgetInteractiveConsole(self, pos)
            self.script_engine.stdout_emitted.connect(obj.append_text)
            self.script_engine.error_emitted.connect(obj.append_text)
            obj.stdin_submitted.connect(self.script_engine.send_input)
        elif tid == "widget_requirements_link": 
            obj = WidgetRequirementsLink(self, pos)

        if obj:
            obj.is_template = False
            obj.set_edit_mode(True)
            obj.show()
            
            # Immediately record the floating-point scale matrix based exactly on where it was dropped
            from PySide6.QtCore import QTimer
            QTimer.singleShot(50, obj.update_relative_geometry)
            event.acceptProposedAction()


class CustomWindow(QWidget):
    """ The primary wrapper containing the Canvas, Toolbar, and Script Engine for one specific Project. """
    def __init__(self, window_id):
        super().__init__()
        self.window_id = window_id
        self.setWindowTitle(f"Project Workspace: {window_id.replace('_',' ')}")
        
        # Calculate 70% of screen size for the window
        screen = QApplication.primaryScreen().geometry()
        window_width = int(screen.width() * 0.7)
        window_height = int(screen.height() * 0.7)
        
        # Resize window to 70% of screen
        self.resize(window_width, window_height)
        
        # Center window on screen
        center_x = (screen.width() - window_width) // 2
        center_y = (screen.height() - window_height) // 2
        self.move(center_x, center_y)
        
        # Theme comes from the application-level stylesheet applied in main.py — no override needed here.
        
        # Establishing Core Asynchronous Execution Engine
        self.engine = ScriptEngine()
        
        self.layout = QVBoxLayout(self)
        
        # Navbar / Header Interface
        nav = QHBoxLayout()
        self.edit_btn = QPushButton(t("design_mode"))
        self.edit_btn.setCheckable(True)
        self.edit_btn.clicked.connect(self.toggle)
        
        save_btn = QPushButton(t("save_project"))
        save_btn.clicked.connect(lambda: package_manager.save_window(self.window_id, self.canvas))
        
        title_label = QLabel(window_id.replace('_', ' ').upper())
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 4px 0px;")
        nav.addWidget(title_label)
        nav.addStretch()
        nav.addWidget(self.edit_btn)
        nav.addWidget(save_btn)
        self.layout.addLayout(nav)

        # Content Layer (Canvas + Toolbar)
        self.content = QHBoxLayout()
        self.canvas = EditorCanvas(self.engine)
        
        # Create scrollable sidebar for edit palette
        self.sidebar_container = QScrollArea()
        self.sidebar_container.setWidgetResizable(True)
        self.sidebar_container.setMinimumWidth(200)
        self.sidebar_container.setMaximumWidth(250)
        # Sidebar inherits theme from application stylesheet
        
        self.sidebar = QWidget()
        self.sidebar_container.setWidget(self.sidebar)
        
        s_lay = QVBoxLayout(self.sidebar)
        s_lay.setSpacing(4)
        s_lay.setContentsMargins(4, 4, 4, 4)
        
        s_lay.addWidget(ToolboxItem(t("script_trigger"), "widget_button"))
        s_lay.addWidget(ToolboxItem(t("title_label"), "widget_label"))
        s_lay.addWidget(ToolboxItem(t("text_input"), "widget_i_text"))
        s_lay.addWidget(ToolboxItem(t("text_output"), "widget_o_text"))
        s_lay.addWidget(ToolboxItem(t("select_field"), "widget_select"))
        s_lay.addWidget(ToolboxItem(t("file_input"), "widget_i_file_link"))
        s_lay.addWidget(ToolboxItem(t("folder_input"), "widget_i_folder_link"))
        s_lay.addWidget(ToolboxItem(t("safe_output"), "widget_o_folder_link"))
        s_lay.addWidget(ToolboxItem(t("system_console"), "widget_console"))
        s_lay.addWidget(ToolboxItem(t("interactive_console"), "widget_interactive_console"))
        s_lay.addWidget(ToolboxItem(t("requirements_link"), "widget_requirements_link"))
        s_lay.addStretch()
        
        self.content.addWidget(self.canvas)
        self.content.addWidget(self.sidebar_container)
        self.layout.addLayout(self.content)
        
        # Hide toolbar by default to enforce "Run Mode" execution experience
        self.sidebar_container.hide()
        
        # Hydrate canvas from saved config json automatically
        package_manager.load_window(self.window_id, self.canvas)
        self._reconnect_loaded_widgets()

    def _reconnect_loaded_widgets(self):
        """ Hard-links restored widgets heavily back to the native Qt C++ signal logic layer """
        for c in self.canvas.findChildren(BaseComponent):
            if isinstance(c, WidgetButton):
                c.run_script_requested.connect(self.engine.run_script)
            elif isinstance(c, WidgetConsole):
                self.engine.stdout_emitted.connect(c.append_text)
                self.engine.error_emitted.connect(c.append_text)
            elif isinstance(c, WidgetInteractiveConsole):
                self.engine.stdout_emitted.connect(c.append_text)
                self.engine.error_emitted.connect(c.append_text)
                c.stdin_submitted.connect(self.engine.send_input)

    def toggle(self):
        state = self.edit_btn.isChecked()
        self.canvas.set_edit_mode(state)
        self.sidebar_container.setVisible(state)

    def closeEvent(self, event):
        # Kill any running process before closing to prevent QProcess orphan warning
        self.engine.kill()
        package_manager.save_window(self.window_id, self.canvas)
        event.accept()
