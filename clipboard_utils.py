import time

import keyboard
import pyperclip


def get_selected_text():
    original_clipboard = pyperclip.paste()
    pyperclip.copy("")

    time.sleep(0.05)
    keyboard.send("ctrl+c")

    selected_text = ""
    deadline = time.time() + 1.0
    while time.time() < deadline:
        time.sleep(0.05)
        selected_text = pyperclip.paste()
        if selected_text != "":
            break

    pyperclip.copy(original_clipboard)

    if selected_text == "":
        return None

    return selected_text


def replace_selected_text(new_text):
    original_clipboard = pyperclip.paste()
    pyperclip.copy(new_text)
    time.sleep(0.12)
    keyboard.send("ctrl+v")
    time.sleep(0.12)
    pyperclip.copy(original_clipboard)
