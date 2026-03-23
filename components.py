import subprocess
import os
import shutil
from PySide6.QtWidgets import (QPushButton, QLineEdit, QLabel, QWidget, 
                               QHBoxLayout, QMenu, QFileDialog, QInputDialog, QMessageBox)
from PySide6.QtCore import Qt, QPoint

class BaseComponent(QWidget):
    def __init__(self, parent, comp_type, pos=QPoint(0,0)):
        super().__init__(parent)
        self.comp_type = comp_type
        self.is_edit_mode = True
        self.arg_order = 0
        self.move(pos)
        self._drag_pos = None
        self.show()

    def set_edit_mode(self, enabled):
        self.is_edit_mode = enabled

    def mousePressEvent(self, event):
        if self.is_edit_mode and event.button() == Qt.LeftButton:
            self._drag_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_edit_mode and self._drag_pos:
            self.move(self.mapToParent(event.pos() - self._drag_pos))
        super().mouseMoveEvent(event)

    def add_base_actions(self, menu):
        menu.addSeparator()
        resize_act = menu.addAction("Resize")
        delete_act = menu.addAction("Delete")
        return resize_act, delete_act

    def handle_base_actions(self, action, res_act, del_act):
        if action == res_act:
            w, ok1 = QInputDialog.getInt(self, "Width", "Width:", self.width())
            h, ok2 = QInputDialog.getInt(self, "Height", "Height:", self.height())
            if ok1 and ok2: self.setFixedSize(w, h)
        elif action == del_act:
            self.deleteLater()

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
        # 1. Ask user for the source folder
        src_dir = QFileDialog.getExistingDirectory(self, "Select Source Folder containing main.py")
        if not src_dir: return

        if not os.path.exists(os.path.join(src_dir, "main.py")):
            QMessageBox.warning(self, "Error", "Selected folder must contain a main.py file!")
            return

        # 2. Identify target project directory
        # The Window object is the parent of the Canvas, and Canvas is the parent of this button
        window_name = self.window().window_id 
        safe_btn_name = self.btn.text().replace(" ", "_")
        
        dest_dir = os.path.join("projects", window_name, "scripts", safe_btn_name)

        # 3. Copy the folder
        try:
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir) # Clear old version if exists
            
            os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
            shutil.copytree(src_dir, dest_dir)
            
            # 4. Update the path to point to our LOCAL copy
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
            # We run the script from our INTERNAL projects folder
            res = subprocess.check_output(["python", self.script_path] + args, text=True, stderr=subprocess.STDOUT)
            outputs = [s for s in siblings if hasattr(s, 'mode') and s.mode == 'output']
            for o in outputs: o.set_value(res)
        except Exception as e:
            print(f"Execution Error: {e}")

class CustomField(BaseComponent):
    def __init__(self, parent, pos, field_type):
        super().__init__(parent, field_type, pos)
        self.setFixedSize(220, 45)
        self.mode = "input"
        self.layout = QHBoxLayout(self)
        self.entry = QLineEdit()
        self.layout.addWidget(self.entry)
        
        if field_type == "file_field":
            self.browse_btn = QPushButton("...")
            self.browse_btn.setFixedWidth(30)
            self.browse_btn.clicked.connect(self.browse)
            self.layout.addWidget(self.browse_btn)

    def contextMenuEvent(self, event):
        if not self.is_edit_mode: return
        menu = QMenu(self)
        mode_act = menu.addAction(f"Switch to {'OUTPUT' if self.mode == 'input' else 'INPUT'}")
        order_act = menu.addAction(f"Set Arg Order ({self.arg_order})")
        res_act, del_act = self.add_base_actions(menu)
        
        action = menu.exec(event.globalPos())
        if action == mode_act:
            self.mode = "output" if self.mode == "input" else "input"
            self.entry.setReadOnly(self.mode == "output")
            self.entry.setPlaceholderText(f"MODE: {self.mode.upper()}")
        elif action == order_act:
            val, ok = QInputDialog.getInt(self, "Order", "Arg Index:", self.arg_order, 0, 100)
            if ok: self.arg_order = val
        self.handle_base_actions(action, res_act, del_act)

    def browse(self):
        if self.is_edit_mode: return
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path: self.entry.setText(path)

    def get_value(self): return self.entry.text()
    def set_value(self, val): self.entry.setText(val)

class DraggableLabel(BaseComponent):
    def __init__(self, parent, pos, text="Text Label"):
        super().__init__(parent, "label", pos)
        self.layout = QHBoxLayout(self)
        self.lbl = QLabel(text)
        self.layout.addWidget(self.lbl)

    def contextMenuEvent(self, event):
        if not self.is_edit_mode: return
        menu = QMenu(self)
        edit_act = menu.addAction("Edit Text")
        res_act, del_act = self.add_base_actions(menu)
        action = menu.exec(event.globalPos())
        if action == edit_act:
            t, ok = QInputDialog.getText(self, "Edit", "Text:", text=self.lbl.text())
            if ok: self.lbl.setText(t)
        self.handle_base_actions(action, res_act, del_act)