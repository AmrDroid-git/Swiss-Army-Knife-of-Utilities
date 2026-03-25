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
        
        # 1. Gather all inputs
        inputs = [s for s in siblings if hasattr(s, 'mode') and s.mode == 'input']
        inputs.sort(key=lambda x: x.arg_order)
        args = [i.get_value() for i in inputs]

        # 2. Gather outputs
        text_outputs = [s for s in siblings if hasattr(s, 'mode') and s.mode == 'output' and getattr(s, 'field_type', '') == 'text_field']
        file_outputs = [s for s in siblings if hasattr(s, 'mode') and s.mode == 'output' and getattr(s, 'field_type', '') in ['file_field', 'folder_field']]

        # 3. Setup paths
        script_dir = os.path.dirname(self.script_path)
        script_name = os.path.basename(self.script_path)
        
        files_outputs_dir = os.path.join(script_dir, "files_outputs")
        os.makedirs(files_outputs_dir, exist_ok=True)

        # 4. TAKE SNAPSHOT BEFORE RUNNING
        before_files = set(os.listdir(script_dir))

        try:
            # 5. Run the script with UTF-8 Environment
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            res = subprocess.check_output(
                [sys.executable, script_name] + args, 
                text=True,
                encoding='utf-8', 
                stderr=subprocess.STDOUT,
                cwd=script_dir,
                env=env
            )
            
            # 6. Send string output to Text Fields
            for o in text_outputs: 
                o.set_value(res.strip())

            # 7. TAKE SNAPSHOT AFTER RUNNING & FIND NEW FILES
            after_files = set(os.listdir(script_dir))
            new_items = after_files - before_files

            # Figure out where these new files should go
            final_dest = files_outputs_dir
            if file_outputs and file_outputs[0].get_value():
                user_chosen_dir = file_outputs[0].get_value()
                if os.path.isdir(user_chosen_dir):
                    final_dest = user_chosen_dir

            # 8. MOVE THE NEW FILES
            if new_items:
                for item in new_items:
                    # Don't accidentally move the files_outputs folder itself
                    if item == "files_outputs": continue 
                    
                    src_path = os.path.join(script_dir, item)
                    dst_path = os.path.join(final_dest, item)
                    
                    # shutil.move works for both files and whole directories
                    shutil.move(src_path, dst_path)
                    
                # print(f"Moved {len(new_items)} new items to {final_dest}")
            else:
                print("No new files were generated.")
                
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Script Crashed (Exit Code {e.returncode})!")
            print(f"--- SCRIPT ERROR LOG ---\n{e.output}\n------------------------\n")
            
            # This throws the exact error into your UI text box so you can read it!
            for o in text_outputs: 
                o.set_value(f"CRASH: {e.output.strip()}")
                
        except Exception as e:
            print(f"System Error: {e}")