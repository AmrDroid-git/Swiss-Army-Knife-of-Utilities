import os
import sys
import shutil
import platform
import subprocess
from PySide6.QtCore import QObject, QProcess, Signal

class ScriptEngine(QObject):
    """
    The Script Engine runs external scripts (Python, Java, C, C++) without freezing the UI.
    It uses PySide6's QProcess to handle asynchronous execution.
    Supports cross-platform execution (Windows/Linux) and multi-language compilation.
    """
    
    # Signals to communicate back to the UI canvas or Console widget
    execution_started = Signal()
    execution_finished = Signal()
    stdout_emitted = Signal(str) # Used to send live text to a Console Widget
    error_emitted = Signal(str)  # Used for system errors
    
    def __init__(self):
        super().__init__()
        self.process = None
        
        # State tracking for the async callbacks
        self.current_script_dir = ""
        self.current_outputs = []
        self.before_files = set()
        self.current_script_type = ""  # Track: 'python', 'java', 'c', 'cpp'

    def detect_script_type(self, script_path):
        """
        Determines the script type based on file extension.
        Returns: 'python', 'java', 'c', 'cpp', or None if unknown
        """
        filename = os.path.basename(script_path)
        if filename == "main.py":
            return "python"
        elif filename == "Main.java":
            return "java"
        elif filename == "Main.c":
            return "c"
        elif filename == "Main.cpp":
            return "cpp"
        return None

    def get_python_executable(self):
        """
        Returns the appropriate Python executable name for the current platform.
        Linux: 'python3', Windows: 'python'
        """
        if platform.system() == "Linux":
            return "python3"
        else:
            return "python"

    def run_script(self, script_path, inputs, outputs):
        """
        Called when a WidgetButton emits the run_script_requested signal.
        Handles Python, Java, C, and C++ scripts.
        """
        # Block concurrent overlapping runs for safety
        if self.process and self.process.state() == QProcess.Running:
            self.error_emitted.emit("A script is already running! Please wait.")
            return

        self.current_script_dir = os.path.dirname(script_path)
        
        # Safety Check: If the script folder was deleted or missing from zip
        if not os.path.exists(self.current_script_dir):
            self.error_emitted.emit(f"CRITICAL ERROR: Script directory not found at {self.current_script_dir}. Did you forget to link the script?")
            return
        
        # Detect script type
        self.current_script_type = self.detect_script_type(script_path)
        if not self.current_script_type:
            self.error_emitted.emit(f"ERROR: Unknown script type. Supported: main.py, Main.java, Main.c, Main.cpp")
            return
            
        self.current_outputs = outputs
        
        # 1. Take a snapshot of files in the script directory before running
        # We need this to mathematically determine which files were "generated" by the script run
        self.before_files = set(os.listdir(self.current_script_dir))
        
        # 2. Extract string arguments and Sandbox inputs
        args = []
        for widget in inputs:
            val = widget.get_value()
            
            # If this is an actual file input, we want to physically copy it into the engine sandbox.
            # This cleanly forces scripts that save outputs "next to the input file" to 
            # output inside our engine folder, so they get swept to the real Output Folder later!
            if getattr(widget, 'field_type', '') == 'file_field' and os.path.isfile(val):
                filename = os.path.basename(val)
                sandbox_path = os.path.join(self.current_script_dir, filename)
                
                if os.path.abspath(val) != os.path.abspath(sandbox_path):
                    try:
                        import shutil
                        shutil.copy2(val, sandbox_path)
                        # Register it as a "before_file" so the sweeper ignores it later
                        self.before_files.add(filename)
                        args.append(os.path.abspath(sandbox_path))
                    except Exception as e:
                        self.error_emitted.emit(f"[Sandbox Warning]: Could not copy {filename} into sandbox. {e}")
                        args.append(os.path.abspath(val))
                else:
                    args.append(os.path.abspath(val))
            else:
                args.append(val)
        
        # 3. Setup PySide6 Async QProcess
        self.process = QProcess(self)
        
        # 4. Prepare command based on script type
        if self.current_script_type == "python":
            self.process.setProgram(self.get_python_executable())
            script_name = os.path.basename(script_path)
            self.process.setArguments(["-u", script_name] + args)
            
        elif self.current_script_type == "java":
            # Find compiled Main.class file
            class_path = os.path.join(self.current_script_dir, "Main.class")
            if not os.path.exists(class_path):
                self.error_emitted.emit(f"ERROR: Main.class not found. Please compile the Java script first using the 'Compile' option.")
                self.process = None
                return
            
            self.process.setProgram("java")
            # Use "." as classpath since we're already in the script directory via setWorkingDirectory
            self.process.setArguments(["-cp", ".", "Main"] + args)
            
        elif self.current_script_type == "c":
            # Find compiled Main executable (or Main.exe on Windows)
            exe_name = "Main.exe" if platform.system() == "Windows" else "Main"
            exe_path = os.path.join(self.current_script_dir, exe_name)
            if not os.path.exists(exe_path):
                self.error_emitted.emit(f"ERROR: {exe_name} executable not found. Please compile the C script first using the 'Compile' option.")
                self.process = None
                return
            
            # On Linux, use stdbuf to unbuffer output for real-time display
            if platform.system() == "Linux":
                self.process.setProgram("stdbuf")
                self.process.setArguments(["-oL", exe_path] + args)
            else:
                # Windows: run directly but output should flush due to fflush() calls
                self.process.setProgram(exe_path)
                self.process.setArguments(args)
            
        elif self.current_script_type == "cpp":
            # Find compiled Main executable (or Main.exe on Windows)
            exe_name = "Main.exe" if platform.system() == "Windows" else "Main"
            exe_path = os.path.join(self.current_script_dir, exe_name)
            if not os.path.exists(exe_path):
                self.error_emitted.emit(f"ERROR: {exe_name} executable not found. Please compile the C++ script first using the 'Compile' option.")
                self.process = None
                return
            
            # On Linux, use stdbuf to unbuffer output for real-time display
            if platform.system() == "Linux":
                self.process.setProgram("stdbuf")
                self.process.setArguments(["-oL", exe_path] + args)
            else:
                # Windows: run directly but output should flush due to fflush() calls
                self.process.setProgram(exe_path)
                self.process.setArguments(args)
        
        # 5. Set working directory safely using absolute path
        self.process.setWorkingDirectory(os.path.abspath(self.current_script_dir))
        
        # Set environment for UTF-8 (important for catching stdout string cleanly)
        env = self.process.systemEnvironment()
        env.append("PYTHONIOENCODING=utf-8")
        self.process.setEnvironment(env)
        
        # Connect QProcess async signals to our python handlers
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.errorOccurred.connect(self.handle_error)
        
        # 6. Start the async process! This does NOT freeze the PySide window!
        self.execution_started.emit()
        self.process.start()
        
    def handle_stdout(self):
        """ Catches standard print() outputs live. """
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode('utf-8', errors='replace').strip()
        if text:
            # Emit outward so it can be picked up by a Console Widget anywhere in the UI
            self.stdout_emitted.emit(text)
            
            # Or send it directly to Output Text Widgets
            text_outputs = [w for w in self.current_outputs if getattr(w, 'field_type', '') == 'text_field']
            for o in text_outputs:
                o.set_value(text)

    def handle_stderr(self):
        """ Catches error tracebacks generated by faulty scripts live. """
        data = self.process.readAllStandardError()
        text = bytes(data).decode('utf-8', errors='replace').strip()
        if text:
            self.error_emitted.emit(f"ERROR: {text}")
            
            # Send to Output Text Widgets so errors are highly visible on canvas
            text_outputs = [w for w in self.current_outputs if getattr(w, 'field_type', '') == 'text_field']
            for o in text_outputs:
                o.set_value(f"CRASH: {text}")

    def handle_error(self, error):
        """ Catches system-level failure to launch the script (e.g., Python missing). """
        self.error_emitted.emit(f"Process Initialization Error: {self.process.errorString()}")

    def handle_finished(self, exitCode, exitStatus):
        """
        Triggered asynchronously when the Python script fully completes.
        Handles moving any newly generated files to their intended targets.
        """
        try:
            # 1. Take a snapshot of files after running
            after_files = set(os.listdir(self.current_script_dir))
            
            # Standard Set-Mathematics to isolate completely brand-new files
            new_items = after_files - self.before_files
            
            # 2. Determine target destination folder
            file_outputs = [w for w in self.current_outputs if getattr(w, 'field_type', '') in ['file_field', 'folder_field']]
            
            # Default safety destination inside the script folder
            final_dest = os.path.join(self.current_script_dir, "files_outputs")
            
            # If the user specified a custom target folder in a Widget on the canvas
            if file_outputs and file_outputs[0].get_value():
                user_chosen_dir = file_outputs[0].get_value()
                if os.path.isdir(user_chosen_dir):
                    final_dest = user_chosen_dir
                    
            os.makedirs(final_dest, exist_ok=True)

            # 3. Move the files
            if new_items:
                for item in new_items:
                    if item == "files_outputs": continue
                    
                    src_path = os.path.join(self.current_script_dir, item)
                    dst_path = os.path.join(final_dest, item)
                    
                    if os.path.exists(dst_path):
                        if os.path.isdir(dst_path):
                            shutil.rmtree(dst_path) # Delete old folders to prevent crash
                        else:
                            os.remove(dst_path)     # Delete old files automatically
                            
                    shutil.move(src_path, dst_path)
                    
                self.stdout_emitted.emit(f"\n[ENGINE LOG]: Moved {len(new_items)} new generated items to target destination.")
                
        except Exception as e:
            self.error_emitted.emit(f"Failed to move output files: {str(e)}")
            
        finally:
            self.execution_finished.emit()
            self.process = None # Cleanup object reference


    def send_input(self, text):
        """ Pipes user-submitted strings directly into the process's standard input stream in real-time. """
        if self.process and self.process.state() == QProcess.Running:
            # We must append a newline '\n' exactly as if the user physically hit Enter in a CMD prompt
            self.process.write((text + "\n").encode('utf-8'))

    def compile_script(self, script_path):
        """
        Compiles Java, C, or C++ scripts.
        Returns: (success, message)
        """
        script_type = self.detect_script_type(script_path)
        script_dir = os.path.dirname(script_path)
        
        if script_type == "python":
            return (True, "Python scripts do not require compilation.")
        
        elif script_type == "java":
            java_file = os.path.join(script_dir, "Main.java")
            if not os.path.exists(java_file):
                return (False, "Main.java not found in the script folder.")
            
            try:
                result = subprocess.run(
                    ["javac", "Main.java"],
                    cwd=os.path.abspath(script_dir),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    return (True, "Java compilation successful!")
                else:
                    return (False, f"Java compilation failed:\n{result.stderr}")
            except FileNotFoundError:
                return (False, "javac not found. Please install Java JDK and add it to your system PATH.")
            except Exception as e:
                return (False, f"Compilation error: {str(e)}")
        
        elif script_type == "c":
            c_file = os.path.join(script_dir, "Main.c")
            if not os.path.exists(c_file):
                return (False, "Main.c not found in the script folder.")
            
            try:
                exe_name = "Main.exe" if platform.system() == "Windows" else "Main"
                
                # Determine compiler based on platform
                compiler = "gcc"
                
                result = subprocess.run(
                    [compiler, "Main.c", "-o", exe_name],
                    cwd=os.path.abspath(script_dir),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    return (True, f"C compilation successful! Executable: {exe_name}")
                else:
                    return (False, f"C compilation failed:\n{result.stderr}")
            except FileNotFoundError:
                return (False, "gcc not found. Please install MinGW/GCC and add it to your system PATH.")
            except Exception as e:
                return (False, f"Compilation error: {str(e)}")
        
        elif script_type == "cpp":
            cpp_file = os.path.join(script_dir, "Main.cpp")
            if not os.path.exists(cpp_file):
                return (False, "Main.cpp not found in the script folder.")
            
            try:
                exe_name = "Main.exe" if platform.system() == "Windows" else "Main"
                
                # Determine compiler based on platform
                compiler = "g++"
                
                result = subprocess.run(
                    [compiler, "Main.cpp", "-o", exe_name],
                    cwd=os.path.abspath(script_dir),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    return (True, f"C++ compilation successful! Executable: {exe_name}")
                else:
                    return (False, f"C++ compilation failed:\n{result.stderr}")
            except FileNotFoundError:
                return (False, "g++ not found. Please install MinGW/GCC and add it to your system PATH.")
            except Exception as e:
                return (False, f"Compilation error: {str(e)}")
        
        return (False, f"Unknown script type: {script_type}")
