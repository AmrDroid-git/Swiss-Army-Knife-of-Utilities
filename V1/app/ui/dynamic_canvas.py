import os
from PySide6.QtWidgets import (QFrame, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox,
                               QScrollArea)
from PySide6.QtCore import Qt, QPoint
from app.widgets import (
    BaseComponent, WidgetButton, WidgetIText, WidgetOText,
    WidgetIFileLink, WidgetOFileLink, WidgetIFolderLink, WidgetOFolderLink,
    WidgetConsole, WidgetInteractiveConsole, WidgetLabel, WidgetRequirementsLink
)
from app.ui.edit_palette import ToolboxItem
from app.core import package_manager
from app.core.script_engine import ScriptEngine

class EditorCanvas(QFrame):
    def __init__(self, script_engine):
        super().__init__()
        self.setAcceptDrops(True)
        # Add basic grid line appearance for editing
        self.setStyleSheet("""
            background-color: #fdfdfd; 
            border: 2px dashed #bdc3c7; 
            border-radius: 8px;
        """)
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
            self.setStyleSheet("background-color: #ffffff; border: none; border-radius: 8px;")
        else:
            self.setStyleSheet("background-color: #eef2f3; border: 2px solid #bdc3c7; border-radius: 8px;")
            
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
            clear_act = menu.addAction("🧹 Clear All Fields & Console")
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
        self.resize(1100, 750)
        
        # Establishing Core Asynchronous Execution Engine
        self.engine = ScriptEngine()
        
        self.layout = QVBoxLayout(self)
        
        # Navbar / Header Interface
        nav = QHBoxLayout()
        self.edit_btn = QPushButton("✎ Design Mode")
        self.edit_btn.setCheckable(True)
        self.edit_btn.setStyleSheet("""
            QPushButton:checked { background-color: #e74c3c; color: white; border: none; padding: 10px; border-radius: 4px; font-weight: bold; }
            QPushButton { background-color: #2980b9; color: white; border: none; padding: 10px; border-radius: 4px; font-weight: bold; }
        """)
        self.edit_btn.clicked.connect(self.toggle)
        
        save_btn = QPushButton("💾 SAVE PROJECT")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; border: none; padding: 10px; border-radius: 4px; font-weight: bold;")
        save_btn.clicked.connect(lambda: package_manager.save_window(self.window_id, self.canvas))
        
        nav.addWidget(QLabel(f"<h2 style='margin:0; color:#2c3e50;'>{window_id.replace('_',' ').upper()}</h2>"))
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
        self.sidebar_container.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                background-color: #f0f0f0;
            }
        """)
        
        self.sidebar = QWidget()
        self.sidebar_container.setWidget(self.sidebar)
        
        s_lay = QVBoxLayout(self.sidebar)
        s_lay.setSpacing(4)
        s_lay.setContentsMargins(4, 4, 4, 4)
        
        s_lay.addWidget(ToolboxItem("🎯 Script Trigger", "widget_button"))
        s_lay.addWidget(ToolboxItem("🏷️ Title/Label", "widget_label"))
        s_lay.addWidget(ToolboxItem("📝 Text Input", "widget_i_text"))
        s_lay.addWidget(ToolboxItem("📟 Text Output", "widget_o_text"))
        s_lay.addWidget(ToolboxItem("📄 File Input", "widget_i_file_link"))
        s_lay.addWidget(ToolboxItem("📂 Folder Input", "widget_i_folder_link"))
        s_lay.addWidget(ToolboxItem("📦 Safe Output Target", "widget_o_folder_link"))
        s_lay.addWidget(ToolboxItem("🖥️ System Console", "widget_console"))
        s_lay.addWidget(ToolboxItem("⌨️ Interactive Console", "widget_interactive_console"))
        s_lay.addWidget(ToolboxItem("ⓘ Requirements Link", "widget_requirements_link"))
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
        package_manager.save_window(self.window_id, self.canvas)
        event.accept()
