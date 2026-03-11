import os
import subprocess
import webbrowser
import pyautogui
import time
import subprocess

def execute_action(action_json):
    action = action_json.get("action")

    if action == "open_app":
        app = action_json.get("app")

        if app == "notepad":
            subprocess.Popen("notepad")
        elif app == "chrome":
            os.system("start chrome")

    elif action == "close_app":
        app = action_json.get("app")

        if app == "notepad":
            os.system("taskkill /f /im notepad.exe")
        elif app == "chrome":
            os.system("taskkill /f /im chrome.exe")

    elif action == "open_website":
        import webbrowser
        webbrowser.open(action_json.get("url"))

    elif action == "type_text":
        import pyautogui
        import time
        time.sleep(1)
        pyautogui.write(action_json.get("text"))
