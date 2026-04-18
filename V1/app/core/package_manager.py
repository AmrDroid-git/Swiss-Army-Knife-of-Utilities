import json
import os
import shutil
from PySide6.QtCore import QPoint
from app.widgets import (
    BaseComponent, WidgetButton, WidgetIText, WidgetOText,
    WidgetIFileLink, WidgetOFileLink, WidgetIFolderLink, WidgetOFolderLink,
    WidgetConsole, WidgetInteractiveConsole, WidgetLabel
)

BASE_PROJECT_DIR = "user_workspaces"

def save_window(win_id, canvas):
    if not os.path.exists(BASE_PROJECT_DIR): 
        os.makedirs(BASE_PROJECT_DIR, exist_ok=True)
        
    win_folder = os.path.join(BASE_PROJECT_DIR, win_id)
    if not os.path.exists(win_folder): 
        os.makedirs(win_folder, exist_ok=True)
    
    data = []
    for c in canvas.findChildren(BaseComponent):
        # Ignore things that are not standard widgets (like templates inside palette if any happen to leak)
        if getattr(c, 'is_template', False): continue
        data.append(c.to_dict())
    
    with open(os.path.join(win_folder, "config.json"), "w") as f:
        json.dump(data, f, indent=4)

def load_window(win_id, canvas):
    path = os.path.join(BASE_PROJECT_DIR, win_id, "config.json")
    if not os.path.exists(path): return
    
    with open(path, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = [] 
            
        for item in data:
            pos = QPoint(item.get('x', 0), item.get('y', 0))
            comp_type = item.get('comp_type')
            
            obj = None
            if comp_type == "widget_button": obj = WidgetButton(canvas, pos)
            elif comp_type == "widget_label": obj = WidgetLabel(canvas, pos)
            elif comp_type == "widget_i_text": obj = WidgetIText(canvas, pos)
            elif comp_type == "widget_o_text": obj = WidgetOText(canvas, pos)
            elif comp_type == "widget_i_file_link": obj = WidgetIFileLink(canvas, pos)
            elif comp_type == "widget_o_file_link": obj = WidgetOFileLink(canvas, pos)
            elif comp_type == "widget_i_folder_link": obj = WidgetIFolderLink(canvas, pos)
            elif comp_type == "widget_o_folder_link": obj = WidgetOFolderLink(canvas, pos)
            elif comp_type == "widget_console": obj = WidgetConsole(canvas, pos)
            elif comp_type == "widget_interactive_console": obj = WidgetInteractiveConsole(canvas, pos)

            if obj:
                obj.from_dict(item)
                obj.is_template = False
                obj.set_edit_mode(False)
                obj.show()

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
