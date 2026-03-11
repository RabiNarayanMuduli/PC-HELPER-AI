# main.py
import sys
import threading
import time
import os
import psutil
import pyautogui
import pyttsx3
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

from avatar import Avatar       # your old GIF avatar code
from voice_input import listen_command  # your voice listener

# -------------------- APP INIT --------------------
app = QApplication(sys.argv)
avatar = Avatar()
avatar.show()  # show avatar window

# -------------------- SIGNALS --------------------
class UIUpdater(QObject):
    update_text = pyqtSignal(str)
    set_idle_signal = pyqtSignal()
    set_thinking_signal = pyqtSignal()

ui_updater = UIUpdater()
ui_updater.update_text.connect(avatar.speak_text)
ui_updater.set_idle_signal.connect(avatar.set_idle)
ui_updater.set_thinking_signal.connect(avatar.set_thinking)

# -------------------- TTS --------------------
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# -------------------- WINDOW CONTROL --------------------
def control_window(app_name, action):
    app_name = app_name.lower()
    windows = []

    # Use pygetwindow to find windows
    import pygetwindow as gw
    windows = [w for w in gw.getAllWindows() if w.title and app_name in w.title.lower()]

    if not windows:
        speak(f"No window found for {app_name}")
        return

    win = windows[0]
    screen_width, screen_height = pyautogui.size()

    try:
        if action == "maximize":
            win.maximize()
        elif action == "minimize":
            win.minimize()
        elif action == "restore":
            win.restore()
        elif action == "fullscreen":
            win.moveTo(0,0)
            win.resizeTo(screen_width, screen_height)
        elif action == "resize_left":
            win.moveTo(0,0)
            win.resizeTo(screen_width//2, screen_height)
        elif action == "resize_right":
            win.moveTo(screen_width//2,0)
            win.resizeTo(screen_width//2, screen_height)
        elif action == "close":
            win.close()
    except Exception as e:
        speak(f"Failed to {action} {app_name}: {e}")
    time.sleep(0.5)

# -------------------- PARSE VOICE COMMAND --------------------
def parse_command(command_text):
    apps = ["chrome", "notepad", "vlc", "whatsapp"]
    actions = {
        "maximize": ["maximize", "full screen", "fullscreen", "enlarge"],
        "minimize": ["minimize", "shrink", "hide"],
        "restore": ["restore", "normal"],
        "resize_left": ["left", "move left"],
        "resize_right": ["right", "move right"],
        "fullscreen": ["fullscreen", "full screen"],
        "close": ["close", "exit", "quit"]
    }

    app_name = None
    action_name = None

    for app in apps:
        if app in command_text:
            app_name = app
            break

    for action, keywords in actions.items():
        for kw in keywords:
            if kw in command_text:
                action_name = action
                break

    if app_name and action_name:
        return {"app": app_name, "action": action_name}
    return None

# -------------------- VOICE LOOP --------------------
def voice_loop():
    speak("Hello! I am ready for your command.")
    while True:
        command_text = listen_command()
        if not command_text:
            continue

        if "exit" in command_text or "quit" in command_text:
            ui_updater.update_text.emit("Goodbye 😘")
            speak("Goodbye 😘")
            QApplication.quit()
            break

        # Avatar thinking
        ui_updater.set_thinking_signal.emit()

        # parse command
        parsed = parse_command(command_text)
        if parsed:
            msg = f"{parsed['action'].capitalize()}ing {parsed['app']}"
            ui_updater.update_text.emit(msg)
            speak(msg)
            control_window(parsed["app"], parsed["action"])
        else:
            msg = "Sorry, I couldn't understand your command."
            ui_updater.update_text.emit(msg)
            speak(msg)

        # Back to idle
        ui_updater.set_idle_signal.emit()
        time.sleep(0.5)

# -------------------- START VOICE THREAD --------------------
threading.Thread(target=voice_loop, daemon=True).start()

# -------------------- RUN APP --------------------
sys.exit(app.exec_())
