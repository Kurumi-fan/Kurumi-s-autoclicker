import ctypes
import threading
import time
import os

class AutoclickerLogic:
    def __init__(self, dll_path):
        self.dll = None
        if os.path.exists(dll_path):
            self.dll = ctypes.CDLL(dll_path)
            self.dll.mouse_click.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool]

        self.running = False
        self.points = []

    def start(self, interval_ms, duration_ms, right_click):
        if self.dll and not self.running and self.points:
            self.running = True
            threading.Thread(target=self._loop, args=(interval_ms, duration_ms, right_click), daemon=True).start()

    def stop(self):
        self.running = False

    def _loop(self, interval, duration, right_click):
        while self.running:
            for x, y in self.points:
                if not self.running:
                    break
                self.dll.mouse_click(int(x), int(y), int(duration), bool(right_click))
                time.sleep(interval / 1000.0)

    def get_profile_data(self):
        return {"points": self.points}

    def set_profile_data(self, data):
        self.points = data.get("points", [])