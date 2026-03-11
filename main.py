import sys
import threading
import time
import webbrowser
import urllib.parse
import os
import psutil
import pygetwindow as gw
import pyautogui
import pyttsx3
import win32gui
import win32con
import win32process

def control_window(app_name, action):
    app_name_lower = app_name.lower()
    found = []

    # Iterate over all top-level windows
    def enum_windows(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd).lower()
            if app_name_lower in title:
                found.append(hwnd)
        return True

    win32gui.EnumWindows(enum_windows, None)

    if not found:
        # fallback: check process names
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'] and app_name_lower in proc.info['name'].lower():
                    def enum_proc_windows(hwnd, pid):
                        _, wnd_pid = win32process.GetWindowThreadProcessId(hwnd)
                        if wnd_pid == pid and win32gui.IsWindowVisible(hwnd):
                            found.append(hwnd)
                    win32gui.EnumWindows(enum_proc_windows, proc.info['pid'])
            except Exception:
                continue

    if not found:
        print(f"No window found for '{app_name}'")
        return

    hwnd = found[0]
    screen_width, screen_height = pyautogui.size()

    if action == "maximize":
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    elif action == "minimize":
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    elif action == "restore":
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    elif action == "fullscreen":
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0,
                              screen_width, screen_height, win32con.SWP_SHOWWINDOW)
    elif action == "resize_left":
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0,
                              screen_width // 2, screen_height, win32con.SWP_SHOWWINDOW)
    elif action == "resize_right":
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, screen_width // 2, 0,
                              screen_width // 2, screen_height, win32con.SWP_SHOWWINDOW)
    elif action == "close":
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    time.sleep(0.5)  # small delay for the action to complete

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

from avatar import Avatar
from ai_engine import get_pc_action
from pc_controller import execute_action
from voice_input import listen_command

# -------------------- APP INIT --------------------
app = QApplication(sys.argv)
avatar = Avatar()
avatar.show()

# -------------------- SIGNALS --------------------
class UIUpdater(QObject):
    update_text = pyqtSignal(str)
    set_idle_signal = pyqtSignal()
    set_thinking_signal = pyqtSignal()

ui_updater = UIUpdater()
ui_updater.update_text.connect(avatar.speak_text)
ui_updater.set_idle_signal.connect(avatar.set_idle)
ui_updater.set_thinking_signal.connect(avatar.set_thinking)

# -------------------- OFFLINE TTS --------------------
engine = pyttsx3.init()
engine.setProperty('rate', 160)   # slower, readable
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
for v in voices:
    if "female" in v.name.lower() or "zira" in v.name.lower():
        engine.setProperty('voice', v.id)
        break

naughty_templates = [
    "Hmm… I like the way you said that 😏",
    "Oh really? Tell me more 😌",
    "You’re making me blush 😳",
    "Hehe, you’re so cheeky 😜",
    "Aww, that’s cute… keep talking 💕"
]

def flirty_reply(base_text):
    import random
    return f"{base_text} {random.choice(naughty_templates)}"

def speak(text):
    engine.say(text)
    engine.runAndWait()  # blocks until done


