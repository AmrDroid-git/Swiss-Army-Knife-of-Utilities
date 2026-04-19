import os
import shutil
import platform
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QMenu, QFileDialog, QInputDialog, QMessageBox
from PySide6.QtCore import Qt, Signal
from app.widgets.base_widget import BaseComponent
from app.translator import t

class WidgetButton(BaseComponent):
    """
    The main execution trigger for the canvas. 
    It finds inputs, sorts them by arg_order, and tells the script_engine to execute!
    Supports Python, Java, C, and C++ scripts with compilation support.
    """

    # Emit signal to delegate execution to script_engine.py per architecture rules.
    # We DO NOT freeze the UI with subprocess here anymore.
    run_script_requested = Signal(str, list, list)
    compile_script_requested = Signal(str)  # Signal to compile a script

    def __init__(self, parent, pos, label="Run Script"):
        super().__init__(parent, "widget_button", pos)
        self.resize(130, 50)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Inner button visual
        self.btn = QPushButton(label)
        self.layout.addWidget(self.btn)
        
        self.script_path = ""  # Points to the script file (main.py, Main.java, Main.c, Main.cpp)
        self.script_type = ""  # Stores: 'python', 'java', 'c', 'cpp'
        self.is_compiled = False  # Tracks if compiled (only for C/C++/Java)
        self.script_folder_name = ""  # Stores the actual folder name (independent of button display name)
        self.btn.clicked.connect(self.execute)

    def contextMenuEvent(self, event):
        """ The right-click menu tailored for the Button (Edit Mode only). """
        if not self.is_edit_mode: return
        menu = QMenu(self)
        
        rename_act = menu.addAction(t("button_rename"))
        link_act = menu.addAction(t("import_link_script"))
        
        # Add Compile option ONLY if a script is linked AND it's a compiled language
        compile_act = None
        if self.script_path and self.script_type in ["java", "c", "cpp"]:
            menu.addSeparator()  # Visual separator before compile
            compile_act = menu.addAction(t("compile_script"))
        
        # Append the standard parent actions (Resize, Delete)
        font_act, res_act, del_act = self.add_base_actions(menu)
        
        action = menu.exec(event.globalPos())
        
        if action == rename_act:
            new_name, ok = QInputDialog.getText(self, t("rename_dialog_title"), t("rename_dialog_prompt"), text=self.btn.text())
            if ok and new_name:
                # If a script folder is linked, rename it on disk too
                if self.script_folder_name:
                    self.rename_script_folder(new_name)
                self.btn.setText(new_name)
        elif action == link_act:
            self.import_script_folder()
        elif compile_act and action == compile_act:
            # Only trigger compile if compile_act exists AND user actually clicked it (not cancelled)
            self.compile_script()
            
        self.handle_base_actions(action, font_act, res_act, del_act)

    def apply_font(self, font):
        self.btn.setFont(font)

    def rename_script_folder(self, new_button_name):
        """
        Rename the script folder on disk when button is renamed.
        Keeps the script linked even after button renaming.
        """
        if not self.script_folder_name:
            return
        
        window_name = getattr(self.window(), "window_id", "default_window")
        old_folder_path = os.path.join("user_workspaces", window_name, "scripts", self.script_folder_name)
        new_folder_name = new_button_name.replace(" ", "_")
        new_folder_path = os.path.join("user_workspaces", window_name, "scripts", new_folder_name)
        
        try:
            if os.path.exists(old_folder_path):
                # Rename the folder on disk
                if os.path.exists(new_folder_path):
                    shutil.rmtree(new_folder_path)  # Remove destination if it exists
                os.rename(old_folder_path, new_folder_path)
                
                # Update the stored folder name and script path
                self.script_folder_name = new_folder_name
                
                # Reconstruct script_path with new folder name
                if self.script_type == "python":
                    filename = "main.py"
                elif self.script_type == "java":
                    filename = "Main.java"
                elif self.script_type == "c":
                    filename = "Main.c"
                elif self.script_type == "cpp":
                    filename = "Main.cpp"
                else:
                    filename = "main.py"
                
                self.script_path = os.path.join(new_folder_path, filename)
        except Exception as e:
            QMessageBox.warning(self, t("error"), f"{t('could_not_rename_folder').format(e=e)}")

    def compile_script(self):
        """
        Compiles Java, C, or C++ scripts using the script engine's compile method.
        """
        if not self.script_path:
            QMessageBox.warning(self, t("error"), t("no_script_linked"))
            return
        
        if self.script_type == "python":
            QMessageBox.information(self, t("info"), t("python_no_compile"))
            return
        
        # Import here to avoid circular dependencies
        from app.core.script_engine import ScriptEngine
        
        engine = ScriptEngine()
        success, message = engine.compile_script(self.script_path)
        
        if success:
            self.is_compiled = True
            QMessageBox.information(self, t("compilation_successful"), message)
        else:
            self.is_compiled = False
            QMessageBox.critical(self, t("compilation_failed"), message)

    def import_script_folder(self):
        """ 
        Allows the user to select an external folder containing a script.
        Supports: main.py (Python), Main.java (Java), Main.c (C), Main.cpp (C++)
        The system will copy it into the window's saved 'scripts' folder, tying it directly to this button.
        """
        src_dir = QFileDialog.getExistingDirectory(self, t("select_source_folder"))
        if not src_dir: return

        # Check for supported script files
        script_file = None
        script_type = None
        
        if os.path.exists(os.path.join(src_dir, "main.py")):
            script_file = "main.py"
            script_type = "python"
        elif os.path.exists(os.path.join(src_dir, "Main.java")):
            script_file = "Main.java"
            script_type = "java"
        elif os.path.exists(os.path.join(src_dir, "Main.c")):
            script_file = "Main.c"
            script_type = "c"
        elif os.path.exists(os.path.join(src_dir, "Main.cpp")):
            script_file = "Main.cpp"
            script_type = "cpp"
        else:
            QMessageBox.warning(self, t("error"), t("folder_must_contain"))
            return

        # Figure out our bundle name so we can save the script neatly structured
        window_name = getattr(self.window(), "window_id", "default_window") 
        safe_btn_name = self.btn.text().replace(" ", "_")
        
        # Save scripts natively inside the core workspace window
        dest_dir = os.path.join("user_workspaces", window_name, "scripts", safe_btn_name)

        try:
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir)  # Overwrite if we are re-linking the script
            
            os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
            shutil.copytree(src_dir, dest_dir)
            
            self.script_path = os.path.join(dest_dir, script_file)
            self.script_type = script_type
            self.script_folder_name = safe_btn_name  # Store the folder name for future renaming
            self.is_compiled = False  # Reset compile status on new import
            
            msg = f"Folder imported to: {dest_dir}\n\nScript type: {script_type.upper()}"
            
            # For compiled languages, suggest compilation
            if script_type in ["java", "c", "cpp"]:
                msg += f"\n\n{t('import_link_script')}!"
            
            QMessageBox.information(self, t("import_success"), msg)
        except Exception as e:
            QMessageBox.critical(self, t("import_failed"), f"{t('could_not_copy').format(e=e)}")

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
        data["script_type"] = self.script_type
        data["is_compiled"] = self.is_compiled
        data["script_folder_name"] = self.script_folder_name  # Store the folder name for future renaming
        return data

    def from_dict(self, data):
        """ Restores button specific attributes from JSON load. """
        super().from_dict(data)
        self.btn.setText(data.get("label", "Run Script"))
        self.script_type = data.get("script_type", "")
        self.is_compiled = data.get("is_compiled", False)
        self.script_folder_name = data.get("script_folder_name", "")  # Load the stored folder name
        
        # Reconstruct path using the STORED folder name (not current button name)
        if data.get("script_path") and self.script_folder_name:
            window_name = getattr(self.window(), "window_id", "default_window") 
            
            # Determine the correct file extension based on script_type
            if self.script_type == "python":
                filename = "main.py"
            elif self.script_type == "java":
                filename = "Main.java"
            elif self.script_type == "c":
                filename = "Main.c"
            elif self.script_type == "cpp":
                filename = "Main.cpp"
            else:
                filename = "main.py"  # Default fallback
            
            # Use the STORED folder name, not the current button name
            self.script_path = os.path.join("user_workspaces", window_name, "scripts", self.script_folder_name, filename)
        else:
            self.script_path = ""
