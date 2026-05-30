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

def get_all_windows_in_groups():
    """Get a flat list of all window IDs across all groups."""
    groups_data = load_groups()
    windows = []
    
    for group in groups_data.get("groups", []):
        windows.extend(group.get("windows", []))
    
    return windows

def add_window_to_group(window_id, group_name):
    """Add a window to a specific group."""
    groups_data = load_groups()
    
    # Remove window from all groups first
    for group in groups_data.get("groups", []):
        if window_id in group.get("windows", []):
            group["windows"].remove(window_id)
    
    # Add to target group
    for group in groups_data.get("groups", []):
        if group["name"] == group_name:
            if window_id not in group.get("windows", []):
                group["windows"].append(window_id)
            save_groups(groups_data)
            return True
    
    return False

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
    
    # Check if group already exists
    for group in groups_data.get("groups", []):
        if group["name"] == group_name:
            return False  # Group already exists
    
    # Add new group
    groups_data["groups"].append({
        "name": group_name,
        "expanded": True,
        "windows": []
    })
    
    save_groups(groups_data)
    return True

def delete_group(group_name):
    """Delete a group (moves its windows to Ungrouped)."""
    groups_data = load_groups()
    
    # Find and move windows to Ungrouped
    ungrouped_idx = None
    delete_idx = None
    
    for i, group in enumerate(groups_data.get("groups", [])):
        if group["name"] == "Ungrouped":
            ungrouped_idx = i
        if group["name"] == group_name:
            delete_idx = i
    
    if delete_idx is not None:
        group_to_delete = groups_data["groups"][delete_idx]
        
        # Move all windows to Ungrouped
        if ungrouped_idx is not None:
            groups_data["groups"][ungrouped_idx]["windows"].extend(
                group_to_delete.get("windows", [])
            )
        
        # Remove the group
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
        # Add to Ungrouped group
        for group in groups_data.get("groups", []):
            if group["name"] == "Ungrouped":
                for window in ungrouped:
                    if window not in group.get("windows", []):
                        group["windows"].append(window)
        
        save_groups(groups_data)
