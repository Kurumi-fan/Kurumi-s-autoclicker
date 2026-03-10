# 💠 Kurumi's Autoclicker

![Logo](https://imgur.com/b4c8SL1.png)

A beautiful, blazing-fast, and feature-packed GUI autoclicker and macro tool. **Now completely Open Source!** Built with **Python (CustomTkinter)** for a gorgeous modern interface and powered by a **C++ DLL** for highly precise, game-level input simulation. Designed for gamers, testers, and automation fans.

---

## 🚀 Features

### 🎯 Autoclicker
* **Pinpoint Accuracy:** Record and save multiple specific click positions per profile.
* **Custom C++ Backend:** Uses native Windows `SendInput` via a custom DLL for lightning-fast, lag-free clicking.
* **Total Control:** Adjustable interval and duration in milliseconds or seconds.
* **Left/Right Click:** Toggle effortlessly between mouse buttons.
* **Live Point Picking:** Pick screen coordinates with a built-in crosshair listener.

### 🧠 Macro
* **Record & Play:** Record complex sequences of key presses and mouse clicks.
* **Advanced Editing:** Select specific actions in your list to **Move Up, Move Down, or Delete** them directly in the UI.
* **Current Position Clicking:** Macros click at your *current* mouse position, giving you flexibility in games.
* **Append Mode:** Add multiple sequences to the same macro without overwriting your progress.

### 🎥 Recorder
* **Full Motion Capture:** Records precise mouse movement paths alongside keyboard inputs.
* **Playback Speed:** Speed up or slow down your recorded sequences on the fly.
* **ESC to Stop:** Safely stop recording or playback at any time with the Escape key.

### ⚙️ Settings & Customization
* **Unified Profile System:** Seamlessly Create, Rename, Save, and Delete profiles for Autoclicker, Macro, and Recorder.
* **Color Picker:** Personalize the UI! Change the default red accent to any color you like.
* **Organized Data:** All profiles and settings are cleanly stored in `%APPDATA%\KurumiProjects`.
* **Desktop Shortcut Generator:** Create a quick-launch shortcut with one click.

### 🔄 Automatic Updates
* **Smart Update Checker:** Checks GitHub for the latest release on startup.
* **Seamless Installation:** Downloads the new `.exe` and replaces the old one automatically via the built-in update assistant.

---

## 📦 How to Use

1. **Launch the program** (A quick tutorial will greet you on your first run).
2. **Pick a tool:** Navigate between Autoclicker, Macro, or Recorder using the top menu.
3. **Set your triggers:** Assign your preferred hotkeys (e.g., `F6`, `F9`, `F10`).
4. **Configure:** Set your click intervals, durations, or record your sequence.
5. **Execute:** Press your assigned hotkey to start or stop the automation.
6. **Save:** Don't forget to save your setup as a Profile in the Settings tab!

---

## 🛠️ For Developers (Build it yourself)

Since v1.1.2, Kurumi's Autoclicker is fully open-source. 

**Prerequisites:**
* Python 3.x
* C++ Compiler (e.g., MinGW or MSVC for building `clicker.dll`)
* Required Python packages: `customtkinter`, `pynput`

**Running from source:**
1. Clone the repository.
2. Ensure `clicker.dll` is compiled and placed in the same directory as `gui.py`.
3. Run `python gui.py`.

---

### ⚠️ Antivirus False Positives?

Because this tool uses global hotkeys, mouse listeners (`pynput`), and a C++ DLL that injects system-level inputs (`SendInput`), some Antivirus software or game anti-cheats might **falsely flag it**.

#### ✅ Why it is safe:
* **100% Open Source:** You can read every single line of code right here on GitHub.
* **No Telemetry:** No data is collected, stored remotely, or transmitted.
* **Local Storage:** Everything saves locally to your `AppData` folder.

Need help or proof?
> 💬 DM me on Discord: **Kurumi_fan** – I’ll gladly walk you through it.

---

## 👤 Developed by [Kurumi-fan](https://github.com/Kurumi-fan)

This is part of **Kurumi’s Projects** – a set of fun, helpful, and clean tools.

More tools:
* [Kurumi’s Crosshair](https://github.com/Kurumi-fan/Kurumi-s-Crosshair)
* [Kurumi’s Crosshair](https://github.com/Kurumi-fan/Kurumi-s-minecraft)
* [Kurumi’s Crosshair](https://github.com/Kurumi-fan/Kurumi-s-toolkit)
* [Kurumi’s Crosshair](https://github.com/Kurumi-fan/Kurumis-SoundControl)

---

## 📥 Download

> [📁 Download the Latest .exe Release here!](https://github.com/Kurumi-fan/Kurumi-s-autoclicker/releases)
