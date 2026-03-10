import os
import sys
import json
import urllib.request
import tempfile
import subprocess
import time
import shutil
import argparse
import customtkinter as ctk
from settings import SettingsManager, APPDATA_PATH


def get_latest_release_info():
    url = "https://api.github.com/repos/Kurumi-fan/Kurumi-s-autoclicker/releases/latest"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            tag = data.get("tag_name", "").lstrip("v")
            download_url = None
            for asset in data.get("assets", []):
                if "Kurumis_autoclicker.exe" in asset.get("name", ""):
                    download_url = asset.get("browser_download_url")
                    break
            return tag, download_url
    except Exception as e:
        print("Update check failed:", e)
        return None, None


def check_for_update(current_version):
    latest_version, download_url = get_latest_release_info()
    if latest_version and download_url:
        if latest_version > current_version:
            return True, download_url, latest_version
    return False, None, None


class UpdateApp(ctk.CTk):
    def __init__(self, current_exe, current_version, download_url=None):
        super().__init__()
        self.current_exe = current_exe
        self.current_version = current_version
        self.download_url = download_url
        self.latest_version = None
        self.temp_exe = None
        self.backup_exe = None

        self.settings = SettingsManager()
        self.red_color = self.settings.color
        self.dark_red = "#1a0000"

        self.title("Kurumi's Autoclicker - Update")
        self.geometry("600x400")
        self.configure(fg_color="#050505")

        self.log_box = ctk.CTkTextbox(
            self, wrap="word", corner_radius=10,
            fg_color=self.dark_red, border_color=self.red_color, border_width=1,
            text_color="#ffffff", scrollbar_button_color=self.red_color
        )
        self.log_box.pack(fill="both", expand=True, padx=20, pady=20)
        self.log_box.configure(state="normal")

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=20, pady=(0,20))

        self.log("Update assistant started.")
        self.log(f"Current version: {self.current_version}")

        self.after(100, self.start_update)

    def log(self, message):
        self.log_box.insert("end", f"> {message}\n")
        self.log_box.see("end")
        self.update_idletasks()

    def start_update(self):
        if not self.download_url:
            self.log("Checking for updates...")
            latest_version, dl_url = get_latest_release_info()
            if not latest_version or not dl_url:
                self.log("Failed to check for updates.")
                self.show_error_and_exit("Update check failed.")
                return
            if latest_version <= self.current_version:
                self.log(f"You are already on the latest version ({self.current_version}).")
                self.show_message_and_exit("No update available.")
                return
            self.latest_version = latest_version
            self.download_url = dl_url
            self.log(f"Update found: version {latest_version}")
        else:
            self.latest_version = "unknown"
            self.log(f"Using provided download URL: {self.download_url}")

        self.log("Downloading update...")
        self.temp_exe = os.path.join(tempfile.gettempdir(), "Kurumis_autoclicker_new.exe")
        success = self.download_file(self.download_url, self.temp_exe)
        if not success:
            self.log("Download failed.")
            self.show_error_and_exit("Download failed.")
            return
        self.log("Download completed.")

        self.log("Replacing executable...")
        time.sleep(1)
        self.backup_exe = self.current_exe + ".bak"
        try:
            if os.path.exists(self.backup_exe):
                os.remove(self.backup_exe)
            os.rename(self.current_exe, self.backup_exe)
            shutil.move(self.temp_exe, self.current_exe)
            self.log("Update successful!")
            self.on_update_complete(True)
        except Exception as e:
            self.log(f"Failed to replace executable: {e}")
            if os.path.exists(self.backup_exe):
                shutil.move(self.backup_exe, self.current_exe)
            self.show_error_and_exit("Update failed.")
            return

    def download_file(self, url, dest_path):
        try:
            urllib.request.urlretrieve(url, dest_path)
            return True
        except Exception as e:
            self.log(f"Download error: {e}")
            return False

    def on_update_complete(self, success):
        if success:
            self.log("Update completed successfully.")
            self.clear_buttons()
            btn_delete = ctk.CTkButton(self.button_frame, text="Delete backup",
                                       fg_color=self.red_color, command=self.delete_backup)
            btn_delete.pack(side="left", padx=5, expand=True, fill="x")
            btn_keep = ctk.CTkButton(self.button_frame, text="Keep backup",
                                     fg_color=self.dark_red, border_width=1, border_color=self.red_color,
                                     command=self.keep_backup)
            btn_keep.pack(side="left", padx=5, expand=True, fill="x")
            btn_delete_all = ctk.CTkButton(self.button_frame, text="Delete all .bak",
                                          fg_color=self.red_color, command=self.delete_all_backups)
            btn_delete_all.pack(side="left", padx=5, expand=True, fill="x")
        else:
            self.show_error_and_exit("Update failed.")

    def clear_buttons(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

    def delete_backup(self):
        try:
            if os.path.exists(self.backup_exe):
                os.remove(self.backup_exe)
                self.log("Backup deleted.")
            else:
                self.log("Backup file not found.")
        except Exception as e:
            self.log(f"Error deleting backup: {e}")
        self.finish_and_launch()

    def keep_backup(self):
        self.log("Backup kept.")
        self.finish_and_launch()

    def delete_all_backups(self):
        dirname = os.path.dirname(self.current_exe)
        count = 0
        for file in os.listdir(dirname):
            if file.endswith(".bak"):
                try:
                    os.remove(os.path.join(dirname, file))
                    count += 1
                except Exception as e:
                    self.log(f"Error deleting {file}: {e}")
        self.log(f"Deleted {count} backup file(s).")
        self.finish_and_launch()

    def finish_and_launch(self):
        try:
            subprocess.Popen([self.current_exe])
        except Exception as e:
            self.log(f"Error launching main program: {e}")
        self.quit()

    def show_error_and_exit(self, message):
        self.log(f"ERROR: {message}")
        self.clear_buttons()
        btn_close = ctk.CTkButton(self.button_frame, text="Close", fg_color=self.red_color,
                                  command=self.quit)
        btn_close.pack(pady=10)

    def show_message_and_exit(self, message):
        self.log(message)
        self.clear_buttons()
        btn_close = ctk.CTkButton(self.button_frame, text="Close", fg_color=self.red_color,
                                  command=self.quit)
        btn_close.pack(pady=10)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-exe", required=True, help="Path to the current executable")
    parser.add_argument("--current-version", required=True, help="Current version string")
    parser.add_argument("--download-url", default=None, help="Pre‑determined download URL")
    args = parser.parse_args()

    app = UpdateApp(args.current_exe, args.current_version, args.download_url)
    app.mainloop()


if __name__ == "__main__":
    sys.exit(main())