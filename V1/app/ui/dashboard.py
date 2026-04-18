import os
import shutil
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QInputDialog, QListWidget, QLabel, QMessageBox, QFileDialog, QMenu
from PySide6.QtCore import Qt
from app.ui.dynamic_canvas import CustomWindow
from app.core import package_manager

class Dashboard(QWidget):
    """
    The main project selection hub acting as the primary menu when starting the software.
    Supports Launching, Creating, Importing, and Exporting complete workspace packages.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Script Builder - Universal Dashboard")
        self.resize(450, 600)
        self.setStyleSheet("""
            QWidget { 
                font-family: 'Inter', 'Segoe UI', sans-serif; 
                background-color: #ecf0f1; 
            }
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                border: none; 
                padding: 12px; 
                border-radius: 6px; 
                font-size: 14px;
                font-weight: bold; 
            }
            QPushButton:hover { background-color: #2980b9; }
            QListWidget { 
                background: white; 
                border: 1px solid #bdc3c7; 
                border-radius: 6px; 
                font-size: 16px; 
                padding: 5px;
            }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #eee; }
            QListWidget::item:selected { background-color: #3498db; color: white; }
        """)
        
        lay = QVBoxLayout(self)
        
        # Header area
        header = QLabel("<b>My Digital Workspace</b>")
        header.setStyleSheet("font-size: 20px; color: #2c3e50; padding-top: 10px; padding-bottom: 5px;")
        lay.addWidget(header)
        
        # Central list of projects
        self.list = QListWidget()
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self.show_context_menu)
        lay.addWidget(self.list)
        
        # Buttons Layer Layout block
        btns_lay = QVBoxLayout()
        
        top_btns = QHBoxLayout()
        btn_open = QPushButton("Open Window")
        btn_new = QPushButton("+ Create New")
        top_btns.addWidget(btn_open)
        top_btns.addWidget(btn_new)
        
        bot_btns = QHBoxLayout()
        btn_import = QPushButton("⬇️ Import .ZIP")
        btn_import.setStyleSheet("background-color: #27ae60;")
        btn_export = QPushButton("📤 Export .ZIP")
        btn_export.setStyleSheet("background-color: #8e44ad;")
        bot_btns.addWidget(btn_import)
        bot_btns.addWidget(btn_export)
        
        btns_lay.addLayout(top_btns)
        btns_lay.addLayout(bot_btns)
        lay.addLayout(btns_lay)

        # Wire handlers
        btn_new.clicked.connect(self.new_win)
        btn_open.clicked.connect(self.open_win)
        btn_import.clicked.connect(self.import_win)
        btn_export.clicked.connect(self.export_win)
        
        # Need to keep python tracking active references to subwindows to stop garbage collection
        self.active_windows = [] 

        self.refresh()

    def refresh(self):
        """ Scans the native directory and dynamically repopulates UI list. """
        self.list.clear()
        if os.path.exists(package_manager.BASE_PROJECT_DIR):
            projects = [d for d in os.listdir(package_manager.BASE_PROJECT_DIR) 
                        if os.path.isdir(os.path.join(package_manager.BASE_PROJECT_DIR, d))]
            self.list.addItems(projects)

    def new_win(self):
        n, ok = QInputDialog.getText(self, "New Workspace", "Enter Window Name:")
        if ok and n:
            n = n.replace(" ", "_") # Safety escaping
            w = CustomWindow(n)
            w.show()
            self.active_windows.append(w) # Protect from GC crash
            self.refresh()

    def open_win(self):
        it = self.list.currentItem()
        if it:
            w = CustomWindow(it.text())
            w.show()
            self.active_windows.append(w)

    def import_win(self):
        """ Safely extracts .ZIP project bundle fully integrating it physically to the workspace format """
        path, _ = QFileDialog.getOpenFileName(self, "Select Window .ZIP", "", "Zip Files (*.zip)")
        if not path: return
        
        n, ok = QInputDialog.getText(self, "Import Workspace", "Choose a name for the window:")
        if ok and n:
            n = n.replace(" ", "_")
            try:
                package_manager.import_window(path, n)
                QMessageBox.information(self, "Success", f"Project {n} successfully injected!")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "System Failure", f"Failed to mount import:\n{e}")

    def export_win(self):
        """ Uses Package Manager standard tools to encapsulate the raw directory tree to a sharable archive """
        it = self.list.currentItem()
        if not it:
            QMessageBox.warning(self, "Export Rule", "Select a project target heavily from the List Box first!")
            return
            
        win_id = it.text()
        dest, _ = QFileDialog.getSaveFileName(self, "Save .ZIP bundle output", win_id + "_export.zip", "Zip Files (*.zip)")
        if dest:
            try:
                package_manager.export_window(win_id, dest)
                QMessageBox.information(self, "Success", f"Archive {win_id} successfully compiled globally!")
            except Exception as e:
                QMessageBox.critical(self, "Compression Error", f"Failed to export archive globally:\n{e}")

    def show_context_menu(self, pos):
        """ Right click options on the window list. """
        item = self.list.itemAt(pos)
        if not item: return

        menu = QMenu(self)
        del_act = menu.addAction("🗑️ Delete Window")
        
        action = menu.exec(self.list.mapToGlobal(pos))
        
        if action == del_act:
            reply = QMessageBox.question(
                self, "Confirm Deletion", 
                f"Are you sure you want to completely delete '{item.text()}'?\nThis action cannot be undone and will delete all its scripts.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                target_dir = os.path.join(package_manager.BASE_PROJECT_DIR, item.text())
                try:
                    shutil.rmtree(target_dir)
                    self.refresh()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete window:\n{e}")
