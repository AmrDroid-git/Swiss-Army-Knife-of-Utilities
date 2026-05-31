import json
import os
import shutil
from PySide6.QtCore import QPoint
from app.widgets import (
    BaseComponent, WidgetButton, WidgetIText, WidgetOText,
    WidgetIFileLink, WidgetOFileLink, WidgetIFolderLink, WidgetOFolderLink,
    WidgetConsole, WidgetInteractiveConsole, WidgetLabel, WidgetRequirementsLink,
    WidgetSelect
)

BASE_PROJECT_DIR = "user_workspaces"

def build_window_data(canvas, save_width=None, save_height=None):
    """
    Builds the JSON data of a window.

    If save_width/save_height are provided, widget geometry is converted from
    the current visible canvas size to the logical save canvas size.

    This fixes the problem where widgets become smaller after saving while
    Design Mode is open, because the sidebar makes the visible canvas smaller.
    """
    current_width = max(1, canvas.width())
    current_height = max(1, canvas.height())

    target_width = save_width if save_width and save_width > 0 else current_width
    target_height = save_height if save_height and save_height > 0 else current_height

    scale_x = target_width / current_width
    scale_y = target_height / current_height

    data = []

    for c in canvas.findChildren(BaseComponent):
        if getattr(c, "is_template", False):
            continue

        item = c.to_dict()

        item["x"] = int(round(item.get("x", c.x()) * scale_x))
        item["y"] = int(round(item.get("y", c.y()) * scale_y))
        item["width"] = max(1, int(round(item.get("width", c.width()) * scale_x)))
        item["height"] = max(1, int(round(item.get("height", c.height()) * scale_y)))

        data.append(item)

    return data


def save_window(win_id, canvas, save_width=None, save_height=None):
    if not os.path.exists(BASE_PROJECT_DIR):
        os.makedirs(BASE_PROJECT_DIR, exist_ok=True)

    win_folder = os.path.join(BASE_PROJECT_DIR, win_id)
    if not os.path.exists(win_folder):
        os.makedirs(win_folder, exist_ok=True)

    data = build_window_data(
        canvas,
        save_width=save_width,
        save_height=save_height
    )

    with open(os.path.join(win_folder, "config.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def clear_canvas(canvas):
    """Remove all real widgets from the canvas without touching toolbox templates."""
    for child in canvas.findChildren(BaseComponent):
        if getattr(child, "is_template", False):
            continue

        child.hide()
        child.setParent(None)
        child.deleteLater()


def create_widget_from_item(item, canvas):
    """Create one widget instance from a saved config item."""
    pos = QPoint(item.get("x", 0), item.get("y", 0))
    comp_type = item.get("comp_type")

    if comp_type == "widget_button":
        return WidgetButton(canvas, pos)
    if comp_type == "widget_label":
        return WidgetLabel(canvas, pos)
    if comp_type == "widget_i_text":
        return WidgetIText(canvas, pos)
    if comp_type == "widget_o_text":
        return WidgetOText(canvas, pos)
    if comp_type == "widget_select":
        return WidgetSelect(canvas, pos)
    if comp_type == "widget_i_file_link":
        return WidgetIFileLink(canvas, pos)
    if comp_type == "widget_o_file_link":
        return WidgetOFileLink(canvas, pos)
    if comp_type == "widget_i_folder_link":
        return WidgetIFolderLink(canvas, pos)
    if comp_type == "widget_o_folder_link":
        return WidgetOFolderLink(canvas, pos)
    if comp_type == "widget_console":
        return WidgetConsole(canvas, pos)
    if comp_type == "widget_interactive_console":
        return WidgetInteractiveConsole(canvas, pos)
    if comp_type == "widget_requirements_link":
        return WidgetRequirementsLink(canvas, pos)

    return None


def load_window_data(data, canvas, edit_mode=False):
    """Load widgets from already parsed window data."""
    for item in data:
        obj = create_widget_from_item(item, canvas)

        if obj:
            obj.from_dict(item)
            obj.is_template = False
            obj.set_edit_mode(edit_mode)
            obj.show()


def load_window(win_id, canvas):
    path = os.path.join(BASE_PROJECT_DIR, win_id, "config.json")
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

    clear_canvas(canvas)
    load_window_data(data, canvas, edit_mode=False)

def export_window(win_id, output_zip_path):
    """ Compresses an entire window bundle securely into a .zip file. """
    win_folder = os.path.join(BASE_PROJECT_DIR, win_id)
    if not os.path.exists(win_folder):
        raise FileNotFoundError("Window bundle does not exist on disk.")
    
    # shutil.make_archive adds the .zip extension automatically
    base_name = os.path.splitext(output_zip_path)[0]
    shutil.make_archive(base_name, 'zip', win_folder)

def import_window(zip_path, new_win_id):
    """ Decompresses an imported .zip bundle straight into the live project directory. """
    win_folder = os.path.join(BASE_PROJECT_DIR, new_win_id)
    if os.path.exists(win_folder):
        raise FileExistsError("A window with this exact name already exists in your workspace!")
    
    os.makedirs(win_folder, exist_ok=True)
    shutil.unpack_archive(zip_path, win_folder, 'zip')
