# 💠 Kurumi's Autoclicker

![Logo](https://imgur.com/b4c8SL1.png)

A beautiful, flexible and feature-packed GUI autoclicker and macro tool powered by Python + PyQt5. Built for gamers, testers, and automation fans.

---

## 🚀 Features

### 🎯 Autoclicker
- Record and save multiple click positions per profile
- Adjustable interval (microseconds, milliseconds, seconds)
- Start/Stop hotkey
- Profiles saved to `profiles.json`
- Choose between left- and right-click
- Optional repeat-duration limit
- Background clicking support
- Smooth & animated UI with galaxy background

### 🧠 Macro
- Record key presses and mouse clicks
- Reorder actions via drag-and-drop
- Add multiple sequences without overwriting
- Set interval between actions
- Start/Stop hotkey
- Profile support via `profiles-makros.json`
- Repeat until stopped or until duration is reached

### 🎥 Recorder (NEW in v1.0.4)
- Records mouse movement paths and keyboard input
- ESC to stop recording
- Set how long the sequence should repeat
- Start/Stop via assigned hotkey
- Profiles saved in `profiles-recorder.json`
- All settings configurable under the **Settings** page

### ⚙️ Settings
- Unified settings area for:
  - Autoclicker
  - Macro
  - Recorder
- Control:
  - Hotkeys
  - Interval types
  - Repeat duration toggle
- Scroll support for small screens

### 🔔 Update Checker
- Automatic update check on startup

---

## 📦 How to Use

1. Launch the program
2. Pick click positions or load a profile
3. Set interval and hotkey
4. Press the hotkey to start/stop

---

### ⚠️ Why Some Antivirus Programs Flag This

The reason is pretty simple: **this tool uses automation features** that are often abused by malware — even though everything it does is safe and transparent. Here's what you need to know:

#### 🧠 Why Antivirus Software Might Flag It

Some antivirus engines flag automation tools because they share **behavioral patterns** with malware. In this case, **Kurumi’s Autoclicker** may be detected due to:

* **Simulated mouse and keyboard actions**
  (`pynput` is used to click, type, and move the mouse – this behavior resembles bots or keyloggers)

* **Global hotkey listening**
  The app listens for hotkeys globally to start/stop clicking or macros – some malware uses similar mechanisms to activate payloads.

* **Creates files on disk**
  The program saves your profiles to `.json` files (e.g. `profiles.json`, `profiles-makros.json`, etc). This activity is flagged as *“drops files during execution”* by some scanners.

* **Uses Windows scripting features**
  It uses `win32com.client` to optionally create desktop shortcuts, which touches Windows internals (e.g. COM objects, WScript.Shell).

* **Network access to check for updates**
  It connects to GitHub to check if new versions are available. This is benign but may be seen as suspicious if you're not expecting it.

---

#### ✅ Is It Safe?

Yes, the program:

* **Does not contain any malicious code**
* **Does not send any personal data**
* **Does not run in the background without user interaction**

> 🛠️ Still worried? 

* **Add me on discord and I can share my screen and use this application/programm.
* **Username: Kurumi_fan

---

## 👤 Developed by [Kurumi-fan](https://github.com/Kurumi-fan)

This project is part of **Kurumi’s Projects** – stay updated with the latest tools and releases.

---

## 📥 Download

> [📁 Latest Release on GitHub](https://github.com/Kurumi-fan/Kurumi-s-autoclicker/releases)
