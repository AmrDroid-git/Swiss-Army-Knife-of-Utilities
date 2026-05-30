"""
Group Manager: Handles organizing windows into collapsible groups.
Groups are stored in a JSON file for UI-only organization (no backend changes).
"""

import json
import os
from app.core.package_manager import BASE_PROJECT_DIR

GROUPS_FILE = os.path.join(BASE_PROJECT_DIR, "groups.json")

DEFAULT_GROUPS = {
    "groups": [
        {
            "name": "Ungrouped",
            "expanded": True,
            "windows": []
        }
    ]
}

def ensure_groups_file():
    """Create groups.json if it doesn't exist."""
    os.makedirs(BASE_PROJECT_DIR, exist_ok=True)
    
    if not os.path.exists(GROUPS_FILE):
        save_groups(DEFAULT_GROUPS)

def load_groups():
    """Load groups from JSON file."""
    ensure_groups_file()
    
    try:
        with open(GROUPS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return DEFAULT_GROUPS.copy()

def save_groups(data):
    """Save groups to JSON file."""
    os.makedirs(BASE_PROJECT_DIR, exist_ok=True)
    
    with open(GROUPS_FILE, 'w') as f:
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


def ensure_group_exists(group_name="Ungrouped"):
    """Create the group if it is missing and save the groups file."""
    groups_data = load_groups()
    _, created = _ensure_group_in_data(groups_data, group_name)
    if created:
        save_groups(groups_data)
    return True

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
    """Remove a window from all groups (when deleted)."""
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

def delete_group(group_name):
    """Delete a group (moves its windows to Ungrouped)."""
    if group_name == "Ungrouped":
        return False

    groups_data = load_groups()
    ungrouped_group, _ = _ensure_group_in_data(groups_data, "Ungrouped")
    delete_idx = None

    for i, group in enumerate(groups_data.get("groups", [])):
        if group.get("name") == group_name:
            delete_idx = i
            break

    if delete_idx is not None:
        group_to_delete = groups_data["groups"][delete_idx]

        for window in group_to_delete.get("windows", []):
            if window not in ungrouped_group.get("windows", []):
                ungrouped_group["windows"].append(window)

        groups_data["groups"].pop(delete_idx)
        save_groups(groups_data)
        return True

    return False

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
    """Add any windows that exist on disk but aren't in any group to 'Ungrouped'."""
    from app.core import package_manager
    import os
    
    groups_data = load_groups()
    ungrouped_group, _ = _ensure_group_in_data(groups_data, "Ungrouped")
    
    # Get all windows on disk
    if os.path.exists(package_manager.BASE_PROJECT_DIR):
        disk_windows = [d for d in os.listdir(package_manager.BASE_PROJECT_DIR)
                        if os.path.isdir(os.path.join(package_manager.BASE_PROJECT_DIR, d))
                        and d != "groups.json"]
    else:
        disk_windows = []
    
    # Get all grouped windows
    grouped_windows = get_all_windows_in_groups()
    
    # Find ungrouped windows
    ungrouped = [w for w in disk_windows if w not in grouped_windows]
    
    if ungrouped:
        for window in ungrouped:
            if window not in ungrouped_group.get("windows", []):
                ungrouped_group["windows"].append(window)

    save_groups(groups_data)
