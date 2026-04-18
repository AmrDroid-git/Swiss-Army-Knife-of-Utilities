import json, os
from PySide6.QtCore import QPoint
from components import ScriptButton, CustomField, DraggableLabel, BaseComponent

# Root folder for all window data and copied scripts
BASE_PROJECT_DIR = "projects"
if not os.path.exists(BASE_PROJECT_DIR): os.makedirs(BASE_PROJECT_DIR)

def save_window(win_id, canvas):
    # Each window gets its own folder inside 'projects'
    win_folder = os.path.join(BASE_PROJECT_DIR, win_id)
    if not os.path.exists(win_folder): os.makedirs(win_folder)
    
    data = []
    for c in canvas.findChildren(BaseComponent):
        item = {"type": c.comp_type, "x": c.x(), "y": c.y(), "w": c.width(), "h": c.height(), "arg_order": c.arg_order}
        if c.comp_type == "script_button":
            item.update({"label": c.btn.text(), "script": c.script_path})
        elif c.comp_type == "label":
            item["text"] = c.lbl.text()
        elif c.comp_type in ["text_field", "file_field", "folder_field"]:
            item["mode"] = c.mode
        data.append(item)
    
    with open(os.path.join(win_folder, "layout.json"), "w") as f:
        json.dump(data, f)

def load_window(win_id, canvas):
    path = os.path.join(BASE_PROJECT_DIR, win_id, "layout.json")
    if not os.path.exists(path): return
    
    with open(path, "r") as f:
        data = json.load(f)
        for item in data:
            pos = QPoint(item['x'], item['y'])
            if item['type'] == "script_button":
                obj = ScriptButton(canvas, pos, item.get('label'))
                obj.script_path = item.get('script', '')
            elif item['type'] == "label":
                obj = DraggableLabel(canvas, pos, item.get('text'))
            else:
                obj = CustomField(canvas, pos, item['type'])
                obj.mode = item.get('mode', 'input')
                obj.entry.setReadOnly(obj.mode == "output")
            obj.setFixedSize(item['w'], item['h'])
            obj.arg_order = item.get('arg_order', 0)
            obj.set_edit_mode(False)