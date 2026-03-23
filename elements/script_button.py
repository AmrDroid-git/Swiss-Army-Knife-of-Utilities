import subprocess
import os
import shutil
import sys
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QMenu, QFileDialog, QInputDialog, QMessageBox
from .base import BaseComponent

class ScriptButton(BaseComponent):
    def __init__(self, parent, pos, label="Run Script"):
        super().__init__(parent, "script_button", pos)
        self.setFixedSize(130, 50)
        self.layout = QHBoxLayout(self)
        self.btn = QPushButton(label)
        self.layout.addWidget(self.btn)
        self.script_path = ""
        self.btn.clicked.connect(self.execute)

    def contextMenuEvent(self, event):
        if not self.is_edit_mode: return
        menu = QMenu(self)
        rename_act = menu.addAction("Rename Button")
        link_act = menu.addAction("Import & Link Script Folder")
        res_act, del_act = self.add_base_actions(menu)
        
        action = menu.exec(event.globalPos())
        
        if action == rename_act:
            t, ok = QInputDialog.getText(self, "Rename", "Text:", text=self.btn.text())
            if ok: self.btn.setText(t)
            
        elif action == link_act:
            self.import_script_folder()
            
        self.handle_base_actions(action, res_act, del_act)

    def import_script_folder(self):
        src_dir = QFileDialog.getExistingDirectory(self, "Select Source Folder containing main.py")
        if not src_dir: return

        if not os.path.exists(os.path.join(src_dir, "main.py")):
            QMessageBox.warning(self, "Error", "Selected folder must contain a main.py file!")
            return

        window_name = self.window().window_id 
        safe_btn_name = self.btn.text().replace(" ", "_")
        
        dest_dir = os.path.join("projects", window_name, "scripts", safe_btn_name)

        try:
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir) 
            
            os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
            shutil.copytree(src_dir, dest_dir)
            
            self.script_path = os.path.join(dest_dir, "main.py")
            QMessageBox.information(self, "Success", f"Folder imported to: {dest_dir}")
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", f"Could not copy folder: {e}")

    def execute(self):
        if self.is_edit_mode or not self.script_path: return
        
        siblings = self.parent().findChildren(BaseComponent)
        inputs = [s for s in siblings if hasattr(s, 'mode') and s.mode == 'input']
        inputs.sort(key=lambda x: x.arg_order)
        args = [i.get_value() for i in inputs]

        try:
            res = subprocess.check_output([sys.executable, self.script_path] + args, text=True, stderr=subprocess.STDOUT)
            outputs = [s for s in siblings if hasattr(s, 'mode') and s.mode == 'output']
            for o in outputs: o.set_value(res)
        except Exception as e:
            print(f"Execution Error: {e}")