def control_window(app_name, action):
    app_name_lower = app_name.lower()
    windows = []

    # Try matching exact titles or process names
    for w in gw.getAllWindows():
        if w.title and app_name_lower in w.title.lower():
            windows.append(w)

    if not windows:
        # fallback: match by process name
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and app_name_lower in proc.info['name'].lower():
                    win_list = gw.getWindowsWithTitle(proc.name())
                    windows.extend(win_list)
            except Exception:
                continue

    if not windows:
        print(f"No window found for '{app_name}'")
        return

    # Control the first window found
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
            win.moveTo(0, 0)
            win.resizeTo(screen_width, screen_height)
        elif action == "resize_left":
            win.moveTo(0, 0)
            win.resizeTo(screen_width // 2, screen_height)
        elif action == "resize_right":
            win.moveTo(screen_width // 2, 0)
            win.resizeTo(screen_width // 2, screen_height)
        elif action == "close":
            win.close()
    except Exception as e:
        print(f"Failed to {action} {app_name}: {e}")


# -------------------- OPEN APP --------------------
def open_app(app_name):
    app_name_lower = app_name.lower().strip()
    if app_name_lower in ["notepad"]:
        os.system("start notepad")
    elif app_name_lower in ["chrome", "google chrome"]:
        os.system("start chrome")
    elif app_name_lower in ["vlc", "vlc player"]:
        os.system("start vlc")
    elif app_name_lower in ["whatsapp", "whatsapp desktop"]:
        path = r"C:\Users\%USERNAME%\AppData\Local\WhatsApp\WhatsApp.exe"
        if os.path.exists(os.path.expandvars(path)):
            os.startfile(os.path.expandvars(path))
        else:
            print("WhatsApp path not found!")

    # Wait a little for the window to appear
    time.sleep(2)


# -------------------- WEBSITE SEARCH --------------------
SITE_SEARCH_URLS = {
    "youtube": "https://www.youtube.com/results?search_query={query}",
    "google": "https://www.google.com/search?q={query}",
    "wikipedia": "https://en.wikipedia.org/wiki/Special:Search?search={query}",
    "bing": "https://www.bing.com/search?q={query}",
    "duckduckgo": "https://duckduckgo.com/?q={query}",
}

def ensure_chrome_open():
    chrome_running = any(proc.info['name'] and 'chrome.exe' in proc.info['name'].lower() for proc in psutil.process_iter(['name']))
    if not chrome_running:
        os.system("start chrome")
        time.sleep(2)

def search_website_chrome(query, site_name):
    # Make sure Chrome is running
    chrome_running = any(
        proc.info['name'] and 'chrome.exe' in proc.info['name'].lower()
        for proc in psutil.process_iter(['name'])
    )
    if not chrome_running:
        os.system("start chrome")
        time.sleep(2)  # wait for Chrome

    # Build URL
    site_name = site_name.lower()
    encoded_query = urllib.parse.quote(query)
    if site_name in SITE_SEARCH_URLS:
        url = SITE_SEARCH_URLS[site_name].format(query=encoded_query)
    else:
        url = f"https://{site_name}/search?q={encoded_query}"

    # Open in Chrome
    os.system(f'start chrome "{url}"')


# -------------------- VOICE LOOP --------------------
def voice_loop():
    while True:
        command = listen_command()
        if not command:
            continue

        if "exit" in command.lower():
            ui_updater.update_text.emit("Goodbye, handsome 😘")
            speak("Goodbye, handsome 😘")
            QApplication.quit()
            break

        ui_updater.set_thinking_signal.emit()
        action_json = get_pc_action(command)
        if not action_json:
            msg = "Sorry, I didn't understand 😅"
            ui_updater.update_text.emit(msg)
            speak(msg)
            ui_updater.set_idle_signal.emit()
            continue

        response_type = action_json.get("type")

        # -------------------- CHAT --------------------
        if response_type == "chat":
            reply = action_json.get("response")
            for part in reply.split(","):
                text_part = part.strip()
                ui_updater.update_text.emit(text_part)
                speak(text_part)
                time.sleep(1)
            ui_updater.set_idle_signal.emit()
            continue

        # -------------------- COMMAND --------------------
        elif response_type == "command":
            action = action_json.get("action")
            app_name = action_json.get("app", "")

            # Website search
            if action == "website_search":
                site = action_json.get("site", "")
                query = action_json.get("query", "")
                if site and query:
                    msg = f"Searching {site} for '{query}', sir 😏"
                    ui_updater.update_text.emit(msg)
                    speak(msg)
                    search_website_chrome(query, site)  # opens Chrome and searches
                else:
                    msg = "Sorry sir, I couldn't understand the site or query."
                    ui_updater.update_text.emit(msg)
                    speak(msg)
                ui_updater.set_idle_signal.emit()
                continue

            # Window control
            if action == "window_control":
                window_action = action_json.get("window_action", "maximize")
                msg = f"{window_action.capitalize()}ing {app_name}, sir 😏"
                ui_updater.update_text.emit(msg)
                speak(msg)
                control_window(app_name, window_action)
                time.sleep(1)
                ui_updater.set_idle_signal.emit()
                continue

            # Close app
            if action == "close_app":
                msg = f"Closing {app_name}, sir 😌"
                ui_updater.update_text.emit(msg)
                speak(msg)
                control_window(app_name, "close")
                time.sleep(1)
                ui_updater.set_idle_signal.emit()
                continue

            # Open app
            if action == "open_app":
                msg = f"Opening {app_name}, sir 😉"
                ui_updater.update_text.emit(msg)
                speak(msg)
                open_app(app_name)
                time.sleep(1)
                ui_updater.set_idle_signal.emit()
                continue

# -------------------- START VOICE THREAD --------------------
threading.Thread(target=voice_loop, daemon=True).start()

# -------------------- RUN APP --------------------
sys.exit(app.exec_())
