import json
import os
import shutil
import tempfile
import re
import uuid
from PySide6.QtCore import QPoint
from app.widgets import (
    BaseComponent, WidgetButton, WidgetIText, WidgetOText,
    WidgetIFileLink, WidgetOFileLink, WidgetIFolderLink, WidgetOFolderLink,
    WidgetConsole, WidgetInteractiveConsole, WidgetLabel, WidgetRequirementsLink,
    WidgetSelect
)

BASE_PROJECT_DIR = "user_workspaces"
WINDOW_META_FILE = "window.json"

WINDOW_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
}


def sanitize_window_id(raw_name):
    """Return a Windows-safe string. Used only for legacy names and export file names."""
    name = str(raw_name or "").strip()
    name = name.replace(" ", "_")
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip(" ._")

    if not name:
        name = "Untitled_Window"

    if name.upper() in WINDOW_RESERVED_NAMES:
        name = f"{name}_window"

    return name


def is_window_id(value):
    """Return True if the value looks like the new internal window id."""
    return bool(re.fullmatch(r"win_[0-9a-f]{12}", str(value or "")))


def generate_window_id():
    """Create a new safe internal id used as the workspace folder name."""
    os.makedirs(BASE_PROJECT_DIR, exist_ok=True)

    while True:
        window_id = f"win_{uuid.uuid4().hex[:12]}"
        if not os.path.exists(os.path.join(BASE_PROJECT_DIR, window_id)):
            return window_id


def get_window_folder(window_id):
    """Return the filesystem folder of a window by its internal id."""
    safe_id = sanitize_window_id(window_id)
    return os.path.join(BASE_PROJECT_DIR, safe_id)


def get_window_meta_path(window_id):
    return os.path.join(get_window_folder(window_id), WINDOW_META_FILE)


def ensure_window_metadata(window_id, display_name=None):
    """Make sure a window has window.json metadata."""
    os.makedirs(BASE_PROJECT_DIR, exist_ok=True)
    folder = get_window_folder(window_id)
    os.makedirs(folder, exist_ok=True)

    meta_path = os.path.join(folder, WINDOW_META_FILE)
    meta = {}

    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except (json.JSONDecodeError, OSError):
            meta = {}

    meta["id"] = window_id

    if display_name is not None and str(display_name).strip():
        meta["name"] = str(display_name).strip()
    elif not str(meta.get("name", "")).strip():
        meta["name"] = window_id

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)

    return meta


def get_window_metadata(window_id):
    """Read window metadata, creating it if it is missing."""
    return ensure_window_metadata(window_id)


def get_window_name(window_id):
    """Return the display name of a window."""
    meta = get_window_metadata(window_id)
    return meta.get("name", window_id)


def rename_window(window_id, new_name):
    """Rename only the visible window name. The folder/id stays unchanged."""
    new_name = str(new_name or "").strip()
    if not new_name:
        return False

    ensure_window_metadata(window_id, new_name)
    return True


def create_window(display_name):
    """Create a new workspace with a unique internal id and a user-facing name."""
    window_id = generate_window_id()
    folder = get_window_folder(window_id)
    os.makedirs(folder, exist_ok=True)

    config_path = os.path.join(folder, "config.json")
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)

    ensure_window_metadata(window_id, display_name)
    return window_id


def _legacy_folder_candidates(legacy_name):
    """Return possible old folders for a legacy window name."""
    candidates = []
    legacy_name = str(legacy_name or "")

    if legacy_name and not any(sep in legacy_name for sep in ("/", "\\")):
        candidates.append(os.path.join(BASE_PROJECT_DIR, legacy_name))

    safe_name = sanitize_window_id(legacy_name)
    candidates.append(os.path.join(BASE_PROJECT_DIR, safe_name))

    unique = []
    for folder in candidates:
        if folder not in unique:
            unique.append(folder)

    return unique


