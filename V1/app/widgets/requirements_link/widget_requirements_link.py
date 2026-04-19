import os
import shutil
import subprocess
import sys
from PySide6.QtWidgets import QLabel, QHBoxLayout, QMenu, QFileDialog, QInputDialog, QMessageBox, QDialog, QVBoxLayout, QTextBrowser, QPushButton, QSplitter, QTextEdit
from PySide6.QtCore import Qt, QPoint, QThread, Signal
from PySide6.QtGui import QFont
from app.widgets.base_widget import BaseComponent
from app.translator import t

class CommandExecutor(QThread):
    """Worker thread to execute shell commands with output streaming."""
    output_updated = Signal(str)  # Emits command output
    finished_signal = Signal()     # Emits when command completes
    
    def __init__(self, command):
        super().__init__()
        self.command = command
    
    def run(self):
        """Execute command and stream output."""
        try:
            # Determine shell based on OS
            shell = True if sys.platform != 'win32' else False
            
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1  # Line buffered
            )
            
            # Stream output in real-time
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.output_updated.emit(line.rstrip('\n'))
            
            process.wait()
            self.finished_signal.emit()
        except Exception as e:
            self.output_updated.emit(f"Error: {e}")
            self.finished_signal.emit()

class InteractiveTerminal(QTextEdit):
    """An interactive terminal that executes shell commands."""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background-color: #000000;
            color: #00ff00;
            font: 9pt 'Courier New', 'Monospace';
            padding: 5px;
            border: none;
        """)
        
        self.setPlaceholderText(t("terminal_title"))
        self.command_executor = None
        self.output_buffer = ""
        self.prompt_pos = 0  # Track where the prompt starts
        
        # Show initial prompt
        self.setText("$ ")
        self.prompt_pos = 0
    
    def keyPressEvent(self, event):
        """Handle key presses - execute command on Enter."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Get all text
            all_text = self.toPlainText()
            
            # Get text after the last prompt
            last_prompt_idx = all_text.rfind("$ ")
            if last_prompt_idx != -1:
                # Extract command (everything after "$ ")
                command = all_text[last_prompt_idx + 2:].strip()
                
                if command:
                    # Prevent further editing and add newline
                    self.setReadOnly(True)
                    self.append("")
                    
                    # Execute the command
                    self.execute_command(command)
                else:
                    # Empty command - just add new prompt
                    self.append("")
                    self.append("$ ")
            else:
                # No prompt found, add one
                self.append("")
                self.append("$ ")
        else:
            super().keyPressEvent(event)
    
    def execute_command(self, command):
        """Execute a shell command with async output."""
        # Kill previous executor if still running
        if self.command_executor and self.command_executor.isRunning():
            self.command_executor.quit()
            self.command_executor.wait()
        
        self.command_executor = CommandExecutor(command)
        self.command_executor.output_updated.connect(self.on_output)
        self.command_executor.finished_signal.connect(self.on_command_finished)
        self.command_executor.start()
    
    def on_output(self, output):
        """Receive output from command executor."""
        self.append(output)
        self.output_buffer += output + "\n"
    
    def on_command_finished(self):
        """Called when command execution is finished."""
        # Re-enable editing and show new prompt
        self.setReadOnly(False)
        self.append("$ ")
    
    def clear_terminal(self):
        """Clear all terminal output."""
        self.clear()
        self.output_buffer = ""
        self.setText("$ ")
        self.setReadOnly(False)
    
    def get_all_output(self):
        """Get all terminal output (for copying)."""
        return self.toPlainText()


