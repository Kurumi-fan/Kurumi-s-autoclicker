import ctypes
import threading
import time
import os
from pynput import mouse, keyboard

class RecorderLogic:
    def __init__(self, dll_path):
        self.dll = None
        if os.path.exists(dll_path):
            self.dll = ctypes.CDLL(dll_path)
            self.dll.mouse_move.argtypes = [ctypes.c_int, ctypes.c_int]
            self.dll.mouse_click.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool]
            self.dll.key_event.argtypes = [ctypes.c_int, ctypes.c_bool]
        self.recording = False
        self.playing = False
        self.data = []

    def start_record(self, on_stop_callback):
        if hasattr(self, 'm_listener') and self.m_listener.is_alive():
            self.m_listener.stop()
        if hasattr(self, 'k_listener') and self.k_listener.is_alive():
            self.k_listener.stop()

        self.data = []
        self.start_time = time.time()
        self.recording = True

        ctypes.windll.user32.MessageBeep(0)

        def get_vk(key):
            if hasattr(key, 'vk'):
                return key.vk
            elif hasattr(key, 'value') and hasattr(key.value, 'vk'):
                return key.value.vk
            else:
                return None

        def on_move(x, y):
            if self.recording:
                self.data.append((time.time() - self.start_time, 'move', int(x), int(y), None))

        def on_click(x, y, button, pressed):
            if self.recording and pressed:
                btn = 1 if button == mouse.Button.right else 0
                self.data.append((time.time() - self.start_time, 'click', int(x), int(y), btn))

        def on_press(key):
            if key == keyboard.Key.esc:
                self.recording = False
                self.m_listener.stop()
                self.k_listener.stop()
                ctypes.windll.user32.MessageBeep(0)
                on_stop_callback()
                return False
            if self.recording:
                vk = get_vk(key)
                if vk:
                    self.data.append((time.time() - self.start_time, 'key', 0, 0, vk))

        self.m_listener = mouse.Listener(on_move=on_move, on_click=on_click)
        self.k_listener = keyboard.Listener(on_press=on_press)
        self.m_listener.start()
        self.k_listener.start()

    def play(self, speed=1.0):
        if self.dll and not self.playing and self.data:
            self.playing = True
            threading.Thread(target=self._play_loop, args=(speed,), daemon=True).start()

    def stop_play(self):
        self.playing = False

    def _play_loop(self, speed):
        last_time = 0
        s = max(0.1, speed)
        for t, action, x, y, val in self.data:
            if not self.playing:
                break
            time.sleep(max(0, (t - last_time) / s))
            if action == 'move':
                self.dll.mouse_move(x, y)
            elif action == 'click':
                self.dll.mouse_click(x, y, 10, bool(val))
            elif action == 'key':
                self.dll.key_event(val, True)
                time.sleep(0.01)
                self.dll.key_event(val, False)
            last_time = t
        self.playing = False

    def get_profile_data(self):
        return {"recorder_data": self.data}

    def set_profile_data(self, data):
        self.data = data.get("recorder_data", [])