import os
import shutil
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QMenu, QFileDialog, QInputDialog, QMessageBox
from PySide6.QtCore import Qt, Signal
from app.widgets.base_widget import BaseComponent

class WidgetButton(BaseComponent):
    """
    The main execution trigger for the canvas. 
    It finds inputs, sorts them by arg_order, and tells the script_engine to execute!
    """

    # Emit signal to delegate execution to script_engine.py per architecture rules.
    # We DO NOT freeze the UI with subprocess here anymore.
    run_script_requested = Signal(str, list, list)

    def __init__(self, parent, pos, label="Run Script"):
        super().__init__(parent, "widget_button", pos)
        self.resize(130, 50)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Inner button visual
        self.btn = QPushButton(label)
        self.layout.addWidget(self.btn)
        
        self.script_path = "" # Points to the python file imported for this specific button
        self.btn.clicked.connect(self.execute)

    def contextMenuEvent(self, event):
        """ The right-click menu tailored for the Button (Edit Mode only). """
        if not self.is_edit_mode: return
        menu = QMenu(self)
        
        rename_act = menu.addAction("Rename Button")
        link_act = menu.addAction("Import & Link Script Folder")
        
        # Append the standard parent actions (Resize, Delete)
        font_act, res_act, del_act = self.add_base_actions(menu)
        
        action = menu.exec(event.globalPos())
        
        if action == rename_act:
            t, ok = QInputDialog.getText(self, "Rename", "Text:", text=self.btn.text())
            if ok: self.btn.setText(t)
        elif action == link_act:
            self.import_script_folder()
            
        self.handle_base_actions(action, font_act, res_act, del_act)

    def apply_font(self, font):
        self.btn.setFont(font)

    def import_script_folder(self):
        """ 
        Allows the user to select an external folder. The system will copy it into 
        the window's saved 'scripts' folder, tying it directly to this button.
        """
        src_dir = QFileDialog.getExistingDirectory(self, "Select Source Folder containing main.py")
        if not src_dir: return

        if not os.path.exists(os.path.join(src_dir, "main.py")):
            QMessageBox.warning(self, "Error", "Selected folder must contain a main.py file!")
            return

        # Figure out our bundle name so we can save the script neatly structured
        window_name = getattr(self.window(), "window_id", "default_window") 
        safe_btn_name = self.btn.text().replace(" ", "_")
        
        # Save scripts natively inside the core workspace window
        dest_dir = os.path.join("user_workspaces", window_name, "scripts", safe_btn_name)

        try:
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir) # Overwrite if we are re-linking the script
            
            os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
            shutil.copytree(src_dir, dest_dir)
            
            self.script_path = os.path.join(dest_dir, "main.py")
            QMessageBox.information(self, "Success", f"Folder imported to: {dest_dir}")
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", f"Could not copy folder: {e}")

    def execute(self):
        """
        Triggered when clicked in RUN MODE.
        Scans all siblings (other widgets on the canvas) to scrape input values,
        sorts them, and sends them out to the Script Engine execution layer via Signal.
        """
        if self.is_edit_mode or not self.script_path: return
        
        siblings = self.parent().findChildren(BaseComponent)
        
        # 1. Gather all inputs (Scan for any widget claiming to be 'input')
        inputs = [s for s in siblings if hasattr(s, 'mode') and s.mode == 'input']
        
        # Sort them numerically so the arguments match the python sys.argv[] positions
        inputs.sort(key=lambda x: x.arg_order)
        
        # 2. Gather outputs (Widgets designed to display the result or accept output files)
        outputs = [s for s in siblings if hasattr(s, 'mode') and s.mode == 'output']
        
        # Fire signal upwards for async execution
        self.run_script_requested.emit(self.script_path, inputs, outputs)

    def to_dict(self):
        """ Appends button specific attributes to the BaseComponent JSON format. """
        data = super().to_dict()
        data["label"] = self.btn.text()
        data["script_path"] = self.script_path
        return data

    def from_dict(self, data):
        """ Restores button specific attributes from JSON load. """
        super().from_dict(data)
        self.btn.setText(data.get("label", "Run Script"))
        
        # Dynamically reconstruct path to protect against the user renaming the workspace upon import
        if data.get("script_path"):
            window_name = getattr(self.window(), "window_id", "default_window") 
            safe_btn_name = self.btn.text().replace(" ", "_")
            self.script_path = os.path.join("user_workspaces", window_name, "scripts", safe_btn_name, "main.py")
        else:
            self.script_path = ""
