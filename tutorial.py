import customtkinter as ctk
import os
import sys
from settings import APPDATA_PATH, SettingsManager

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class TutorialApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Kurumi's Autoclicker - Tutorial")
        self.geometry("500x400")
        self.configure(fg_color="#050505")

        self.settings_manager = SettingsManager()
        self.red_color = self.settings_manager.color
        self.dark_red = "#1a0000"

        self.textbox = ctk.CTkTextbox(
            self, wrap="word", corner_radius=10,
            fg_color=self.dark_red, border_color=self.red_color, border_width=1,
            text_color="#ffffff", scrollbar_button_color=self.red_color
        )
        self.textbox.pack(fill="both", expand=True, padx=20, pady=20)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0,20))

        self.dont_show_btn = ctk.CTkButton(
            btn_frame, text="Don't show again", fg_color=self.red_color,
            command=self.dont_show_again
        )
        self.dont_show_btn.pack(side="left", padx=5, expand=True, fill="x")

        self.continue_btn = ctk.CTkButton(
            btn_frame, text="Continue", fg_color=self.dark_red,
            border_width=1, border_color=self.red_color,
            command=self.destroy
        )
        self.continue_btn.pack(side="right", padx=5, expand=True, fill="x")

        self.btn_frame = btn_frame

        self.load_tutorial_text()

        self.after(10, self.center_window)

    def load_tutorial_text(self):
        tutorial_path = resource_path("tutorial.txt")
        try:
            with open(tutorial_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = f"Error loading tutorial.txt:\n{e}"

        self.textbox.insert("1.0", content)
        self.textbox.configure(state="disabled")

        self.update_idletasks()
        self.adjust_window_size()

    def adjust_window_size(self):
        text_height = self.textbox.winfo_reqheight()
        btn_height = self.btn_frame.winfo_reqheight()
        total_padding = 20 + 20 + 20
        extra = 10
        new_height = text_height + btn_height + total_padding + extra
        if new_height < 400:
            new_height = 400
        self.geometry(f"500x{new_height}")

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def dont_show_again(self):
        self.settings_manager.show_tutorial = False
        self.settings_manager.save()
        self.destroy()

if __name__ == "__main__":
    app = TutorialApp()
    app.mainloop()