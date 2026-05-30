"""
Group Manager: Handles organizing windows into collapsible groups.
Groups are stored in a JSON file for UI-only organization (no backend changes).
"""

import copy
import json
import os
from app.core.package_manager import BASE_PROJECT_DIR

GROUPS_FILE = os.path.join(BASE_PROJECT_DIR, "groups.json")
UNGROUPED_GROUP_NAME = "Ungrouped"

# Important: Ungrouped is NOT a permanent group anymore.
# It will be created only when a window really has no group.
DEFAULT_GROUPS = {
    "groups": []
}


def ensure_groups_file():
    """Create groups.json if it doesn't exist."""
    os.makedirs(BASE_PROJECT_DIR, exist_ok=True)

    if not os.path.exists(GROUPS_FILE):
        save_groups(copy.deepcopy(DEFAULT_GROUPS))


def load_groups():
    """Load groups from JSON file."""
    ensure_groups_file()

    try:
        with open(GROUPS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("groups", [])
            return data
    except (json.JSONDecodeError, IOError):
        return copy.deepcopy(DEFAULT_GROUPS)


def save_groups(data):
    """Save groups to JSON file."""
    os.makedirs(BASE_PROJECT_DIR, exist_ok=True)

    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def _ensure_group_in_data(groups_data, group_name):
    """Ensure a group exists inside an already loaded groups structure."""
    groups = groups_data.setdefault("groups", [])
    for group in groups:
        if group.get("name") == group_name:
            group.setdefault("expanded", True)
            group.setdefault("windows", [])
            return group, False

    new_group = {
        "name": group_name,
        "expanded": True,
        "windows": []
    }
    groups.append(new_group)
    return new_group, True


def ensure_group_exists(group_name=UNGROUPED_GROUP_NAME):
    """Create the group if it is missing and save the groups file."""
    groups_data = load_groups()
    _, created = _ensure_group_in_data(groups_data, group_name)
    if created:
        save_groups(groups_data)
    return True


def get_group_windows(group_name):
    """Return a copy of the window list of a group."""
    groups_data = load_groups()
    for group in groups_data.get("groups", []):
        if group.get("name") == group_name:
            return list(group.get("windows", []))
    return []


def get_all_windows_in_groups():
    """Get a flat list of all window IDs across all groups."""
    groups_data = load_groups()
    windows = []

    for group in groups_data.get("groups", []):
        windows.extend(group.get("windows", []))

    return windows


def add_window_to_group(window_id, group_name):
    """Add a window to a specific group, creating that group if needed."""
    groups_data = load_groups()
    target_group, _ = _ensure_group_in_data(groups_data, group_name)

    # Remove window from all groups first
    for group in groups_data.get("groups", []):
        if window_id in group.get("windows", []):
            group["windows"].remove(window_id)

    if window_id not in target_group.get("windows", []):
        target_group["windows"].append(window_id)

    save_groups(groups_data)
    return True


def remove_window_from_groups(window_id):
    """Remove a window from all groups when the window is deleted."""
    groups_data = load_groups()

    for group in groups_data.get("groups", []):
        if window_id in group.get("windows", []):
            group["windows"].remove(window_id)

    save_groups(groups_data)


def create_group(group_name):
    """Create a new group."""
    groups_data = load_groups()
    _, created = _ensure_group_in_data(groups_data, group_name)
    if not created:
        return False

    save_groups(groups_data)
    return True


def delete_group(group_name, move_windows_to_ungrouped=False):
    """
    Delete a group.

    If move_windows_to_ungrouped=True, the windows from the deleted group are moved
    to the Ungrouped group. This is ignored when deleting Ungrouped itself.
    """
    groups_data = load_groups()
    delete_idx = None

    for i, group in enumerate(groups_data.get("groups", [])):
        if group.get("name") == group_name:
            delete_idx = i
            break

    if delete_idx is None:
        return False

    group_to_delete = groups_data["groups"][delete_idx]
    windows_to_move = list(group_to_delete.get("windows", []))

    # Remove the group first so deleting Ungrouped is allowed.
    groups_data["groups"].pop(delete_idx)

    # Optional behavior: keep the windows by moving them to Ungrouped.
    if move_windows_to_ungrouped and windows_to_move and group_name != UNGROUPED_GROUP_NAME:
        ungrouped_group, _ = _ensure_group_in_data(groups_data, UNGROUPED_GROUP_NAME)
        for window in windows_to_move:
            if window not in ungrouped_group.get("windows", []):
                ungrouped_group["windows"].append(window)

    save_groups(groups_data)
    return True


def rename_group(old_name, new_name):
    """Rename a group."""
    groups_data = load_groups()

    for group in groups_data.get("groups", []):
        if group["name"] == old_name:
            group["name"] = new_name
            save_groups(groups_data)
            return True

    return False


def toggle_group_expanded(group_name):
    """Toggle group expand/collapse state."""
    groups_data = load_groups()

    for group in groups_data.get("groups", []):
        if group["name"] == group_name:
            group["expanded"] = not group.get("expanded", True)
            save_groups(groups_data)
            return True

    return False


def get_group_for_window(window_id):
    """Find which group a window belongs to."""
    groups_data = load_groups()

    for group in groups_data.get("groups", []):
        if window_id in group.get("windows", []):
            return group["name"]

    return None


def organize_ungrouped_windows():
    """
    Add windows that exist on disk but are not assigned to any group.

    Important: Ungrouped is created only if such windows exist.
    This allows the user to delete the Ungrouped group when it is empty.
    """
    from app.core import package_manager

    groups_data = load_groups()

    # Get all windows on disk
    if os.path.exists(package_manager.BASE_PROJECT_DIR):
        disk_windows = [
            d for d in os.listdir(package_manager.BASE_PROJECT_DIR)
            if os.path.isdir(os.path.join(package_manager.BASE_PROJECT_DIR, d))
            and d != "groups.json"
        ]
    else:
        disk_windows = []

    # Get all grouped windows from the already-loaded data
    grouped_windows = []
    for group in groups_data.get("groups", []):
        grouped_windows.extend(group.get("windows", []))

    # Find windows that are on disk but not inside any group
    ungrouped = [w for w in disk_windows if w not in grouped_windows]

    if ungrouped:
        ungrouped_group, _ = _ensure_group_in_data(groups_data, UNGROUPED_GROUP_NAME)
        for window in ungrouped:
            if window not in ungrouped_group.get("windows", []):
                ungrouped_group["windows"].append(window)
        save_groups(groups_data)
    else:
        # Save only to normalize a broken/missing file, without recreating Ungrouped.
        save_groups(groups_data)
