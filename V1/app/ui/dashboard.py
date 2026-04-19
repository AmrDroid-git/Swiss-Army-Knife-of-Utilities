import os
import shutil
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QInputDialog, 
                               QTreeWidget, QTreeWidgetItem, QLabel, QMessageBox, QFileDialog, QMenu, QWidget, QComboBox, QDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from app.ui.dynamic_canvas import CustomWindow
from app.core import package_manager, group_manager, theme_manager
from app.translator import get_translator, t, get_language_signal

class Dashboard(QMainWindow):
    """
    The main project selection hub acting as the primary menu when starting the software.
    Supports Launching, Creating, Importing, and Exporting complete workspace packages.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Script Builder - Universal Dashboard")
        self.resize(700, 750)
        
        # Theme is applied globally via QApplication in main.py.
        # No per-window stylesheet needed here.
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        lay = QVBoxLayout(central_widget)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)
        
        # ===== CREATE MENU BAR =====
        menubar = self.menuBar()
        
        # FILE MENU
        file_menu = menubar.addMenu(t("file"))
        file_menu.addAction(t("new_window"), self.new_win)
        file_menu.addAction(t("new_group"), self.create_new_group)
        file_menu.addSeparator()
        file_menu.addAction(t("import_zip"), self.import_win)
        file_menu.addAction(t("export_zip"), self.export_win_button)
        file_menu.addSeparator()
        file_menu.addAction(t("exit"), self.close)
        
        # EDIT MENU
        edit_menu = menubar.addMenu(t("edit"))
        edit_menu.addAction(t("rename_group"), self.edit_selected_group)
        edit_menu.addAction(t("delete_group"), self.delete_selected_group)
        edit_menu.addSeparator()
        edit_menu.addAction(t("delete_window"), self.delete_selected_window)
        
        view_menu = menubar.addMenu(t("view"))
        view_menu.addAction(t("open_selected"), self.open_win)
        view_menu.addAction(t("move_to_group"), self.move_selected_to_group)
        
        # SETTINGS MENU
        settings_menu = menubar.addMenu(t("settings"))
        settings_menu.addAction(t("appearance"), self.show_appearance_settings)
        settings_menu.addAction(t("change_language"), self.show_language_dialog)
        
        # ===== HEADER =====
        self.header = QLabel(f"<b>{t('my_workspace')}</b>")
        self.header.setStyleSheet("font-size: 18px; padding: 8px 0px; font-weight: bold;")
        lay.addWidget(self.header)
        
        # Central tree widget for grouped projects
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([t("windows_groups")])
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.doubleClicked.connect(self.on_tree_double_click)
        lay.addWidget(self.tree)
        
        # Need to keep python tracking active references to subwindows to stop garbage collection
        self.active_windows = [] 

        self.refresh()
        
        # Connect language change signal for real-time UI refresh
        language_signal = get_language_signal()
        language_signal.connect(self.on_language_changed)
        
        # Center window on screen
        self.center_on_screen()

    def center_on_screen(self):
        """Center the window on the screen."""
        from PySide6.QtWidgets import QApplication
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
    
    def on_language_changed(self, language_code):
        """Called when language changes - refresh all translations immediately."""
        self.refresh()
        self.update_menu_bar_text()
    
    def update_menu_bar_text(self):
        """Update all menu bar text with new translations."""
        menubar = self.menuBar()
        menubar.clear()
        
        # FILE MENU
        file_menu = menubar.addMenu(t("file"))
        file_menu.addAction(t("new_window"), self.new_win)
        file_menu.addAction(t("new_group"), self.create_new_group)
        file_menu.addSeparator()
        file_menu.addAction(t("import_zip"), self.import_win)
        file_menu.addAction(t("export_zip"), self.export_win_button)
        file_menu.addSeparator()
        file_menu.addAction(t("exit"), self.close)
        
        # EDIT MENU
        edit_menu = menubar.addMenu(t("edit"))
        edit_menu.addAction(t("rename_group"), self.edit_selected_group)
        edit_menu.addAction(t("delete_group"), self.delete_selected_group)
        edit_menu.addSeparator()
        edit_menu.addAction(t("delete_window"), self.delete_selected_window)
        
        # VIEW MENU
        view_menu = menubar.addMenu(t("view"))
        view_menu.addAction(t("open_selected"), self.open_win)
        view_menu.addAction(t("move_to_group"), self.move_selected_to_group)
        
        # SETTINGS MENU
        settings_menu = menubar.addMenu(t("settings"))
        settings_menu.addAction(t("appearance"), self.show_appearance_settings)
        settings_menu.addAction(t("change_language"), self.show_language_dialog)

    def refresh(self):
        """Load and display all groups and windows in tree structure."""
        # Update header and tree labels with current language
        self.header.setText(f"<b>{t('my_workspace')}</b>")
        self.tree.setHeaderLabels([t("windows_groups")])
        
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
            QMessageBox.warning(self, t("selection_required"), t("please_select_group"))
            return
        self.rename_group(group_name)

    def delete_selected_group(self):
        """Delete selected group."""
        group_name = self.get_selected_group()
        if not group_name:
            QMessageBox.warning(self, t("selection_required"), t("please_select_group"))
            return
        self.delete_group(group_name)

    def delete_selected_window(self):
        """Delete selected window."""
        window_id = self.get_selected_window()
        if not window_id:
            QMessageBox.warning(self, t("selection_required"), f"{t('please_select_window')} delete!")
            return
        self.delete_window(window_id)

    def move_selected_to_group(self):
        """Move selected window to group."""
        window_id = self.get_selected_window()
        if not window_id:
            QMessageBox.warning(self, t("selection_required"), f"{t('please_select_window')} move!")
            return
        self.move_window_to_group(window_id)

    def new_win(self):
        n, ok = QInputDialog.getText(self, t("new_workspace"), t("enter_window_name"))
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
        path, _ = QFileDialog.getOpenFileName(self, t("import_zip"), "", "Zip Files (*.zip)")
        if not path: 
            return
        
        n, ok = QInputDialog.getText(self, t("import_workspace"), t("choose_name"))
        if ok and n:
            n = n.replace(" ", "_")
            try:
                package_manager.import_window(path, n)
                # Add to Ungrouped by default
                group_manager.add_window_to_group(n, "Ungrouped")
                QMessageBox.information(self, t("success"), f"Project {n} {t('successfully_imported')}")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, t("error"), f"{t('failed_to_import')}:\n{e}")

    def export_win_button(self):
        """Export a selected window to ZIP."""
        window_id = self.get_selected_window()
        if not window_id:
            QMessageBox.warning(self, t("selection_required"), f"{t('please_select_window')} export!")
            return
        self.export_window(window_id)
    
    def create_new_group(self):
        """Create a new group."""
        group_name, ok = QInputDialog.getText(self, t("create_group_title"), t("group_name"))
        if ok and group_name:
            group_name = group_name.strip()
            if group_manager.create_group(group_name):
                self.refresh()
            else:
                QMessageBox.warning(self, t("error"), f"{t('group_exists')}")

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
            edit_act = menu.addAction(t("rename_group"))
            delete_act = menu.addAction(t("delete_group"))
            menu.addSeparator()
            add_win_to_group = menu.addAction(t("add_new_window"))
            
            action = menu.exec(self.tree.mapToGlobal(pos))
            
            if action == edit_act:
                self.rename_group(item_name)
            elif action == delete_act:
                self.delete_group(item_name)
            elif action == add_win_to_group:
                self.new_win_in_group(item_name)
        
        elif item_type == "window":
            # Options for windows
            open_act = menu.addAction(t("open_window"))
            menu.addSeparator()
            delete_act = menu.addAction(t("delete_window"))
            menu.addSeparator()
            move_act = menu.addAction(t("move_window_group"))
            export_act = menu.addAction(t("export_zip_item"))
            
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
        new_name, ok = QInputDialog.getText(self, t("rename_group_title"), f"{t('new_name_for')} '{old_name}':")
        if ok and new_name:
            if group_manager.rename_group(old_name, new_name):
                self.refresh()
            else:
                QMessageBox.warning(self, t("error"), t("could_not_rename_group"))
    
    def delete_group(self, group_name):
        """Delete a group (moves windows to Ungrouped)."""
        reply = QMessageBox.question(self, t("confirm_deletion"), 
                                     t("are_you_sure_delete_group"))
        if reply == QMessageBox.Yes:
            group_manager.delete_group(group_name)
            self.refresh()
    
    def delete_window(self, window_id):
        """Delete a window."""
        reply = QMessageBox.question(self, t("delete_window_title"), 
                                     t("are_you_sure_delete_window"))
        if reply == QMessageBox.Yes:
            try:
                win_folder = os.path.join(package_manager.BASE_PROJECT_DIR, window_id)
                if os.path.exists(win_folder):
                    shutil.rmtree(win_folder)
                group_manager.remove_window_from_groups(window_id)
                self.refresh()
                QMessageBox.information(self, t("success"), f"{t('window_deleted')}")
            except Exception as e:
                QMessageBox.critical(self, t("error"), f"{t('failed_to_export')}:\n{e}")
    
    def move_window_to_group(self, window_id):
        """Move window to a different group."""
        groups_data = group_manager.load_groups()
        group_names = [g["name"] for g in groups_data.get("groups", [])]
        
        # Create a simple dialog to select group
        group_name, ok = QInputDialog.getItem(self, t("move_window_title"), 
                                              f"{t('select_group_for')} '{window_id}':", 
                                              group_names, 0, False)
        if ok and group_name:
            group_manager.add_window_to_group(window_id, group_name)
            self.refresh()
    
    def new_win_in_group(self, group_name):
        """Create a new window and add it to specified group."""
        n, ok = QInputDialog.getText(self, t("new_workspace"), t("enter_window_name"))
        if ok and n:
            n = n.replace(" ", "_")
            group_manager.add_window_to_group(n, group_name)
            w = CustomWindow(n)
            w.show()
            self.active_windows.append(w)
            self.refresh()
    
    def export_window(self, window_id):
        """Export a window to ZIP."""
        dest, _ = QFileDialog.getSaveFileName(self, t("export_zip"), 
                                              window_id + "_export.zip", "Zip Files (*.zip)")
        if dest:
            try:
                package_manager.export_window(window_id, dest)
                QMessageBox.information(self, t("success"), f"{t('project')} '{window_id}' {t('successfully_exported')}!")
            except Exception as e:
                QMessageBox.critical(self, t("error"), f"{t('failed_to_export')}:\n{e}")
    
    def show_appearance_settings(self):
        """Show theme selection dialog."""
        tm = theme_manager.get_theme_manager()
        
        # Create theme selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(t("appearance"))
        dialog.resize(300, 140)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Label
        label = QLabel(t("select_theme") + ":")
        layout.addWidget(label)
        
        # Combo box for theme selection
        combo = QComboBox()
        available_themes = tm.list_themes_with_names()
        for theme_id, theme_name in available_themes:
            combo.addItem(theme_name, theme_id)
        
        # Set current theme
        current_idx = combo.findData(tm.current_theme)
        if current_idx >= 0:
            combo.setCurrentIndex(current_idx)
        
        layout.addWidget(combo)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton(t("close"))
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        if dialog.exec():
            selected_theme_id = combo.currentData()
            tm.set_current_theme(selected_theme_id)
            # Apply theme to current dashboard
            self.apply_theme(selected_theme_id)
            QMessageBox.information(self, t("success"), t("theme_applied").format(theme_name=combo.currentText()))
    
    def apply_theme(self, theme_id):
        """Apply a theme to the entire application (dashboard + all open project windows)."""
        from PySide6.QtWidgets import QApplication
        tm = theme_manager.get_theme_manager()
        stylesheet = tm.get_stylesheet(theme_id)
        # Apply at application level so ALL windows inherit
        QApplication.instance().setStyleSheet(stylesheet)
        # Save the theme preference
        tm.save_theme_preference()
        # Clean up any closed windows from the tracking list
        self.active_windows = [w for w in self.active_windows if w.isVisible()]
    
    def show_language_dialog(self):
        """Show language selection dialog."""
        translator = get_translator()
        current_lang = translator.get_current_language_name()
        
        # Create language selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(t("select_language"))
        dialog.resize(280, 120)  # Much smaller dialog
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Label
        label = QLabel(t("select_language") + ":")
        layout.addWidget(label)
        
        # Combo box for language selection
        combo = QComboBox()
        combo.addItems(translator.available_languages)
        combo.setCurrentText(current_lang)
        layout.addWidget(combo)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton(t("exit"))
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        if dialog.exec():
            selected_lang = combo.currentText()
            if translator.set_language(selected_lang):
                # Language changed signal will trigger automatic refresh
                pass
