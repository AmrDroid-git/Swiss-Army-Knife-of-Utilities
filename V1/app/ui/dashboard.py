import os
import shutil
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QInputDialog, 
                               QTreeWidget, QTreeWidgetItem, QLabel, QMessageBox, QFileDialog, QMenu, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from app.ui.dynamic_canvas import CustomWindow
from app.core import package_manager, group_manager

class Dashboard(QMainWindow):
    """
    The main project selection hub acting as the primary menu when starting the software.
    Supports Launching, Creating, Importing, and Exporting complete workspace packages.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Script Builder - Universal Dashboard")
        self.resize(700, 750)
        self.setStyleSheet("""
            QMainWindow { 
                background-color: #ecf0f1; 
            }
            QMenuBar {
                background-color: #f5f5f5;
                color: #2c3e50;
                border-bottom: 1px solid #bdc3c7;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
                color: white;
            }
            QMenu {
                background-color: #ffffff;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                border: none; 
                padding: 8px 14px; 
                border-radius: 4px; 
                font-size: 12px;
                font-weight: bold; 
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #1f618d; }
            QTreeWidget { 
                background: white; 
                border: 1px solid #bdc3c7; 
                border-radius: 6px; 
                font-size: 14px; 
                padding: 5px;
            }
            QTreeWidget::item { 
                padding: 6px; 
                border-bottom: 1px solid #eee;
            }
            QTreeWidget::item:selected { 
                background-color: #3498db; 
                color: white; 
            }
        """)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        lay = QVBoxLayout(central_widget)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)
        
        # ===== CREATE MENU BAR =====
        menubar = self.menuBar()
        
        # FILE MENU
        file_menu = menubar.addMenu("📁 File")
        file_menu.addAction("➕ New Window", self.new_win)
        file_menu.addAction("📁 New Group", self.create_new_group)
        file_menu.addSeparator()
        file_menu.addAction("⬇️ Import .ZIP", self.import_win)
        file_menu.addAction("📤 Export .ZIP", self.export_win_button)
        file_menu.addSeparator()
        file_menu.addAction("❌ Exit", self.close)
        
        # EDIT MENU
        edit_menu = menubar.addMenu("✏️ Edit")
        edit_menu.addAction("✏️ Rename Group", self.edit_selected_group)
        edit_menu.addAction("🗑️ Delete Group", self.delete_selected_group)
        edit_menu.addSeparator()
        edit_menu.addAction("🗑️ Delete Window", self.delete_selected_window)
        
        # VIEW MENU
        view_menu = menubar.addMenu("👁️ View")
        view_menu.addAction("📂 Open Selected Window", self.open_win)
        view_menu.addAction("📤 Move Window to Group", self.move_selected_to_group)
        
        # ===== HEADER =====
        header = QLabel("<b>My Digital Workspace</b>")
        header.setStyleSheet("font-size: 18px; color: #2c3e50; padding: 8px 0px; font-weight: bold;")
        lay.addWidget(header)
        
        # Central tree widget for grouped projects
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Windows & Groups"])
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.doubleClicked.connect(self.on_tree_double_click)
        lay.addWidget(self.tree)
        
        # Need to keep python tracking active references to subwindows to stop garbage collection
        self.active_windows = [] 

        self.refresh()

    def refresh(self):
        """Load and display all groups and windows in tree structure."""
        self.tree.clear()
        
        # Organize any new windows that aren't grouped yet
        group_manager.organize_ungrouped_windows()
        
        # Load groups data
        groups_data = group_manager.load_groups()
        
        # Create tree items for each group
        for group_info in groups_data.get("groups", []):
            group_name = group_info["name"]
            group_item = QTreeWidgetItem(self.tree)
            group_item.setText(0, f"📁 {group_name}")
            group_item.setData(0, Qt.UserRole, ("group", group_name))
            
            # Expand/collapse based on saved state
            group_item.setExpanded(group_info.get("expanded", True))
            
            # Add windows to group
            for window_id in group_info.get("windows", []):
                window_item = QTreeWidgetItem(group_item)
                window_item.setText(0, f"📄 {window_id}")
                window_item.setData(0, Qt.UserRole, ("window", window_id))
        
        # Connect tree expansion changes
        self.tree.itemExpanded.connect(self.on_item_expanded)
        self.tree.itemCollapsed.connect(self.on_item_collapsed)
    
    def on_item_expanded(self, item):
        """Save group expansion state."""
        data = item.data(0, Qt.UserRole)
        if data and data[0] == "group":
            group_manager.toggle_group_expanded(data[1])
    
    def on_item_collapsed(self, item):
        """Save group collapse state."""
        data = item.data(0, Qt.UserRole)
        if data and data[0] == "group":
            group_manager.toggle_group_expanded(data[1])
    
    def on_tree_double_click(self, index):
        """Handle double-click on tree items - open window if it's a window item."""
        item = self.tree.itemFromIndex(index)
        if item:
            data = item.data(0, Qt.UserRole)
            if data and data[0] == "window":
                # Double-clicked a window - open it
                window_id = data[1]
                w = CustomWindow(window_id)
                w.show()
                self.active_windows.append(w)
    
    def get_selected_window(self):
        """Get the currently selected window ID from tree."""
        item = self.tree.currentItem()
        if item:
            data = item.data(0, Qt.UserRole)
            if data and data[0] == "window":
                return data[1]
        return None

    def get_selected_group(self):
        """Get the currently selected group name from tree."""
        item = self.tree.currentItem()
        if item:
            data = item.data(0, Qt.UserRole)
            if data and data[0] == "group":
                return data[1]
        return None

    def edit_selected_group(self):
        """Rename selected group."""
        group_name = self.get_selected_group()
        if not group_name:
            QMessageBox.warning(self, "Selection Required", "Please select a group to rename!")
            return
        self.rename_group(group_name)

    def delete_selected_group(self):
        """Delete selected group."""
        group_name = self.get_selected_group()
        if not group_name:
            QMessageBox.warning(self, "Selection Required", "Please select a group to delete!")
            return
        self.delete_group(group_name)

    def delete_selected_window(self):
        """Delete selected window."""
        window_id = self.get_selected_window()
        if not window_id:
            QMessageBox.warning(self, "Selection Required", "Please select a window to delete!")
            return
        self.delete_window(window_id)

    def move_selected_to_group(self):
        """Move selected window to group."""
        window_id = self.get_selected_window()
        if not window_id:
            QMessageBox.warning(self, "Selection Required", "Please select a window to move!")
            return
        self.move_window_to_group(window_id)

    def new_win(self):
        n, ok = QInputDialog.getText(self, "New Workspace", "Enter Window Name:")
        if ok and n:
            n = n.replace(" ", "_")  # Safety escaping
            # Add to Ungrouped by default
            group_manager.add_window_to_group(n, "Ungrouped")
            w = CustomWindow(n)
            w.show()
            self.active_windows.append(w)  # Protect from GC crash
            self.refresh()

    def open_win(self):
        window_id = self.get_selected_window()
        if window_id:
            w = CustomWindow(window_id)
            w.show()
            self.active_windows.append(w)

    def import_win(self):
        """Safely extracts .ZIP project bundle fully integrating it physically to the workspace format"""
        path, _ = QFileDialog.getOpenFileName(self, "Select Window .ZIP", "", "Zip Files (*.zip)")
        if not path: 
            return
        
        n, ok = QInputDialog.getText(self, "Import Workspace", "Choose a name for the window:")
        if ok and n:
            n = n.replace(" ", "_")
            try:
                package_manager.import_window(path, n)
                # Add to Ungrouped by default
                group_manager.add_window_to_group(n, "Ungrouped")
                QMessageBox.information(self, "Success", f"Project {n} successfully imported!")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "System Failure", f"Failed to import:\n{e}")

    def export_win_button(self):
        """Export a selected window to ZIP."""
        window_id = self.get_selected_window()
        if not window_id:
            QMessageBox.warning(self, "Selection Required", "Please select a window to export first!")
            return
        self.export_window(window_id)
    
    def create_new_group(self):
        """Create a new group."""
        group_name, ok = QInputDialog.getText(self, "Create New Group", "Group Name:")
        if ok and group_name:
            group_name = group_name.strip()
            if group_manager.create_group(group_name):
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", f"Group '{group_name}' already exists!")

    def show_context_menu(self, pos):
        """Right click options on groups or windows."""
        item = self.tree.itemAt(pos)
        if not item:
            return
        
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        
        item_type, item_name = data
        menu = QMenu(self)
        
        if item_type == "group":
            # Options for groups
            edit_act = menu.addAction("✏️ Rename Group")
            delete_act = menu.addAction("🗑️ Delete Group")
            menu.addSeparator()
            add_win_to_group = menu.addAction("➕ Add New Window")
            
            action = menu.exec(self.tree.mapToGlobal(pos))
            
            if action == edit_act:
                self.rename_group(item_name)
            elif action == delete_act:
                self.delete_group(item_name)
            elif action == add_win_to_group:
                self.new_win_in_group(item_name)
        
        elif item_type == "window":
            # Options for windows
            open_act = menu.addAction("📂 Open Window")
            menu.addSeparator()
            delete_act = menu.addAction("🗑️ Delete Window")
            menu.addSeparator()
            move_act = menu.addAction("📤 Move to Group")
            export_act = menu.addAction("📤 Export .ZIP")
            
            action = menu.exec(self.tree.mapToGlobal(pos))
            
            if action == open_act:
                w = CustomWindow(item_name)
                w.show()
                self.active_windows.append(w)
            elif action == delete_act:
                self.delete_window(item_name)
            elif action == move_act:
                self.move_window_to_group(item_name)
            elif action == export_act:
                self.export_window(item_name)
    
    def rename_group(self, old_name):
        """Rename a group."""
        new_name, ok = QInputDialog.getText(self, "Rename Group", f"New name for '{old_name}':")
        if ok and new_name:
            if group_manager.rename_group(old_name, new_name):
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", "Could not rename group")
    
    def delete_group(self, group_name):
        """Delete a group (moves windows to Ungrouped)."""
        reply = QMessageBox.question(self, "Delete Group", 
                                     f"Delete '{group_name}'? Windows will move to 'Ungrouped'.")
        if reply == QMessageBox.Yes:
            group_manager.delete_group(group_name)
            self.refresh()
    
    def delete_window(self, window_id):
        """Delete a window."""
        reply = QMessageBox.question(self, "Delete Window", 
                                     f"Permanently delete '{window_id}'? This cannot be undone!")
        if reply == QMessageBox.Yes:
            try:
                win_folder = os.path.join(package_manager.BASE_PROJECT_DIR, window_id)
                if os.path.exists(win_folder):
                    shutil.rmtree(win_folder)
                group_manager.remove_window_from_groups(window_id)
                self.refresh()
                QMessageBox.information(self, "Success", f"Window '{window_id}' deleted!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete window:\n{e}")
    
    def move_window_to_group(self, window_id):
        """Move window to a different group."""
        groups_data = group_manager.load_groups()
        group_names = [g["name"] for g in groups_data.get("groups", [])]
        
        # Create a simple dialog to select group
        group_name, ok = QInputDialog.getItem(self, "Move Window", 
                                              f"Select group for '{window_id}':", 
                                              group_names, 0, False)
        if ok and group_name:
            group_manager.add_window_to_group(window_id, group_name)
            self.refresh()
    
    def new_win_in_group(self, group_name):
        """Create a new window and add it to specified group."""
        n, ok = QInputDialog.getText(self, "New Workspace", "Enter Window Name:")
        if ok and n:
            n = n.replace(" ", "_")
            group_manager.add_window_to_group(n, group_name)
            w = CustomWindow(n)
            w.show()
            self.active_windows.append(w)
            self.refresh()
    
    def export_window(self, window_id):
        """Export a window to ZIP."""
        dest, _ = QFileDialog.getSaveFileName(self, "Save .ZIP bundle output", 
                                              window_id + "_export.zip", "Zip Files (*.zip)")
        if dest:
            try:
                package_manager.export_window(window_id, dest)
                QMessageBox.information(self, "Success", f"Archive '{window_id}' exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export:\n{e}")
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
