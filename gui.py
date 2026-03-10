import customtkinter as ctk
import os
import threading
import ctypes
import tkinter.colorchooser as colorchooser
import webbrowser
import subprocess
import sys
import urllib.request
import re
from pynput import mouse as pynput_mouse
from pynput import keyboard
from autoclicker import AutoclickerLogic
from macro import MacroLogic
from recorder import RecorderLogic
from settings import SettingsManager, ProfileManager, create_desktop_shortcut, APPDATA_PATH
from update import check_for_update

VERSION = "1.1.2"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class KurumisAutoclicker(ctk.CTk):
    def __init__(self):
        super().__init__()

        base_path = os.path.dirname(__file__)
        dll_path = os.path.join(base_path, "clicker.dll")
        icon_path = resource_path("icon.ico")

        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.ac_logic = AutoclickerLogic(dll_path)
        self.m_logic = MacroLogic(dll_path)
        self.r_logic = RecorderLogic(dll_path)

        self.settings_manager = SettingsManager(APPDATA_PATH)
        self.red_color = self.settings_manager.color
        self.dark_red = "#1a0000"

        ac_default = {"interval": 100, "duration": 10, "hotkey": "F6", "click_type": "left"}
        macro_default = {"interval": 100, "duration": 10, "hotkey": "F9"}
        rec_default = {"speed": 1.0, "hotkey": "F10"}

        self.ac_profile_manager = ProfileManager(APPDATA_PATH, "autoclicker", ac_default)
        self.macro_profile_manager = ProfileManager(APPDATA_PATH, "macro", macro_default)
        self.rec_profile_manager = ProfileManager(APPDATA_PATH, "recorder", rec_default)

        self.width, self.height = 400, 700
        self.title("Kurumi's Projects")
        self.geometry(f"{self.width}x{self.height}")
        self.configure(fg_color="#050505")

        self.vcmd = (self.register(self.validate_numbers), '%P')
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.ac_interval_unit = ctk.StringVar(value="ms")
        self.ac_duration_unit = ctk.StringVar(value="ms")
        self.rec_duration_unit = ctk.StringVar(value="ms")
        self.click_type_var = ctk.IntVar(value=1)

        self.selected_macro_line = None

        self.color_widgets = []

        self.about_links = {}

        self.create_navigation()

        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#050505")
        self.main_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.pages = {}
        self.create_pages()
        self.select_page("Autoclicker")

        self.load_initial_profiles()

        self.apply_color()

        threading.Thread(target=self.setup_hotkeys, daemon=True).start()

        threading.Thread(target=self.check_for_updates_startup, daemon=True).start()

        if self.settings_manager.show_tutorial:
            self.start_tutorial()

    def validate_numbers(self, P):
        return P == "" or P.isdigit()

    def create_navigation(self):
        self.nav_var = ctk.StringVar(value="Autoclicker")
        self.nav_menu = ctk.CTkSegmentedButton(
            self, values=["Autoclicker", "Macro", "Recorder", "Settings", "About"],
            variable=self.nav_var, command=self.select_page,
            selected_color=self.red_color, unselected_color=self.dark_red)
        self.nav_menu.grid(row=1, column=0, sticky="ew", padx=15, pady=(15, 0))
        self.color_widgets.append(self.nav_menu)

    def select_page(self, page_name):
        for frame in self.pages.values():
            frame.grid_forget()
        if page_name in self.pages:
            self.pages[page_name].grid(row=0, column=0, sticky="nsew")

    def log(self, textbox, message):
        textbox.configure(state="normal")
        textbox.insert("end", f"> {message}\n")
        textbox.see("end")
        textbox.configure(state="disabled")

    def create_log_box(self, parent, height=120):
        box = ctk.CTkTextbox(
            parent, height=height, corner_radius=10,
            fg_color=self.dark_red, border_color=self.red_color, border_width=1,
            text_color="#ffffff", scrollbar_button_color=self.red_color
        )
        box.configure(state="disabled")
        self.color_widgets.append(box)
        return box

    def show_message(self, title, message, icon=None):
        top = ctk.CTkToplevel(self)
        top.title(title)
        top.geometry("300x150")
        top.transient(self)
        top.grab_set()
        top.configure(fg_color="#050505")
        top.resizable(False, False)

        label = ctk.CTkLabel(top, text=message, text_color=self.red_color, wraplength=250)
        label.pack(expand=True, fill="both", padx=20, pady=20)
        self.color_widgets.append(label)

        btn = ctk.CTkButton(top, text="OK", fg_color=self.red_color,
                            command=top.destroy)
        btn.pack(pady=(0, 20))
        self.color_widgets.append(btn)
        top.wait_window()

    def setup_hotkey_entry(self, entry, default_key):
        entry.delete(0, "end")
        entry.insert(0, default_key)
        entry.bind("<Key>", lambda e: self.on_hotkey_key(e, entry))

    def on_hotkey_key(self, event, entry):
        keysym = event.keysym
        if keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R",
                      "Meta_L", "Meta_R", "Caps_Lock", "Num_Lock", "Scroll_Lock"):
            return "break"
        if len(keysym) == 1:
            new_key = keysym.upper() if keysym.isalpha() else keysym
        elif keysym.startswith("F") and keysym[1:].isdigit():
            new_key = keysym.upper()
        elif keysym.upper() in ("SPACE", "RETURN", "ESCAPE", "TAB", "BACKSPACE", "DELETE",
                                "HOME", "END", "PRIOR", "NEXT", "INSERT", "PAUSE", "PRINT", "MENU"):
            new_key = keysym.upper()
        else:
            return "break"
        entry.delete(0, "end")
        entry.insert(0, new_key)
        self.focus_set()
        return "break"

    def load_initial_profiles(self):
        ac_prof = self.ac_profile_manager.get_current_profile()
        if ac_prof:
            self.ac_int_entry.delete(0, "end")
            self.ac_int_entry.insert(0, str(ac_prof.get("interval", 100)))
            self.ac_dur_entry.delete(0, "end")
            self.ac_dur_entry.insert(0, str(ac_prof.get("duration", 10)))
            self.ac_hotkey_entry.delete(0, "end")
            self.ac_hotkey_entry.insert(0, ac_prof.get("hotkey", "F6"))
            self.click_type_var.set(2 if ac_prof.get("click_type") == "right" else 1)
            self.ac_logic.set_profile_data(ac_prof)
            self.update_ac_log()

        macro_prof = self.macro_profile_manager.get_current_profile()
        if macro_prof:
            self.m_interval_entry.delete(0, "end")
            self.m_interval_entry.insert(0, str(macro_prof.get("interval", 100)))
            self.m_duration_entry.delete(0, "end")
            self.m_duration_entry.insert(0, str(macro_prof.get("duration", 10)))
            self.m_hotkey_entry.delete(0, "end")
            self.m_hotkey_entry.insert(0, macro_prof.get("hotkey", "F9"))
            self.m_logic.set_profile_data(macro_prof)
            self.update_macro_list()

        rec_prof = self.rec_profile_manager.get_current_profile()
        if rec_prof:
            self.r_speed.delete(0, "end")
            self.r_speed.insert(0, str(rec_prof.get("speed", 1.0)))
            self.r_hotkey_entry.delete(0, "end")
            self.r_hotkey_entry.insert(0, rec_prof.get("hotkey", "F10"))
            self.r_logic.set_profile_data(rec_prof)
            self.update_recorder_list()

    def load_profile_to_ui(self, component):
        if component == "autoclicker":
            prof = self.ac_profile_manager.get_current_profile()
            if prof:
                self.ac_int_entry.delete(0, "end")
                self.ac_int_entry.insert(0, str(prof.get("interval", 100)))
                self.ac_dur_entry.delete(0, "end")
                self.ac_dur_entry.insert(0, str(prof.get("duration", 10)))
                self.ac_hotkey_entry.delete(0, "end")
                self.ac_hotkey_entry.insert(0, prof.get("hotkey", "F6"))
                self.click_type_var.set(2 if prof.get("click_type") == "right" else 1)
                self.ac_logic.set_profile_data(prof)
                self.update_ac_log()
        elif component == "macro":
            prof = self.macro_profile_manager.get_current_profile()
            if prof:
                self.m_interval_entry.delete(0, "end")
                self.m_interval_entry.insert(0, str(prof.get("interval", 100)))
                self.m_duration_entry.delete(0, "end")
                self.m_duration_entry.insert(0, str(prof.get("duration", 10)))
                self.m_hotkey_entry.delete(0, "end")
                self.m_hotkey_entry.insert(0, prof.get("hotkey", "F9"))
                self.m_logic.set_profile_data(prof)
                self.update_macro_list()
        elif component == "recorder":
            prof = self.rec_profile_manager.get_current_profile()
            if prof:
                self.r_speed.delete(0, "end")
                self.r_speed.insert(0, str(prof.get("speed", 1.0)))
                self.r_hotkey_entry.delete(0, "end")
                self.r_hotkey_entry.insert(0, prof.get("hotkey", "F10"))
                self.r_logic.set_profile_data(prof)
                self.update_recorder_list()

    def save_current_profile_from_ui(self, component):
        if component == "autoclicker":
            settings = {
                "interval": int(self.ac_int_entry.get() or 100),
                "duration": int(self.ac_dur_entry.get() or 10),
                "hotkey": self.ac_hotkey_entry.get(),
                "click_type": "right" if self.click_type_var.get() == 2 else "left"
            }
            settings.update(self.ac_logic.get_profile_data())
            self.ac_profile_manager.update_current_profile(settings)
            self.show_message("Profile saved", "Autoclicker profile saved.")
        elif component == "macro":
            settings = {
                "interval": int(self.m_interval_entry.get() or 100),
                "duration": int(self.m_duration_entry.get() or 10),
                "hotkey": self.m_hotkey_entry.get()
            }
            settings.update(self.m_logic.get_profile_data())
            self.macro_profile_manager.update_current_profile(settings)
            self.show_message("Profile saved", "Macro profile saved.")
        elif component == "recorder":
            try:
                speed = float(self.r_speed.get() or 1.0)
            except:
                speed = 1.0
            settings = {
                "speed": speed,
                "hotkey": self.r_hotkey_entry.get()
            }
            settings.update(self.r_logic.get_profile_data())
            self.rec_profile_manager.update_current_profile(settings)
            self.show_message("Profile saved", "Recorder profile saved.")

    def update_ac_log(self):
        self.ac_log.configure(state="normal")
        self.ac_log.delete("1.0", "end")
        for idx, (x, y) in enumerate(self.ac_logic.points):
            self.ac_log.insert("end", f"{idx+1}: ({x}, {y})\n")
        self.ac_log.configure(state="disabled")

    def setup_hotkeys(self):
        def on_press(key):
            try:
                if hasattr(key, 'name'):
                    k_name = key.name.upper()
                elif hasattr(key, 'char'):
                    k_name = key.char.upper()
                else:
                    return

                if k_name == self.ac_hotkey_entry.get().upper():
                    self.after(0, self.toggle_autoclicker)
                elif k_name == self.m_hotkey_entry.get().upper():
                    self.after(0, self.play_macro)
                elif k_name == self.r_hotkey_entry.get().upper():
                    self.after(0, self.toggle_recorder_playback)
            except:
                pass

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def toggle_autoclicker(self):
        if not self.ac_logic.running:
            interval = int(self.ac_int_entry.get()) * (1000 if self.ac_interval_unit.get() == "s" else 1)
            duration = int(self.ac_dur_entry.get()) * (1000 if self.ac_duration_unit.get() == "s" else 1)
            self.ac_logic.start(interval, duration, self.click_type_var.get() == 2)
            self.log(self.ac_log, "Started via Hotkey")
        else:
            self.ac_logic.stop()
            self.log(self.ac_log, "Stopped via Hotkey")

    def toggle_recorder_playback(self):
        if self.r_logic.playing:
            self.r_logic.stop_play()
            self.log(self.r_event_list, "Playback stopped via Hotkey")
        else:
            try:
                speed = float(self.r_speed.get())
                self.r_logic.play(speed)
                self.log(self.r_event_list, f"Playback started via Hotkey (speed {speed})")
            except ValueError:
                self.log(self.r_event_list, "Invalid speed value")

    def pick_point(self):
        self.iconify()
        def on_click(x, y, button, pressed):
            if pressed:
                self.ac_logic.points.append((x, y))
                self.after(0, lambda: [self.deiconify(),
                                        self.log(self.ac_log, f"Point: {int(x)}, {int(y)}"),
                                        self.update_ac_log()])
                return False
        threading.Thread(target=lambda: pynput_mouse.Listener(on_click=on_click).start()).start()

    def start_macro_recording(self):
        self.m_status_label.configure(text="Press ESC to stop recording")
        self.m_event_list.configure(state="normal")
        self.m_event_list.delete("1.0", "end")
        self.m_event_list.configure(state="disabled")
        self.selected_macro_line = None
        ctypes.windll.user32.MessageBeep(0)
        self.m_logic.start_recording(
            on_stop_callback=lambda: self.after(0, self.stop_macro_recording),
            on_event_callback=lambda ev: self.after(0, self.update_macro_list)
        )

    def stop_macro_recording(self):
        self.m_status_label.configure(text="")
        ctypes.windll.user32.MessageBeep(0)
        self.update_macro_list()

    def update_macro_list(self):
        self.m_event_list.configure(state="normal")
        self.m_event_list.delete("1.0", "end")
        for idx, ev in enumerate(self.m_logic.events):
            if ev[0] == 'key':
                text = f"{idx+1}: Key {ev[1]}"
            else:
                btn = ev[1]
                text = f"{idx+1}: {'Right' if btn else 'Left'} click"
            self.m_event_list.insert("end", text + "\n")
        self.m_event_list.configure(state="disabled")
        if self.selected_macro_line is not None:
            if self.selected_macro_line < len(self.m_logic.events):
                self.select_macro_line(self.selected_macro_line)
            else:
                self.selected_macro_line = None

    def on_macro_list_click(self, event):
        index = self.m_event_list.index(f"@{event.x},{event.y}")
        line = int(index.split('.')[0]) - 1
        if 0 <= line < len(self.m_logic.events):
            self.select_macro_line(line)

    def select_macro_line(self, line):
        self.m_event_list.tag_remove("sel", "1.0", "end")
        start = f"{line+1}.0"
        end = f"{line+1}.end"
        self.m_event_list.tag_add("sel", start, end)
        self.m_event_list.tag_config("sel", background=self.red_color, foreground="#ffffff")
        self.selected_macro_line = line

    def get_selected_line_index(self):
        return self.selected_macro_line

    def delete_selected_macro(self):
        idx = self.get_selected_line_index()
        if idx is not None:
            del self.m_logic.events[idx]
            self.selected_macro_line = None
            self.update_macro_list()

    def move_macro_up(self):
        idx = self.get_selected_line_index()
        if idx is not None and idx > 0:
            self.m_logic.events[idx], self.m_logic.events[idx-1] = self.m_logic.events[idx-1], self.m_logic.events[idx]
            self.selected_macro_line = idx - 1
            self.update_macro_list()

    def move_macro_down(self):
        idx = self.get_selected_line_index()
        if idx is not None and idx < len(self.m_logic.events)-1:
            self.m_logic.events[idx], self.m_logic.events[idx+1] = self.m_logic.events[idx+1], self.m_logic.events[idx]
            self.selected_macro_line = idx + 1
            self.update_macro_list()

    def play_macro(self):
        try:
            interval = int(self.m_interval_entry.get())
            duration = int(self.m_duration_entry.get())
            if self.m_interval_unit.get() == "s":
                interval *= 1000
            if self.m_duration_unit.get() == "s":
                duration *= 1000
            self.m_logic.play(interval, duration)
        except ValueError:
            pass

    def start_recorder_recording(self):
        self.r_status_label.configure(text="Press ESC to stop recording")
        self.r_event_list.configure(state="normal")
        self.r_event_list.delete("1.0", "end")
        self.r_event_list.configure(state="disabled")
        ctypes.windll.user32.MessageBeep(0)
        self.r_logic.start_record(lambda: self.after(0, self.stop_recorder_recording))

    def stop_recorder_recording(self):
        self.r_status_label.configure(text="")
        ctypes.windll.user32.MessageBeep(0)
        self.update_recorder_list()

    def update_recorder_list(self):
        self.r_event_list.configure(state="normal")
        self.r_event_list.delete("1.0", "end")
        for idx, ev in enumerate(self.r_logic.data):
            timestamp, action, x, y, val = ev
            if action == 'move':
                text = f"{idx+1}: Move ({x}, {y})"
            elif action == 'click':
                text = f"{idx+1}: {'Right' if val else 'Left'} click ({x},{y})"
            elif action == 'key':
                text = f"{idx+1}: Key {val}"
            else:
                text = f"{idx+1}: Unknown"
            self.r_event_list.insert("end", text + "\n")
        self.r_event_list.configure(state="disabled")

    def create_input_row(self, parent, label_text, entry_default, unit_var=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=5)
        label = ctk.CTkLabel(row, text=label_text, font=ctk.CTkFont(size=12, weight="bold"),
                              text_color=self.red_color)
        label.pack(anchor="w")
        self.color_widgets.append(label)

        cont = ctk.CTkFrame(row, fg_color="transparent")
        cont.pack(fill="x")
        e = ctk.CTkEntry(cont, height=35, border_color=self.red_color, fg_color="#050505",
                         text_color=self.red_color, validate="key", validatecommand=self.vcmd)
        e.insert(0, entry_default)
        e.pack(side="left", fill="x", expand=True)
        self.color_widgets.append(e)

        if unit_var:
            b = ctk.CTkButton(cont, text=unit_var.get(), width=60, height=35,
                              fg_color=self.dark_red,
                              command=lambda: [unit_var.set("s" if unit_var.get()=="ms" else "ms"),
                                               b.configure(text=unit_var.get())])
            b.pack(side="right", padx=(10,0))
            b.color_role = "secondary"
            self.color_widgets.append(b)
        return e

    def create_hotkey_row(self, parent, label_text, default_key):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=5)
        label = ctk.CTkLabel(row, text=label_text, font=ctk.CTkFont(size=12, weight="bold"),
                              text_color=self.red_color)
        label.pack(anchor="w")
        self.color_widgets.append(label)

        e = ctk.CTkEntry(row, height=35, border_color=self.red_color, fg_color="#050505",
                         text_color=self.red_color)
        e.pack(fill="x")
        self.setup_hotkey_entry(e, default_key)
        self.color_widgets.append(e)
        return e

    def create_pages(self):
        ac_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.pages["Autoclicker"] = ac_frame
        title = ctk.CTkLabel(ac_frame, text="AUTOCLICKER", font=ctk.CTkFont(size=20, weight="bold"),
                              text_color=self.red_color)
        title.pack(pady=10)
        self.color_widgets.append(title)

        self.ac_int_entry = self.create_input_row(ac_frame, "Click Interval:", "100", self.ac_interval_unit)
        self.ac_dur_entry = self.create_input_row(ac_frame, "Click Duration:", "10", self.ac_duration_unit)
        self.ac_hotkey_entry = self.create_hotkey_row(ac_frame, "Start/Stop Hotkey:", "F6")

        radio_f = ctk.CTkFrame(ac_frame, fg_color="transparent")
        radio_f.pack(fill="x", pady=10)
        radio_left = ctk.CTkRadioButton(radio_f, text="Left Click", variable=self.click_type_var, value=1,
                                         fg_color=self.red_color, text_color=self.red_color)
        radio_left.pack(side="left", expand=True)
        radio_right = ctk.CTkRadioButton(radio_f, text="Right Click", variable=self.click_type_var, value=2,
                                          fg_color=self.red_color, text_color=self.red_color)
        radio_right.pack(side="left", expand=True)
        self.color_widgets.extend([radio_left, radio_right])

        btn_pick = ctk.CTkButton(ac_frame, text="📌 PICK POINT", fg_color=self.red_color,
                                  command=self.pick_point)
        btn_pick.pack(fill="x", pady=2)
        btn_pick.color_role = "primary"
        self.color_widgets.append(btn_pick)

        btn_clear = ctk.CTkButton(ac_frame, text="🗑 CLEAR EVENTS", fg_color="transparent", border_width=1,
                                   border_color=self.red_color, text_color=self.red_color,
                                   command=lambda: [self.ac_logic.points.clear(),
                                                    self.update_ac_log()])
        btn_clear.pack(fill="x", pady=2)
        self.color_widgets.append(btn_clear)

        self.ac_log = self.create_log_box(ac_frame, height=220)
        self.ac_log.pack(fill="x", pady=10)

        m_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.pages["Macro"] = m_frame
        title = ctk.CTkLabel(m_frame, text="MACRO", font=ctk.CTkFont(size=20, weight="bold"),
                              text_color=self.red_color)
        title.pack(pady=10)
        self.color_widgets.append(title)

        self.m_interval_unit = ctk.StringVar(value="ms")
        self.m_duration_unit = ctk.StringVar(value="ms")
        self.m_interval_entry = self.create_input_row(m_frame, "Event Interval:", "100", self.m_interval_unit)
        self.m_duration_entry = self.create_input_row(m_frame, "Click Duration:", "10", self.m_duration_unit)

        self.m_hotkey_entry = self.create_hotkey_row(m_frame, "Play Hotkey:", "F9")

        self.m_status_label = ctk.CTkLabel(m_frame, text="", text_color=self.red_color,
                                           font=ctk.CTkFont(size=10))
        self.m_status_label.pack(pady=(0,5))
        self.color_widgets.append(self.m_status_label)

        btn_record = ctk.CTkButton(m_frame, text="🔴 START RECORDING", fg_color=self.red_color,
                                    command=self.start_macro_recording)
        btn_record.pack(fill="x", pady=2)
        btn_record.color_role = "primary"
        self.color_widgets.append(btn_record)

        btn_play = ctk.CTkButton(m_frame, text="▶ PLAY MACRO", fg_color=self.dark_red, border_width=1,
                                  border_color=self.red_color, command=self.play_macro)
        btn_play.pack(fill="x", pady=2)
        btn_play.color_role = "secondary"
        self.color_widgets.append(btn_play)

        btn_clear = ctk.CTkButton(m_frame, text="🗑 CLEAR ALL", fg_color="transparent", border_width=1,
                                   border_color=self.red_color, text_color=self.red_color,
                                   command=lambda: [self.m_logic.events.clear(), self.update_macro_list()])
        btn_clear.pack(fill="x", pady=2)
        self.color_widgets.append(btn_clear)

        self.m_event_list = ctk.CTkTextbox(
            m_frame, height=130, corner_radius=10,
            fg_color=self.dark_red, border_color=self.red_color, border_width=1,
            text_color="#ffffff", scrollbar_button_color=self.red_color
        )
        self.m_event_list.pack(fill="x", pady=10)
        self.color_widgets.append(self.m_event_list)

        btn_frame = ctk.CTkFrame(m_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=1)

        btn_del = ctk.CTkButton(btn_frame, text="Delete selected", fg_color=self.dark_red, border_width=1,
                                 border_color=self.red_color, command=self.delete_selected_macro)
        btn_del.grid(row=0, column=0, padx=2, sticky="ew")
        btn_del.color_role = "secondary"
        self.color_widgets.append(btn_del)

        btn_up = ctk.CTkButton(btn_frame, text="Move up", fg_color=self.dark_red, border_width=1,
                                border_color=self.red_color, command=self.move_macro_up)
        btn_up.grid(row=0, column=1, padx=2, sticky="ew")
        btn_up.color_role = "secondary"
        self.color_widgets.append(btn_up)

        btn_down = ctk.CTkButton(btn_frame, text="Move down", fg_color=self.dark_red, border_width=1,
                                  border_color=self.red_color, command=self.move_macro_down)
        btn_down.grid(row=0, column=2, padx=2, sticky="ew")
        btn_down.color_role = "secondary"
        self.color_widgets.append(btn_down)

        self.m_event_list.bind("<Button-1>", self.on_macro_list_click)

        r_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.pages["Recorder"] = r_frame
        title = ctk.CTkLabel(r_frame, text="RECORDER", font=ctk.CTkFont(size=20, weight="bold"),
                              text_color=self.red_color)
        title.pack(pady=10)
        self.color_widgets.append(title)

        self.r_speed = self.create_input_row(r_frame, "Playback Speed:", "1")
        self.r_hotkey_entry = self.create_hotkey_row(r_frame, "Playback Hotkey:", "F10")

        self.r_status_label = ctk.CTkLabel(r_frame, text="", text_color=self.red_color,
                                           font=ctk.CTkFont(size=10))
        self.r_status_label.pack(pady=(0,5))
        self.color_widgets.append(self.r_status_label)

        btn_record = ctk.CTkButton(r_frame, text="▶ START RECORDING", fg_color=self.red_color,
                                    command=self.start_recorder_recording)
        btn_record.pack(fill="x", pady=(10, 2))
        btn_record.color_role = "primary"
        self.color_widgets.append(btn_record)

        btn_clear = ctk.CTkButton(r_frame, text="🗑 CLEAR RECORDING", fg_color="transparent", border_width=1,
                                   border_color=self.red_color, text_color=self.red_color,
                                   command=lambda: [self.r_logic.data.clear(), self.update_recorder_list()])
        btn_clear.pack(fill="x", pady=2)
        self.color_widgets.append(btn_clear)

        btn_play = ctk.CTkButton(r_frame, text="⚡ PLAYBACK", fg_color=self.dark_red, border_width=1,
                                  border_color=self.red_color,
                                  command=lambda: self.r_logic.play(float(self.r_speed.get())))
        btn_play.pack(fill="x", pady=2)
        btn_play.color_role = "secondary"
        self.color_widgets.append(btn_play)

        self.r_event_list = ctk.CTkTextbox(
            r_frame, height=200, corner_radius=10,
            fg_color=self.dark_red, border_color=self.red_color, border_width=1,
            text_color="#ffffff", scrollbar_button_color=self.red_color
        )
        self.r_event_list.pack(fill="x", pady=10)
        self.color_widgets.append(self.r_event_list)

        settings_frame = ctk.CTkScrollableFrame(
            self.main_frame, fg_color="transparent",
            scrollbar_button_color=self.red_color
        )
        self.pages["Settings"] = settings_frame
        self.color_widgets.append(settings_frame)

        title = ctk.CTkLabel(settings_frame, text="SETTINGS", font=ctk.CTkFont(size=20, weight="bold"),
                              text_color=self.red_color)
        title.pack(pady=10)
        self.color_widgets.append(title)

        ac_prof_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        ac_prof_frame.pack(fill="x", pady=5)
        label = ctk.CTkLabel(ac_prof_frame, text="Autoclicker Profiles", font=ctk.CTkFont(size=14, weight="bold"),
                              text_color=self.red_color)
        label.pack(anchor="w")
        self.color_widgets.append(label)

        self.ac_prof_current_label = ctk.CTkLabel(ac_prof_frame, text="Current:", text_color=self.red_color)
        self.ac_prof_current_label.pack(anchor="w")
        self.color_widgets.append(self.ac_prof_current_label)

        self.ac_prof_dropdown = ctk.CTkOptionMenu(
            ac_prof_frame, values=list(self.ac_profile_manager.profiles.keys()),
            command=lambda choice: self.on_profile_selected("autoclicker", choice),
            fg_color="#050505",
            button_color="#050505",
            text_color=self.red_color,
            dropdown_fg_color=self.dark_red,
            dropdown_hover_color=self.red_color
        )
        self.ac_prof_dropdown.pack(fill="x", pady=2)
        self.ac_prof_dropdown.set(self.ac_profile_manager.current_profile or "")
        self.color_widgets.append(self.ac_prof_dropdown)

        btn_frame_ac = ctk.CTkFrame(ac_prof_frame, fg_color="transparent")
        btn_frame_ac.pack(fill="x", pady=2)
        btn_new = ctk.CTkButton(btn_frame_ac, text="New", fg_color=self.red_color,
                                 command=lambda: self.new_profile("autoclicker"))
        btn_new.pack(side="left", padx=2, expand=True, fill="x")
        btn_new.color_role = "primary"
        self.color_widgets.append(btn_new)

        btn_del = ctk.CTkButton(btn_frame_ac, text="Delete", fg_color=self.red_color,
                                 command=lambda: self.delete_profile("autoclicker"))
        btn_del.pack(side="left", padx=2, expand=True, fill="x")
        btn_del.color_role = "primary"
        self.color_widgets.append(btn_del)

        btn_rename = ctk.CTkButton(btn_frame_ac, text="Rename", fg_color=self.red_color,
                                    command=lambda: self.rename_profile("autoclicker"))
        btn_rename.pack(side="left", padx=2, expand=True, fill="x")
        btn_rename.color_role = "primary"
        self.color_widgets.append(btn_rename)

        btn_save = ctk.CTkButton(btn_frame_ac, text="Save", fg_color=self.red_color,
                                  command=lambda: self.save_profile("autoclicker"))
        btn_save.pack(side="left", padx=2, expand=True, fill="x")
        btn_save.color_role = "primary"
        self.color_widgets.append(btn_save)

        macro_prof_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        macro_prof_frame.pack(fill="x", pady=10)
        label = ctk.CTkLabel(macro_prof_frame, text="Macro Profiles", font=ctk.CTkFont(size=14, weight="bold"),
                              text_color=self.red_color)
        label.pack(anchor="w")
        self.color_widgets.append(label)

        self.macro_prof_dropdown = ctk.CTkOptionMenu(
            macro_prof_frame, values=list(self.macro_profile_manager.profiles.keys()),
            command=lambda choice: self.on_profile_selected("macro", choice),
            fg_color="#050505",
            button_color="#050505",
            text_color=self.red_color,
            dropdown_fg_color=self.dark_red,
            dropdown_hover_color=self.red_color
        )
        self.macro_prof_dropdown.pack(fill="x", pady=2)
        self.macro_prof_dropdown.set(self.macro_profile_manager.current_profile or "")
        self.color_widgets.append(self.macro_prof_dropdown)

        btn_frame_macro = ctk.CTkFrame(macro_prof_frame, fg_color="transparent")
        btn_frame_macro.pack(fill="x", pady=2)
        btn_new = ctk.CTkButton(btn_frame_macro, text="New", fg_color=self.red_color,
                                 command=lambda: self.new_profile("macro"))
        btn_new.pack(side="left", padx=2, expand=True, fill="x")
        btn_new.color_role = "primary"
        self.color_widgets.append(btn_new)

        btn_del = ctk.CTkButton(btn_frame_macro, text="Delete", fg_color=self.red_color,
                                 command=lambda: self.delete_profile("macro"))
        btn_del.pack(side="left", padx=2, expand=True, fill="x")
        btn_del.color_role = "primary"
        self.color_widgets.append(btn_del)

        btn_rename = ctk.CTkButton(btn_frame_macro, text="Rename", fg_color=self.red_color,
                                    command=lambda: self.rename_profile("macro"))
        btn_rename.pack(side="left", padx=2, expand=True, fill="x")
        btn_rename.color_role = "primary"
        self.color_widgets.append(btn_rename)

        btn_save = ctk.CTkButton(btn_frame_macro, text="Save", fg_color=self.red_color,
                                  command=lambda: self.save_profile("macro"))
        btn_save.pack(side="left", padx=2, expand=True, fill="x")
        btn_save.color_role = "primary"
        self.color_widgets.append(btn_save)

        rec_prof_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        rec_prof_frame.pack(fill="x", pady=10)
        label = ctk.CTkLabel(rec_prof_frame, text="Recorder Profiles", font=ctk.CTkFont(size=14, weight="bold"),
                              text_color=self.red_color)
        label.pack(anchor="w")
        self.color_widgets.append(label)

        self.rec_prof_dropdown = ctk.CTkOptionMenu(
            rec_prof_frame, values=list(self.rec_profile_manager.profiles.keys()),
            command=lambda choice: self.on_profile_selected("recorder", choice),
            fg_color="#050505",
            button_color="#050505",
            text_color=self.red_color,
            dropdown_fg_color=self.dark_red,
            dropdown_hover_color=self.red_color
        )
        self.rec_prof_dropdown.pack(fill="x", pady=2)
        self.rec_prof_dropdown.set(self.rec_profile_manager.current_profile or "")
        self.color_widgets.append(self.rec_prof_dropdown)

        btn_frame_rec = ctk.CTkFrame(rec_prof_frame, fg_color="transparent")
        btn_frame_rec.pack(fill="x", pady=2)
        btn_new = ctk.CTkButton(btn_frame_rec, text="New", fg_color=self.red_color,
                                 command=lambda: self.new_profile("recorder"))
        btn_new.pack(side="left", padx=2, expand=True, fill="x")
        btn_new.color_role = "primary"
        self.color_widgets.append(btn_new)

        btn_del = ctk.CTkButton(btn_frame_rec, text="Delete", fg_color=self.red_color,
                                 command=lambda: self.delete_profile("recorder"))
        btn_del.pack(side="left", padx=2, expand=True, fill="x")
        btn_del.color_role = "primary"
        self.color_widgets.append(btn_del)

        btn_rename = ctk.CTkButton(btn_frame_rec, text="Rename", fg_color=self.red_color,
                                    command=lambda: self.rename_profile("recorder"))
        btn_rename.pack(side="left", padx=2, expand=True, fill="x")
        btn_rename.color_role = "primary"
        self.color_widgets.append(btn_rename)

        btn_save = ctk.CTkButton(btn_frame_rec, text="Save", fg_color=self.red_color,
                                  command=lambda: self.save_profile("recorder"))
        btn_save.pack(side="left", padx=2, expand=True, fill="x")
        btn_save.color_role = "primary"
        self.color_widgets.append(btn_save)

        color_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        color_frame.pack(fill="x", pady=15)
        label = ctk.CTkLabel(color_frame, text="Color:", font=ctk.CTkFont(size=12, weight="bold"),
                              text_color=self.red_color)
        label.pack(anchor="w")
        self.color_widgets.append(label)

        self.color_entry = ctk.CTkEntry(color_frame, height=35, border_color=self.red_color,
                                        fg_color="#050505", text_color=self.red_color)
        self.color_entry.insert(0, self.settings_manager.color)
        self.color_entry.pack(fill="x", pady=2)
        self.color_widgets.append(self.color_entry)

        btn_color = ctk.CTkButton(color_frame, text="Choose Color", fg_color=self.red_color,
                                   command=self.change_color)
        btn_color.pack(fill="x", pady=2)
        btn_color.color_role = "primary"
        self.color_widgets.append(btn_color)

        btn_shortcut = ctk.CTkButton(settings_frame, text="Create Desktop shortcut", fg_color=self.red_color,
                                      command=self.create_desktop_shortcut_click)
        btn_shortcut.pack(fill="x", pady=5)
        btn_shortcut.color_role = "primary"
        self.color_widgets.append(btn_shortcut)

        btn_update = ctk.CTkButton(settings_frame, text="Check for updates", fg_color=self.red_color,
                                    command=self.check_for_updates_click)
        btn_update.pack(fill="x", pady=5)
        btn_update.color_role = "primary"
        self.color_widgets.append(btn_update)

        ver_label = ctk.CTkLabel(settings_frame, text=f"v{VERSION}", text_color=self.red_color)
        ver_label.pack(pady=2)
        self.color_widgets.append(ver_label)

        about_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.pages["About"] = about_frame

        about_frame.grid_rowconfigure(1, weight=1)
        about_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(about_frame, text="ABOUT", font=ctk.CTkFont(size=20, weight="bold"),
                              text_color=self.red_color)
        title.grid(row=0, column=0, pady=10)
        self.color_widgets.append(title)

        self.about_text = ctk.CTkTextbox(
            about_frame, wrap="word", corner_radius=10,
            fg_color=self.dark_red, border_color=self.red_color, border_width=1,
            text_color="#ffffff", scrollbar_button_color=self.red_color
        )
        self.about_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        self.about_text.configure(state="disabled")
        self.color_widgets.append(self.about_text)
        threading.Thread(target=self.load_about, daemon=True).start()

    def load_about(self):
        base_path = os.path.dirname(__file__)
        about_path = os.path.join(base_path, "about.txt")
        try:
            with open(about_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = f"Error loading about.txt:\n{e}"

        self.after(0, lambda: self.display_about(content))

    def display_about(self, content):
        self.about_text.configure(state="normal")
        self.about_text.delete("1.0", "end")
        self.about_links.clear()

        lines = content.splitlines()
        link_counter = 0

        self.about_text.tag_config("heading", foreground=self.red_color)
        self.about_text.tag_config("bold", foreground="#ff9999")
        self.about_text.tag_config("link", foreground="blue", underline=True)

        for line in lines:
            line = line.rstrip()
            if not line:
                self.about_text.insert("end", "\n")
                continue

            if line.startswith("# "):
                text = line[2:].strip().upper()
                self.about_text.insert("end", text + "\n", "heading")
                continue

            if re.match(r'^[-_*]{3,}$', line.strip()):
                width_px = self.about_text.winfo_width()
                if width_px > 0:
                    font = self.about_text.cget("font")
                    char_width = font.measure("─")
                    count = max(1, int(width_px / char_width))
                else:
                    count = 50
                self.about_text.insert("end", "─" * count + "\n")
                continue
            pos = 0
            length = len(line)
            last_pos = 0
            while pos < length:
                if line.startswith('[', pos):
                    end_bracket = line.find(']', pos+1)
                    if end_bracket != -1 and end_bracket+1 < length and line[end_bracket+1] == '(':
                        end_paren = line.find(')', end_bracket+2)
                        if end_paren != -1:
                            if pos > last_pos:
                                self.about_text.insert("end", line[last_pos:pos])
                            link_text = line[pos+1:end_bracket]
                            link_url = line[end_bracket+2:end_paren]
                            tag_name = f"link{link_counter}"
                            self.about_text.insert("end", link_text, (tag_name, "link"))
                            self.about_links[tag_name] = link_url
                            link_counter += 1
                            last_pos = end_paren + 1
                            pos = end_paren + 1
                            continue

                if line.startswith('**', pos):
                    end_bold = line.find('**', pos+2)
                    if end_bold != -1:
                        if pos > last_pos:
                            self.about_text.insert("end", line[last_pos:pos])
                        bold_text = line[pos+2:end_bold]
                        self.about_text.insert("end", bold_text, "bold")
                        last_pos = end_bold + 2
                        pos = end_bold + 2
                        continue

                pos += 1

            if last_pos < length:
                self.about_text.insert("end", line[last_pos:])

            self.about_text.insert("end", "\n")

        for tag, url in self.about_links.items():
            self.about_text.tag_bind(tag, "<Button-1>", lambda e, url=url: webbrowser.open(url))

        self.about_text.configure(state="disabled")

    def on_profile_selected(self, component, choice):
        if component == "autoclicker":
            self.ac_profile_manager.set_current_profile(choice)
            self.load_profile_to_ui("autoclicker")
            self.ac_prof_dropdown.set(choice)
        elif component == "macro":
            self.macro_profile_manager.set_current_profile(choice)
            self.load_profile_to_ui("macro")
            self.macro_prof_dropdown.set(choice)
        elif component == "recorder":
            self.rec_profile_manager.set_current_profile(choice)
            self.load_profile_to_ui("recorder")
            self.rec_prof_dropdown.set(choice)

    def new_profile(self, component):
        dialog = ctk.CTkInputDialog(text="Enter new profile name:", title="New Profile")
        name = dialog.get_input()
        if name:
            if component == "autoclicker":
                settings = {
                    "interval": int(self.ac_int_entry.get() or 100),
                    "duration": int(self.ac_dur_entry.get() or 10),
                    "hotkey": self.ac_hotkey_entry.get(),
                    "click_type": "right" if self.click_type_var.get() == 2 else "left"
                }
                settings.update(self.ac_logic.get_profile_data())
                mgr = self.ac_profile_manager
                dropdown = self.ac_prof_dropdown
            elif component == "macro":
                settings = {
                    "interval": int(self.m_interval_entry.get() or 100),
                    "duration": int(self.m_duration_entry.get() or 10),
                    "hotkey": self.m_hotkey_entry.get()
                }
                settings.update(self.m_logic.get_profile_data())
                mgr = self.macro_profile_manager
                dropdown = self.macro_prof_dropdown
            elif component == "recorder":
                try:
                    speed = float(self.r_speed.get() or 1.0)
                except:
                    speed = 1.0
                settings = {
                    "speed": speed,
                    "hotkey": self.r_hotkey_entry.get()
                }
                settings.update(self.r_logic.get_profile_data())
                mgr = self.rec_profile_manager
                dropdown = self.rec_prof_dropdown
            else:
                return

            if mgr.add_profile(name, settings):
                dropdown.configure(values=list(mgr.profiles.keys()))
                dropdown.set(name)
                mgr.set_current_profile(name)
                self.load_profile_to_ui(component)
                self.show_message("Profile created", f"Profile '{name}' has been created.")

    def delete_profile(self, component):
        if component == "autoclicker":
            mgr = self.ac_profile_manager
            dropdown = self.ac_prof_dropdown
        elif component == "macro":
            mgr = self.macro_profile_manager
            dropdown = self.macro_prof_dropdown
        elif component == "recorder":
            mgr = self.rec_profile_manager
            dropdown = self.rec_prof_dropdown
        else:
            return

        current = mgr.current_profile
        if current and len(mgr.profiles) > 1:
            mgr.delete_profile(current)
            dropdown.configure(values=list(mgr.profiles.keys()))
            new_current = mgr.current_profile
            dropdown.set(new_current)
            self.load_profile_to_ui(component)
            self.show_message("Profile deleted", f"Profile '{current}' has been removed.")

    def rename_profile(self, component):
        if component == "autoclicker":
            mgr = self.ac_profile_manager
            dropdown = self.ac_prof_dropdown
        elif component == "macro":
            mgr = self.macro_profile_manager
            dropdown = self.macro_prof_dropdown
        elif component == "recorder":
            mgr = self.rec_profile_manager
            dropdown = self.rec_prof_dropdown
        else:
            return

        current = mgr.current_profile
        if current:
            dialog = ctk.CTkInputDialog(text="Enter new name:", title="Rename Profile")
            new_name = dialog.get_input()
            if new_name and new_name != current:
                if mgr.rename_profile(current, new_name):
                    dropdown.configure(values=list(mgr.profiles.keys()))
                    dropdown.set(new_name)
                    self.show_message("Profile renamed", f"Profile is now '{new_name}'.")

    def save_profile(self, component):
        self.save_current_profile_from_ui(component)

    def darken_color(self, hex_color, factor=0.7):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def change_color(self):
        color_code = colorchooser.askcolor(title="Choose color", initialcolor=self.settings_manager.color)[1]
        if color_code:
            self.settings_manager.color = color_code
            self.settings_manager.save()
            self.color_entry.delete(0, "end")
            self.color_entry.insert(0, color_code)
            self.red_color = color_code
            self.dark_red = self.darken_color(self.red_color)
            self.apply_color()
            self.show_message("Color saved", "The new color has been applied.")

    def apply_color(self):
        hover_color = self.darken_color(self.red_color)
        for widget in self.color_widgets:
            try:
                if isinstance(widget, ctk.CTkSegmentedButton):
                    widget.configure(selected_color=self.red_color,
                                     unselected_color=self.dark_red,
                                     hover_color=hover_color)
                elif isinstance(widget, ctk.CTkButton):
                    if hasattr(widget, 'color_role'):
                        if widget.color_role == "primary":
                            widget.configure(fg_color=self.red_color,
                                             hover_color=hover_color)
                        elif widget.color_role == "secondary":
                            widget.configure(fg_color=self.dark_red,
                                             hover_color=hover_color)
                    else:
                        widget.configure(text_color=self.red_color,
                                         hover_color=hover_color)
                    if widget.cget("border_width") > 0:
                        widget.configure(border_color=self.red_color)
                elif isinstance(widget, ctk.CTkRadioButton):
                    widget.configure(fg_color=self.red_color,
                                     hover_color=hover_color,
                                     text_color=self.red_color)
                elif isinstance(widget, ctk.CTkEntry):
                    widget.configure(border_color=self.red_color,
                                     text_color=self.red_color)
                elif isinstance(widget, ctk.CTkTextbox):
                    widget.configure(border_color=self.red_color,
                                     scrollbar_button_color=self.red_color)
                elif isinstance(widget, ctk.CTkLabel):
                    widget.configure(text_color=self.red_color)
                elif isinstance(widget, ctk.CTkOptionMenu):
                    widget.configure(
                        fg_color="#050505",
                        button_color="#050505",
                        button_hover_color=hover_color,
                        dropdown_fg_color=self.dark_red,
                        dropdown_hover_color=self.red_color,
                        text_color=self.red_color
                    )
                elif isinstance(widget, ctk.CTkScrollableFrame):
                    widget.configure(scrollbar_button_color=self.red_color)
            except Exception:
                pass

        if hasattr(self, 'about_text'):
            self.about_text.tag_config("heading", foreground=self.red_color)

    def create_desktop_shortcut_click(self):
        exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
        success, msg = create_desktop_shortcut(exe_path)
        if success:
            self.show_message("Success", msg)
        else:
            self.show_message("Error", msg)

    def check_for_updates_startup(self):
        update_avail, download_url, latest_version = check_for_update(VERSION)
        if update_avail:
            self.after(0, lambda: self.show_update_dialog(download_url, latest_version))

    def check_for_updates_click(self):
        update_avail, download_url, latest_version = check_for_update(VERSION)
        if update_avail:
            self.show_update_dialog(download_url, latest_version)
        else:
            self.show_message("No update", "You are using the latest version.")

    def show_update_dialog(self, download_url, latest_version):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Update available")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color="#050505")
        label = ctk.CTkLabel(dialog, text=f"New version {latest_version} is available!",
                              text_color=self.red_color)
        label.pack(pady=10)
        self.color_widgets.append(label)
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        btn_update = ctk.CTkButton(btn_frame, text="Update", fg_color=self.red_color,
                                    command=lambda: self.perform_update(download_url, dialog))
        btn_update.pack(side="left", padx=5)
        btn_later = ctk.CTkButton(btn_frame, text="Later", fg_color=self.dark_red,
                                   command=dialog.destroy)
        btn_later.pack(side="left", padx=5)
        self.color_widgets.extend([btn_update, btn_later])
        dialog.wait_window()

    def perform_update(self, download_url, dialog):
        dialog.destroy()
        exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
        base = os.path.dirname(exe_path)
        update_script = os.path.join(base, "update.py")
        use_python = False
        if os.path.exists(update_script):
            if getattr(sys, 'frozen', False):
                update_script = os.path.join(base, "update.exe")
                if not os.path.exists(update_script):
                    self.show_message("Update Error", "update.exe not found.")
                    return
            else:
                use_python = True
        else:
            update_script = os.path.join(base, "update.exe")
            if not os.path.exists(update_script):
                self.show_message("Update Error", "update.exe not found.")
                return

        if use_python:
            args = [sys.executable, update_script, "--current-exe", exe_path,
                    "--current-version", VERSION, "--download-url", download_url]
        else:
            args = [update_script, "--current-exe", exe_path,
                    "--current-version", VERSION, "--download-url", download_url]

        subprocess.Popen(args)
        self.quit()

    def start_tutorial(self):
        try:
            base_path = os.path.dirname(sys.argv[0])
            if getattr(sys, 'frozen', False):
                tutorial_exe = os.path.join(base_path, "tutorial.exe")
                if os.path.exists(tutorial_exe):
                    subprocess.Popen([tutorial_exe])
                else:
                    tutorial_script = os.path.join(base_path, "tutorial.py")
                    if os.path.exists(tutorial_script):
                        subprocess.Popen([sys.executable, tutorial_script])
            else:
                tutorial_script = os.path.join(base_path, "tutorial.py")
                if os.path.exists(tutorial_script):
                    subprocess.Popen([sys.executable, tutorial_script])
        except Exception as e:
            print("Failed to start tutorial:", e)


if __name__ == "__main__":
    app = KurumisAutoclicker()
    app.mainloop()