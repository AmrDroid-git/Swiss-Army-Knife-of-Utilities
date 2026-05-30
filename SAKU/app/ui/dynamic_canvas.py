import os
import json
from PySide6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QApplication, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from app.widgets import (
    BaseComponent, WidgetButton, WidgetIText, WidgetOText,
    WidgetIFileLink, WidgetOFileLink, WidgetIFolderLink, WidgetOFolderLink,
    WidgetConsole, WidgetInteractiveConsole, WidgetLabel, WidgetRequirementsLink,
    WidgetSelect
)
from app.ui.edit_palette import ToolboxItem
from app.core import package_manager
from app.core.script_engine import ScriptEngine
from app.translator import t


class EditorCanvas(QFrame):
    def __init__(self, script_engine):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("EditorCanvas { border: 2px dashed #9ca3af; border-radius: 8px; }")
        self.is_edit_mode = False
        self.script_engine = script_engine
        self._loading_in_progress = False

    def set_loading_state(self, state: bool):
        self._loading_in_progress = state

    def _refresh_relative_geometry_for_all_widgets(self):
        for c in self.findChildren(BaseComponent):
            if hasattr(c, "update_relative_geometry"):
                try:
                    c.update_relative_geometry()
                except Exception:
                    pass

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if self._loading_in_progress:
            return

        cur_w = event.size().width()
        cur_h = event.size().height()
        if cur_w <= 0 or cur_h <= 0:
            return

        for c in self.findChildren(BaseComponent):
            if (
                hasattr(c, "_rel_x")
                and hasattr(c, "_rel_y")
                and hasattr(c, "_rel_w")
                and hasattr(c, "_rel_h")
                and c._rel_w > 0
                and c._rel_h > 0
            ):
                new_x = int(c._rel_x * cur_w)
                new_y = int(c._rel_y * cur_h)
                new_w = int(c._rel_w * cur_w)
                new_h = int(c._rel_h * cur_h)

                new_w = max(40, new_w)
                new_h = max(20, new_h)

                c.setGeometry(new_x, new_y, new_w, new_h)

    def set_edit_mode(self, state):
        self.is_edit_mode = state

        if state:
            self.setStyleSheet("EditorCanvas { border: 2px dashed #6366f1; border-radius: 8px; }")
        else:
            self.setCursor(Qt.ArrowCursor)
            self.setStyleSheet("EditorCanvas { border: 2px dashed #9ca3af; border-radius: 8px; }")

        for c in self.findChildren(BaseComponent):
            try:
                c.set_edit_mode(state)
            except Exception:
                pass

    def dragEnterEvent(self, event):
        if self.is_edit_mode and event.mimeData().hasFormat("application/x-widget-template"):
            event.acceptProposedAction()

    def contextMenuEvent(self, event):
        if not self.is_edit_mode:
            from PySide6.QtWidgets import QMenu

            menu = QMenu(self)
            clear_act = menu.addAction(t("clear_all_fields"))

            if menu.exec(event.globalPos()) == clear_act:
                for c in self.findChildren(BaseComponent):
                    if hasattr(c, "clear_text"):
                        c.clear_text()
                    elif hasattr(c, "set_value"):
                        c.set_value("")

    def dropEvent(self, event):
        if not self.is_edit_mode:
            return

        pos = event.position().toPoint()
        item_data = event.mimeData().data("application/x-widget-template")
        tid = bytes(item_data).decode("utf-8")

        obj = None

        if tid == "widget_button":
            obj = WidgetButton(self, pos)
            obj.run_script_requested.connect(self.script_engine.run_script)

        elif tid == "widget_label":
            obj = WidgetLabel(self, pos)

        elif tid == "widget_i_text":
            obj = WidgetIText(self, pos)

        elif tid == "widget_o_text":
            obj = WidgetOText(self, pos)

        elif tid == "widget_select":
            obj = WidgetSelect(self, pos)

        elif tid == "widget_i_file_link":
            obj = WidgetIFileLink(self, pos)

        elif tid == "widget_o_file_link":
            obj = WidgetOFileLink(self, pos)

        elif tid == "widget_i_folder_link":
            obj = WidgetIFolderLink(self, pos)

        elif tid == "widget_o_folder_link":
            obj = WidgetOFolderLink(self, pos)

        elif tid == "widget_console":
            obj = WidgetConsole(self, pos)
            self.script_engine.stdout_emitted.connect(obj.append_text)
            self.script_engine.error_emitted.connect(obj.append_text)

        elif tid == "widget_interactive_console":
            obj = WidgetInteractiveConsole(self, pos)
            self.script_engine.stdout_emitted.connect(obj.append_text)
            self.script_engine.error_emitted.connect(obj.append_text)
            obj.stdin_submitted.connect(self.script_engine.send_input)

        elif tid == "widget_requirements_link":
            obj = WidgetRequirementsLink(self, pos)

        if obj:
            obj.is_template = False
            obj.set_edit_mode(True)
            obj.show()
            QTimer.singleShot(0, lambda: self._safe_update_relative_geometry(obj))
            event.acceptProposedAction()

    def _safe_update_relative_geometry(self, widget):
        if widget is None:
            return
        if hasattr(widget, "update_relative_geometry"):
            try:
                widget.update_relative_geometry()
            except Exception:
                pass


