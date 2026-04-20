from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QMenu, QInputDialog, QDialog, 
    QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from app.widgets.base_widget import BaseComponent
from app.translator import t


class WidgetSelect(BaseComponent):
    """
    A dropdown select field widget for allowing users to choose 
    from predefined options.
    
    Useful for script arguments where only specific values are allowed.
    Example: Format selection (mp3, mp4, wav) for a video converter.
    
    Features:
    - Dropdown combo box UI
    - Configurable options list
    - Right-click to manage options or change appearance
    - Argument ordering for script execution
    - Font customization
    """
    
    def __init__(self, parent, pos):
        super().__init__(parent, "widget_select", pos)
        self.field_type = "select_field"
        self.mode = "input"
        
        # Setup widget size and layout
        self.resize(220, 45)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the combo box (dropdown)
        self.combo = QComboBox()
        self.combo.setPlaceholderText(t("select_option"))

        
        self.layout.addWidget(self.combo)
        
        # Initialize default properties in the properties dict
        if "options" not in self.properties:
            self.properties["options"] = ["Option 1", "Option 2", "Option 3"]
        
        # Populate combo box with initial options
        self._populate_combo_box()

    def _populate_combo_box(self):
        """Refills the combo box from the options list."""
        self.combo.clear()
        options = self.properties.get("options", [])
        self.combo.addItems(options)

    def contextMenuEvent(self, event):
        """
        Right-click context menu handling.
        DUAL BEHAVIOR:
        - Edit Mode: Full menu with configuration options
        - Run Mode: Simple clear operation
        """
        if not self.is_edit_mode:
            # In RUN MODE: Just clear option
            menu = QMenu(self)
            clear_act = menu.addAction(t("clear_content"))
            if menu.exec(event.globalPos()) == clear_act:
                self.combo.setCurrentIndex(-1)
            return
        
        # In EDIT MODE: Full customization menu
        menu = QMenu(self)
        
        # Widget-specific actions
        edit_options_act = menu.addAction("Edit Select Options...")
        edit_default_act = menu.addAction(t("edit_default_value"))
        
        # Argument ordering
        order_act = menu.addAction(t("set_arg_order").format(order=self.arg_order))
        
        # Delegate to base for standard actions (Font, Resize, Delete)
        font_act, res_act, del_act = self.add_base_actions(menu)
        
        action = menu.exec(event.globalPos())
        
        # Handle custom actions
        if action == edit_options_act:
            self._open_options_editor()
            
        elif action == edit_default_act:
            current = self.combo.currentText()
            idx, ok = QInputDialog.getInt(
                self,
                t("edit_dialog_title"),
                "Select default option index (0-based):",
                self.combo.currentIndex(),
                -1,
                len(self.properties.get("options", [])) - 1
            )
            if ok:
                self.combo.setCurrentIndex(idx)
                
        elif action == order_act:
            val, ok = QInputDialog.getInt(
                self,
                t("order_dialog_title"),
                t("order_dialog_prompt"),
                self.arg_order,
                0,
                100
            )
            if ok:
                self.arg_order = val
        
        # Let base class handle standard actions
        self.handle_base_actions(action, font_act, res_act, del_act)

    def _open_options_editor(self):
        """
        Opens a dialog window to manage select field options.
        Users can add, remove, and reorder options here.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Select Options")
        dialog.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # List widget to display current options
        list_widget = QListWidget()
        options = self.properties.get("options", [])
        for option in options:
            item = QListWidgetItem(option)
            item.setFlags(item.flags() | Qt.ItemIsEditable)  # Make editable
            list_widget.addItem(item)
        layout.addWidget(list_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Add button
        def add_option():
            new_opt, ok = QInputDialog.getText(
                dialog,
                "Add Option",
                "Enter new option text:"
            )
            if ok and new_opt.strip():
                item = QListWidgetItem(new_opt)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                list_widget.addItem(item)
        
        add_btn = QPushButton("Add Option")
        add_btn.clicked.connect(add_option)
        button_layout.addWidget(add_btn)
        
        # Remove button
        def remove_option():
            current_row = list_widget.currentRow()
            if current_row >= 0:
                list_widget.takeItem(current_row)
            else:
                QMessageBox.warning(dialog, "Warning", "Select an option to remove first")
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(remove_option)
        button_layout.addWidget(remove_btn)
        
        layout.addLayout(button_layout)
        
        # OK / Cancel buttons
        ok_cancel_layout = QHBoxLayout()
        
        def save_changes():
            # Extract all current items from list widget
            updated_options = []
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                updated_options.append(item.text())
            
            if not updated_options:
                QMessageBox.warning(dialog, "Error", "You must have at least one option!")
                return
            
            # Update properties
            self.properties["options"] = updated_options
            self._populate_combo_box()  # Refresh combo box UI
            dialog.accept()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(save_changes)
        ok_cancel_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        ok_cancel_layout.addWidget(cancel_btn)
        
        layout.addLayout(ok_cancel_layout)
        
        dialog.exec()

    def apply_font(self, font):
        """
        Override base to apply font to the inner QComboBox and its dropdown.
        Called when user selects "Change Font" from context menu.
        """
        font_str = f"{font.family()}, Arial, sans-serif"
        # Apply font to the main combobox
        self.combo.setFont(font)
        # Also apply to the dropdown view/list
        if self.combo.view():
            self.combo.view().setFont(font)
        # Use stylesheet to ensure font overrides theme stylesheets
        self.combo.setStyleSheet(f"QComboBox {{font-family: '{font_str}'; font-size: {font.pointSize()}pt !important;}}")
        # Also apply to the model
        if self.combo.model():
            self.combo.model().layoutChanged.emit()

    def get_value(self):
        """
        Called by button's execute() method to fetch the selected option.
        Gets passed to the script as sys.argv[arg_order]
        """
        return self.combo.currentText()

    def set_value(self, val):
        """
        Programmatically set the selected value.
        Finds the index of the value in options and selects it.
        """
        index = self.combo.findText(val)
        if index >= 0:
            self.combo.setCurrentIndex(index)
    
    def to_dict(self):
        """
        Save to JSON. Includes the options list and current selection.
        Called when user saves the window layout.
        """
        data = super().to_dict()  # Get base properties (position, size, font, etc)
        data["value"] = self.combo.currentText()  # Current selection
        data["properties"]["options"] = self.properties.get("options", [])
        return data

    def from_dict(self, data):
        """
        Restore from JSON. Rehydrates the options and selection.
        Called when user loads a saved window layout.
        """
        super().from_dict(data)  # Restore position, size, font, arg_order
        
        # Restore options list
        if "properties" in data and "options" in data["properties"]:
            self.properties["options"] = data["properties"]["options"]
            self._populate_combo_box()
        
        # Restore selected value
        if "value" in data:
            self.set_value(data["value"])