class WidgetRequirementsLink(BaseComponent):
    """
    A widget that displays a small link icon (<a>) which opens a requirements/documentation window.
    Allows linking to a markdown file that describes requirements, dependencies, or other info.
    Includes a button to open a separate terminal window.
    """

    def __init__(self, parent, pos):
        super().__init__(parent, "widget_requirements_link", pos)
        self.resize(60, 30)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Display as a link-like label
        self.lbl = QLabel("ⓘ Info")
        font = QFont()
        font.setUnderline(True)
        font.setPointSize(10)
        self.lbl.setFont(font)
        self.lbl.setStyleSheet("color: #0078d4; cursor: pointer;")
        self.layout.addWidget(self.lbl)
        
        self.md_file_path = ""  # Path to linked markdown file
        self.widget_name = "Requirements"
        self.workspace_md_path = ""  # Path to markdown in workspace

    def contextMenuEvent(self, event):
        """ The right-click menu tailored for the Requirements Link (Edit Mode only). """
        if not self.is_edit_mode: return
        menu = QMenu(self)
        
        link_act = menu.addAction(t("link_markdown"))
        rename_act = menu.addAction("Rename Label")
        
        # Append the standard parent actions (Resize, Delete)
        font_act, res_act, del_act = self.add_base_actions(menu)
        
        action = menu.exec(event.globalPos())
        
        if action == link_act:
            self.link_markdown_file()
        elif action == rename_act:
            t_text, ok = QInputDialog.getText(self, "Rename", "Label Text:", text=self.lbl.text())
            if ok: 
                self.lbl.setText(t_text)
                self.widget_name = t_text
            
        self.handle_base_actions(action, font_act, res_act, del_act)

    def apply_font(self, font):
        self.lbl.setFont(font)

    def link_markdown_file(self):
        """
        Allows the user to select a markdown (.md) file that contains requirements documentation.
        Saves it to the workspace for persistence.
        """
        md_file = QFileDialog.getOpenFileName(self, t("markdown_file"), "", "Markdown Files (*.md);;All Files (*)")
        if md_file and md_file[0]:
            self.md_file_path = md_file[0]
            
            # Save to workspace
            window_name = getattr(self.window(), "window_id", "default_window")
            workspace_docs_dir = os.path.join("user_workspaces", window_name, "docs")
            os.makedirs(workspace_docs_dir, exist_ok=True)
            
            md_filename = os.path.basename(md_file[0])
            self.workspace_md_path = os.path.join(workspace_docs_dir, md_filename)
            
            try:
                shutil.copy2(md_file[0], self.workspace_md_path)
                QMessageBox.information(self, "Success", f"{t('linked_to')}:\n{md_filename}\n\n{t('saved_persistence')}")
            except Exception as e:
                QMessageBox.critical(self, t("error"), f"{t('could_not_save')}: {e}")

    def mousePressEvent(self, event):
        """
        In Run Mode: Click to open requirements window.
        In Edit Mode: Handle dragging like normal.
        """
        if not self.is_edit_mode and event.button() == Qt.LeftButton:
            self.show_requirements_window()
        super().mousePressEvent(event)

    def markdown_to_html(self, markdown_text):
        """
        Converts markdown text to HTML for rendering in QTextBrowser.
        """
        try:
            import markdown
            return markdown.markdown(markdown_text, extensions=['tables', 'fenced_code', 'codehilite'])
        except ImportError:
            # Fallback: simple markdown-like HTML conversion
            html = "<html><body>"
            lines = markdown_text.split('\n')
            for line in lines:
                if line.startswith("# "):
                    html += f"<h1>{line[2:]}</h1>"
                elif line.startswith("## "):
                    html += f"<h2>{line[3:]}</h2>"
                elif line.startswith("### "):
                    html += f"<h3>{line[4:]}</h3>"
                elif line.startswith("- ") or line.startswith("* "):
                    html += f"<li>{line[2:]}</li>"
                elif line.startswith(">"):
                    html += f"<blockquote>{line[1:]}</blockquote>"
                elif line.startswith("```"):
                    html += "<pre><code>"
                elif line == "```":
                    html += "</code></pre>"
                elif line.strip():
                    html += f"<p>{line}</p>"
            html += "</body></html>"
            return html

    def show_requirements_window(self):
        """
        Opens a dialog showing the markdown content with integrated interactive terminal.
        """
        # Use workspace markdown if available, otherwise original
        md_path = self.workspace_md_path if self.workspace_md_path and os.path.exists(self.workspace_md_path) else self.md_file_path
        
        if not md_path or not os.path.exists(md_path):
            QMessageBox.warning(self, t("error"), t("no_requirements"))
            return
        
        # Read markdown content
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            QMessageBox.critical(self, t("error"), f"{t('could_not_read')}: {e}")
            return
        
        # Create professional requirements dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(self.widget_name)
        dialog.resize(900, 700)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QTextBrowser {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #d0d0d0;
                padding: 10px;
                font: 10pt 'Segoe UI', 'Arial';
            }
            QTextEdit {
                background-color: #000000;
                color: #00ff00;
                border: 1px solid #d0d0d0;
                font: 9pt 'Courier New', 'Monospace';
                padding: 5px;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Create splitter for resizable content and terminal
        splitter = QSplitter(Qt.Vertical)
        
        # Markdown content display
        text_browser = QTextBrowser()
        html_content = self.markdown_to_html(content)
        text_browser.setHtml(html_content)
        splitter.addWidget(text_browser)
        
        # Create an interactive terminal
        terminal = InteractiveTerminal()
        splitter.addWidget(terminal)
        
        splitter.setStretchFactor(0, 2)  # Markdown takes more space
        splitter.setStretchFactor(1, 1)  # Terminal takes less space
        
        layout.addWidget(splitter)
        
        # Button layout
        btn_layout = QHBoxLayout()
        
        btn_clear = QPushButton(t("clear_terminal"))
        btn_clear.clicked.connect(terminal.clear_terminal)
        btn_layout.addWidget(btn_clear)
        
        btn_copy = QPushButton(t("copy_terminal"))
        btn_copy.clicked.connect(lambda: self.copy_to_clipboard(terminal.get_all_output()))
        btn_layout.addWidget(btn_copy)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dialog.close)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        
        dialog.exec()


    def copy_to_clipboard(self, text):
        """Copy text to system clipboard."""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, t("copied"), t("terminal_text_copied"))

    def to_dict(self):
        """ Appends requirements link specific attributes to the BaseComponent JSON format. """
        data = super().to_dict()
        data["label"] = self.lbl.text()
        data["md_file_path"] = self.md_file_path
        data["workspace_md_path"] = self.workspace_md_path
        data["widget_name"] = self.widget_name
        return data

    def from_dict(self, data):
        """ Restores requirements link specific attributes from JSON load. """
        super().from_dict(data)
        self.lbl.setText(data.get("label", "ⓘ Info"))
        self.md_file_path = data.get("md_file_path", "")
        self.workspace_md_path = data.get("workspace_md_path", "")
        self.widget_name = data.get("widget_name", "Requirements")
