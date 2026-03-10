import os
import json
import sys

APPDATA_PATH = os.path.join(os.getenv('APPDATA'), 'KurumiProjects')

class SettingsManager:
    def __init__(self, appdata_path=None):
        if appdata_path is None:
            appdata_path = APPDATA_PATH
        self.appdata_path = appdata_path
        self.settings_file = os.path.join(appdata_path, "settings.json")
        self.color = "#e60000"
        self.show_tutorial = True
        self.load()

    def load(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.color = data.get("color", self.color)
                    self.show_tutorial = data.get("show_tutorial", self.show_tutorial)
            except:
                pass
        else:
            self.save()

    def save(self):
        os.makedirs(self.appdata_path, exist_ok=True)
        with open(self.settings_file, 'w') as f:
            json.dump({
                "color": self.color,
                "show_tutorial": self.show_tutorial
            }, f, indent=4)


class ProfileManager:
    def __init__(self, appdata_path, component_name, default_profile):
        self.appdata_path = appdata_path
        self.component_name = component_name
        self.profiles_file = os.path.join(appdata_path, f"{component_name}.json")
        self.profiles = {}
        self.current_profile = None
        self.default_profile = default_profile
        self.load()

    def load(self):
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    self.profiles = data.get("profiles", {})
                    self.current_profile = data.get("current_profile")
            except:
                pass
        if not self.profiles:
            self.profiles["profile-1"] = self.default_profile.copy()
            self.current_profile = "profile-1"
            self.save()

    def save(self):
        os.makedirs(self.appdata_path, exist_ok=True)
        with open(self.profiles_file, 'w') as f:
            json.dump({
                "profiles": self.profiles,
                "current_profile": self.current_profile
            }, f, indent=4)

    def get_current_profile(self):
        if self.current_profile and self.current_profile in self.profiles:
            return self.profiles[self.current_profile]
        else:
            if self.profiles:
                self.current_profile = next(iter(self.profiles))
                return self.profiles[self.current_profile]
            return None

    def set_current_profile(self, name):
        if name in self.profiles:
            self.current_profile = name
            self.save()
            return True
        return False

    def add_profile(self, name, settings):
        if name not in self.profiles:
            self.profiles[name] = settings
            self.save()
            return True
        return False

    def delete_profile(self, name):
        if name in self.profiles and len(self.profiles) > 1:
            del self.profiles[name]
            if self.current_profile == name:
                self.current_profile = next(iter(self.profiles))
            self.save()
            return True
        return False

    def rename_profile(self, old_name, new_name):
        if old_name in self.profiles and new_name not in self.profiles:
            self.profiles[new_name] = self.profiles.pop(old_name)
            if self.current_profile == old_name:
                self.current_profile = new_name
            self.save()
            return True
        return False

    def update_current_profile(self, settings):
        if self.current_profile:
            self.profiles[self.current_profile] = settings
            self.save()
            return True
        return False


def create_desktop_shortcut(target_path, shortcut_name="Kurumi's Autoclicker.lnk",
                            description="Kurumi's Autoclicker"):
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    shortcut_path = os.path.join(desktop, shortcut_name)

    try:
        import winshell
        with winshell.shortcut(shortcut_path) as link:
            link.path = target_path
            link.description = description
            link.working_directory = os.path.dirname(target_path)
        return True, "Desktop shortcut (.lnk) created."
    except ImportError:
        try:
            url_path = shortcut_path.replace('.lnk', '.url')
            with open(url_path, 'w') as f:
                f.write(f"[InternetShortcut]\nURL=file:///{target_path}\nIconIndex=0\nIconFile={target_path}")
            return True, "Desktop shortcut (.url) created (winshell not installed)."
        except Exception as e:
            return False, f"Error creating shortcut: {e}"