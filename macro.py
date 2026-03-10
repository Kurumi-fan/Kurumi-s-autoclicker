import ctypes
import ctypes.wintypes
import threading
import time
import os
from pynput import mouse, keyboard

class MacroLogic:
    def __init__(self, dll_path):
        self.dll = None
        if os.path.exists(dll_path):
            self.dll = ctypes.CDLL(dll_path)
            self.dll.key_event.argtypes = [ctypes.c_int, ctypes.c_bool]
            self.dll.mouse_click.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool]
        self.running = False
        self.recording = False
        self.events = []

    def start_recording(self, on_stop_callback, on_event_callback=None):
        if hasattr(self, 'key_listener') and self.key_listener.is_alive():
            self.key_listener.stop()
        if hasattr(self, 'mouse_listener') and self.mouse_listener.is_alive():
            self.mouse_listener.stop()

        self.events = []
        self.recording = True

        def get_vk(key):
            if hasattr(key, 'vk'):
                return key.vk
            elif hasattr(key, 'value') and hasattr(key.value, 'vk'):
                return key.value.vk
            else:
                return None

        def on_key_press(key):
            if key == keyboard.Key.esc:
                self.recording = False
                if hasattr(self, 'key_listener'):
                    self.key_listener.stop()
                if hasattr(self, 'mouse_listener'):
                    self.mouse_listener.stop()
                on_stop_callback()
                return False
            if self.recording:
                vk = get_vk(key)
                if vk:
                    self.events.append(('key', vk))
                    if on_event_callback:
                        on_event_callback(f"Key {key}")

        def on_click(x, y, button, pressed):
            if self.recording and pressed:
                btn = 1 if button == mouse.Button.right else 0
                self.events.append(('click', btn))
                if on_event_callback:
                    on_event_callback(f"{'Right' if btn else 'Left'} click")

        self.key_listener = keyboard.Listener(on_press=on_key_press)
        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.key_listener.start()
        self.mouse_listener.start()

    def play(self, interval_ms, duration_ms):
        if self.dll and not self.running and self.events:
            self.running = True
            threading.Thread(target=self._run_macro, args=(interval_ms, duration_ms), daemon=True).start()

    def _run_macro(self, interval_ms, duration_ms):
        interval = interval_ms / 1000.0
        for ev in self.events:
            if not self.running:
                break
            if ev[0] == 'key':
                vk = ev[1]
                self.dll.key_event(int(vk), True)
                time.sleep(0.05)
                self.dll.key_event(int(vk), False)
            elif ev[0] == 'click':
                btn = ev[1]
                point = ctypes.wintypes.POINT()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
                self.dll.mouse_click(point.x, point.y, int(duration_ms), bool(btn))
            time.sleep(interval)
        self.running = False

    def get_profile_data(self):
        return {"events": self.events}

    def set_profile_data(self, data):
        self.events = data.get("events", [])