class CustomWindow(QWidget):
    def __init__(self, window_id):
        super().__init__()
        self.window_id = window_id
        self.setWindowTitle(f"Project Workspace: {window_id.replace('_', ' ')}")

        self._project_loaded_once = False
        self._window_state_restored = False
        self._last_saved_project_snapshot = None

        screen = QApplication.primaryScreen().geometry()
        window_width = int(screen.width() * 0.7)
        window_height = int(screen.height() * 0.7)

        self.resize(window_width, window_height)

        center_x = (screen.width() - window_width) // 2
        center_y = (screen.height() - window_height) // 2
        self.move(center_x, center_y)

        self.engine = ScriptEngine()
        self.layout = QVBoxLayout(self)

        nav = QHBoxLayout()

        self.edit_btn = QPushButton(t("design_mode"))
        self.edit_btn.setCheckable(True)
        self.edit_btn.clicked.connect(self.toggle)

        save_btn = QPushButton(t("save_project"))
        save_btn.clicked.connect(self.save_project)

        title_label = QLabel(window_id.replace("_", " ").upper())
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 4px 0px;")

        nav.addWidget(title_label)
        nav.addStretch()
        nav.addWidget(self.edit_btn)
        nav.addWidget(save_btn)
        self.layout.addLayout(nav)

        self.content = QHBoxLayout()

        self.canvas = EditorCanvas(self.engine)

        self.sidebar_container = QScrollArea()
        self.sidebar_container.setWidgetResizable(True)
        self.sidebar_container.setMinimumWidth(200)
        self.sidebar_container.setMaximumWidth(250)

        self.sidebar = QWidget()
        self.sidebar_container.setWidget(self.sidebar)

        s_lay = QVBoxLayout(self.sidebar)
        s_lay.setSpacing(4)
        s_lay.setContentsMargins(4, 4, 4, 4)

        s_lay.addWidget(ToolboxItem(t("script_trigger"), "widget_button"))
        s_lay.addWidget(ToolboxItem(t("title_label"), "widget_label"))
        s_lay.addWidget(ToolboxItem(t("text_input"), "widget_i_text"))
        s_lay.addWidget(ToolboxItem(t("text_output"), "widget_o_text"))
        s_lay.addWidget(ToolboxItem(t("select_field"), "widget_select"))
        s_lay.addWidget(ToolboxItem(t("file_input"), "widget_i_file_link"))
        s_lay.addWidget(ToolboxItem(t("folder_input"), "widget_i_folder_link"))
        s_lay.addWidget(ToolboxItem(t("safe_output"), "widget_o_folder_link"))
        s_lay.addWidget(ToolboxItem(t("system_console"), "widget_console"))
        s_lay.addWidget(ToolboxItem(t("interactive_console"), "widget_interactive_console"))
        s_lay.addWidget(ToolboxItem(t("requirements_link"), "widget_requirements_link"))
        s_lay.addStretch()

        self.content.addWidget(self.canvas)
        self.content.addWidget(self.sidebar_container)
        self.layout.addLayout(self.content)

        self.sidebar_container.hide()

        self._restore_window_state()

    def _get_window_state_file(self):
        base_dir = os.path.join(package_manager.BASE_PROJECT_DIR, self.window_id)
        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, "window_state.json")
    
    def _get_logical_save_canvas_size(self):
        """
        Returns the canvas size that should be used when saving.

        In Design Mode, the sidebar is visible and makes the real canvas smaller.
        But saved widget geometry should be based on the full canvas size,
        otherwise widgets become smaller after reopening the workspace.
        """
        canvas_width = max(1, self.canvas.width())
        canvas_height = max(1, self.canvas.height())

        if self.edit_btn.isChecked() and self.sidebar_container.isVisible():
            spacing = self.content.spacing()
            if spacing < 0:
                spacing = 6

            logical_width = canvas_width + self.sidebar_container.width() + spacing
            return logical_width, canvas_height

        return canvas_width, canvas_height
    
    def _get_project_snapshot(self):
        """Returns a stable JSON snapshot of the logical saved canvas state."""
        save_width, save_height = self._get_logical_save_canvas_size()

        data = package_manager.build_window_data(
            self.canvas,
            save_width=save_width,
            save_height=save_height
        )

        data.sort(
            key=lambda item: json.dumps(
                item,
                sort_keys=True,
                ensure_ascii=False
            )
        )

        return json.dumps(data, sort_keys=True, ensure_ascii=False)

    def _mark_project_as_saved(self):
        """Stores the latest saved canvas snapshot in memory."""
        self._last_saved_project_snapshot = self._get_project_snapshot()

    def _has_unsaved_project_changes(self):
        """Checks if the current canvas is different from the last saved version."""
        if self._last_saved_project_snapshot is None:
            return False

        return self._get_project_snapshot() != self._last_saved_project_snapshot

    def _enable_edit_mode_after_cancel_close(self):
        """Cancel closing and return the user to edit mode."""
        self.edit_btn.setChecked(True)
        self.canvas.set_edit_mode(True)
        self.sidebar_container.show()

    def _save_window_state(self):
        try:
            state_data = {
                "x": self.x(),
                "y": self.y(),
                "width": self.width(),
                "height": self.height(),
                "maximized": self.isMaximized(),
                "fullscreen": self.isFullScreen()
            }

            with open(self._get_window_state_file(), "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=4)
        except Exception as e:
            print(f"Error saving window state: {e}")

    def _restore_window_state(self):
        try:
            state_file = self._get_window_state_file()
            if not os.path.exists(state_file):
                return

            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            x = data.get("x")
            y = data.get("y")
            w = data.get("width")
            h = data.get("height")

            if isinstance(w, int) and isinstance(h, int) and w > 100 and h > 100:
                self.resize(w, h)

            if isinstance(x, int) and isinstance(y, int):
                self.move(x, y)

            self._saved_maximized = bool(data.get("maximized", False))
            self._saved_fullscreen = bool(data.get("fullscreen", False))
            self._window_state_restored = True

        except Exception as e:
            print(f"Error restoring window state: {e}")

    def showEvent(self, event):
        super().showEvent(event)

        if self._window_state_restored:
            if getattr(self, "_saved_fullscreen", False):
                self.showFullScreen()
            elif getattr(self, "_saved_maximized", False):
                self.showMaximized()

            self._window_state_restored = False

        if not self._project_loaded_once:
            self._project_loaded_once = True
            QTimer.singleShot(0, self._load_project_after_show)

    def _load_project_after_show(self):
        self.canvas.set_loading_state(True)

        try:
            package_manager.load_window(self.window_id, self.canvas)
            self._reconnect_loaded_widgets()
            self.canvas._refresh_relative_geometry_for_all_widgets()

        finally:
            self.canvas.set_loading_state(False)
            QTimer.singleShot(0, self.canvas._refresh_relative_geometry_for_all_widgets)
            QTimer.singleShot(0, self._mark_project_as_saved)

    def _reconnect_loaded_widgets(self):
        for c in self.canvas.findChildren(BaseComponent):
            if isinstance(c, WidgetButton):
                c.run_script_requested.connect(self.engine.run_script)

            elif isinstance(c, WidgetConsole):
                try:
                    self.engine.stdout_emitted.connect(c.append_text)
                    self.engine.error_emitted.connect(c.append_text)
                except Exception:
                    pass

            elif isinstance(c, WidgetInteractiveConsole):
                try:
                    self.engine.stdout_emitted.connect(c.append_text)
                    self.engine.error_emitted.connect(c.append_text)
                    c.stdin_submitted.connect(self.engine.send_input)
                except Exception:
                    pass

    def toggle(self):
        state = self.edit_btn.isChecked()
        self.canvas.set_edit_mode(state)
        self.sidebar_container.setVisible(state)

    def save_project(self):
        save_width, save_height = self._get_logical_save_canvas_size()

        package_manager.save_window(
            self.window_id,
            self.canvas,
            save_width=save_width,
            save_height=save_height
        )

        if hasattr(self, "_mark_project_as_saved"):
            self._mark_project_as_saved()

    def closeEvent(self, event):
        if self._has_unsaved_project_changes():
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle(t("unsaved_changes_title", "Unsaved changes"))
            msg.setText(t("unsaved_changes_message", "You have unsaved changes in this window."))
            msg.setInformativeText(
                t(
                    "unsaved_changes_question",
                    "Do you want to save before quitting, go back to edit mode, or quit without saving?"
                )
            )

            save_quit_btn = msg.addButton(
                t("save_and_quit", "Save & Quit"),
                QMessageBox.AcceptRole
            )
            back_edit_btn = msg.addButton(
                t("back_to_edit_mode", "Back to edit mode"),
                QMessageBox.RejectRole
            )
            quit_btn = msg.addButton(
                t("quit_without_saving", "Quit"),
                QMessageBox.DestructiveRole
            )

            msg.setDefaultButton(save_quit_btn)
            msg.setEscapeButton(back_edit_btn)
            msg.exec()

            clicked_button = msg.clickedButton()

            if clicked_button == back_edit_btn:
                self._enable_edit_mode_after_cancel_close()
                event.ignore()
                return

            if clicked_button == save_quit_btn:
                try:
                    self.save_project()
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        t("error", "Error"),
                        f"Could not save the project:\n{e}"
                    )
                    event.ignore()
                    return

            elif clicked_button == quit_btn:
                pass

            else:
                event.ignore()
                return

        self.engine.kill()

        try:
            self._save_window_state()
        except Exception as e:
            print(f"Error during close save: {e}")

        event.accept()