def migrate_legacy_window(legacy_name):
    """
    Convert an old name-based workspace into a new id-based workspace.

    Old code used the visible name as the folder name.
    New code uses win_xxxxx ids.
    """
    if is_window_id(legacy_name):
        ensure_window_metadata(legacy_name)
        return legacy_name

    display_name = str(legacy_name or "Untitled Window").strip() or "Untitled Window"

    existing_folder = None
    for candidate in _legacy_folder_candidates(display_name):
        if os.path.isdir(candidate):
            existing_folder = candidate
            break

    window_id = generate_window_id()
    new_folder = get_window_folder(window_id)

    if existing_folder:
        if os.path.abspath(existing_folder) != os.path.abspath(new_folder):
            shutil.move(existing_folder, new_folder)
    else:
        os.makedirs(new_folder, exist_ok=True)
        with open(os.path.join(new_folder, "config.json"), "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)

    ensure_window_metadata(window_id, display_name)
    return window_id


def list_window_ids():
    """Return every valid window id stored on disk."""
    if not os.path.exists(BASE_PROJECT_DIR):
        return []

    window_ids = []

    for name in os.listdir(BASE_PROJECT_DIR):
        folder = os.path.join(BASE_PROJECT_DIR, name)
        if not os.path.isdir(folder):
            continue

        if is_window_id(name):
            ensure_window_metadata(name)
            window_ids.append(name)
        else:
            window_ids.append(migrate_legacy_window(name))

    return window_ids


def build_window_data(canvas, save_width=None, save_height=None):
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


def save_window(window_id, canvas, save_width=None, save_height=None):
    os.makedirs(BASE_PROJECT_DIR, exist_ok=True)
    ensure_window_metadata(window_id)
    win_folder = get_window_folder(window_id)

    data = build_window_data(
        canvas,
        save_width=save_width,
        save_height=save_height
    )

    with open(os.path.join(win_folder, "config.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return window_id


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


def load_window(window_id, canvas):
    ensure_window_metadata(window_id)
    path = os.path.join(get_window_folder(window_id), "config.json")

    if not os.path.exists(path):
        clear_canvas(canvas)
        return

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

    clear_canvas(canvas)
    load_window_data(data, canvas, edit_mode=False)


def export_window(window_id, output_zip_path):
    """Compress an entire window bundle into a .zip file."""
    ensure_window_metadata(window_id)
    win_folder = get_window_folder(window_id)

    if not os.path.exists(win_folder):
        raise FileNotFoundError("Window bundle does not exist on disk.")

    base_name = os.path.splitext(output_zip_path)[0]
    shutil.make_archive(base_name, "zip", win_folder)


def import_window(zip_path, display_name):
    """Import a window zip into a new id-based workspace."""
    window_id = create_window(display_name)
    win_folder = get_window_folder(window_id)

    try:
        shutil.unpack_archive(zip_path, win_folder, "zip")
    except Exception:
        shutil.rmtree(win_folder, ignore_errors=True)
        raise

    ensure_window_metadata(window_id, display_name)
    return window_id


def _make_unique_window_id(preferred_win_id):
    """Backward compatible alias used by older import code."""
    return create_window(preferred_win_id)


def export_group(group_name, window_ids, output_zip_path):
    """Export a complete group with all its window folders into one ZIP file."""
    os.makedirs(BASE_PROJECT_DIR, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        windows_dir = os.path.join(temp_dir, "windows")
        os.makedirs(windows_dir, exist_ok=True)

        exported_windows = []

        for window_id in window_ids:
            ensure_window_metadata(window_id)
            src_folder = get_window_folder(window_id)

            if not os.path.isdir(src_folder):
                raise FileNotFoundError(f"Window '{window_id}' does not exist on disk.")

            dst_folder = os.path.join(windows_dir, window_id)
            shutil.copytree(src_folder, dst_folder)
            exported_windows.append({
                "id": window_id,
                "name": get_window_name(window_id)
            })

        manifest = {
            "type": "saku_group_export",
            "version": 2,
            "group_name": group_name,
            "windows": exported_windows
        }

        with open(os.path.join(temp_dir, "group_manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=4, ensure_ascii=False)

        base_name = os.path.splitext(output_zip_path)[0]
        shutil.make_archive(base_name, "zip", temp_dir)


def import_group(zip_path, new_group_name):
    """Import a group ZIP and copy all contained windows into the workspace."""
    os.makedirs(BASE_PROJECT_DIR, exist_ok=True)

    imported_windows = []

    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.unpack_archive(zip_path, temp_dir, "zip")

        manifest_path = os.path.join(temp_dir, "group_manifest.json")
        if not os.path.isfile(manifest_path):
            raise ValueError("This ZIP is not a SAKU group export.")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        if manifest.get("type") != "saku_group_export":
            raise ValueError("This ZIP is not a valid SAKU group export.")

        windows_dir = os.path.join(temp_dir, "windows")
        exported_windows = manifest.get("windows", [])

        for entry in exported_windows:
            if isinstance(entry, dict):
                old_window_id = entry.get("id")
                display_name = entry.get("name") or old_window_id or "Imported Window"
            else:
                old_window_id = str(entry)
                display_name = old_window_id

            src_folder = os.path.join(windows_dir, old_window_id)
            if not os.path.isdir(src_folder):
                raise FileNotFoundError(f"Missing window '{old_window_id}' in the group ZIP.")

            new_window_id = generate_window_id()
            dst_folder = get_window_folder(new_window_id)
            shutil.copytree(src_folder, dst_folder)
            ensure_window_metadata(new_window_id, display_name)
            imported_windows.append(new_window_id)

    return {
        "group_name": new_group_name,
        "windows": imported_windows
    }