import json
import os
import tempfile
import shutil


class ZoomManager:
    def __init__(self):
        self.min_zoom = 50
        self.max_zoom = 200
        self.zoom_step = 10
        self.current_zoom = 100

        self.SETTINGS_FILE = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "user_workspaces",
            "app_settings.json"
        )

    def zoom_in(self):
        """Increase zoom and return the new zoom value."""
        self.current_zoom = min(self.current_zoom + self.zoom_step, self.max_zoom)
        return self.current_zoom

    def zoom_out(self):
        """Decrease zoom and return the new zoom value."""
        self.current_zoom = max(self.current_zoom - self.zoom_step, self.min_zoom)
        return self.current_zoom

    def set_zoom(self, value):
        """Set zoom directly, clamped to allowed range."""
        try:
            value = int(value)
        except Exception:
            value = 100

        self.current_zoom = max(self.min_zoom, min(value, self.max_zoom))
        return self.current_zoom

    def get_zoom(self):
        """Return current zoom percent."""
        return self.current_zoom

    def get_zoom_factor(self):
        """Return zoom as scale factor, e.g. 100 -> 1.0, 120 -> 1.2."""
        return self.current_zoom / 100.0

    def load_zoom(self):
        """Load zoom value from app_settings.json."""
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

                dashboard_data = data.get("dashboard", {})
                zoom = dashboard_data.get("zoom", 100)
                self.set_zoom(zoom)
            else:
                self.current_zoom = 100

        except Exception as e:
            print(f"Error loading zoom settings: {e}")
            self.current_zoom = 100

        return self.current_zoom

    def load_geometry(self):
        """Load saved window geometry from settings."""
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

                dashboard_data = data.get("dashboard", {})
                geometry = dashboard_data.get("geometry")
                if isinstance(geometry, dict):
                    return geometry

        except Exception as e:
            print(f"Error loading geometry settings: {e}")

        return None

    def save_settings(self, geometry=None):
        """
        Save zoom and optional geometry without erasing other settings
        like language or theme.
        """
        try:
            settings_dir = os.path.dirname(self.SETTINGS_FILE)
            os.makedirs(settings_dir, exist_ok=True)

            data = {}

            if os.path.exists(self.SETTINGS_FILE):
                try:
                    with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if not isinstance(data, dict):
                        data = {}
                except Exception:
                    data = {}

            if "dashboard" not in data or not isinstance(data["dashboard"], dict):
                data["dashboard"] = {}

            data["dashboard"]["zoom"] = self.current_zoom

            if geometry is not None:
                data["dashboard"]["geometry"] = geometry

            fd, temp_path = tempfile.mkstemp(suffix=".json", dir=settings_dir)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
                    json.dump(data, tmp_file, indent=4, ensure_ascii=False)

                if os.path.exists(self.SETTINGS_FILE):
                    backup_path = self.SETTINGS_FILE + ".bak"
                    try:
                        shutil.copy2(self.SETTINGS_FILE, backup_path)
                    except Exception:
                        pass

                shutil.move(temp_path, self.SETTINGS_FILE)

            finally:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass

        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_font_sizes(self):
        """Optional helper if you want to scale fonts elsewhere too."""
        factor = self.get_zoom_factor()
        return {
            "title": max(10, int(16 * factor)),
            "header": max(9, int(14 * factor)),
            "normal": max(8, int(11 * factor)),
            "small": max(7, int(9 * factor)),
            "button": max(8, int(10 * factor)),
        }