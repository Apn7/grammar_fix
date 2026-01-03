import sys
import threading
import keyboard
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QObject, pyqtSignal

from groq_client import GroqClient
from clipboard_utils import get_selected_text, replace_selected_text
from overlay import OverlayWindow

# Worker signal to communicate from thread to GUI
class WorkerSignals(QObject):
    show_overlay = pyqtSignal(str, str)

class GrammarFixApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.groq = GroqClient()
        self.overlay = OverlayWindow()
        self.signals = WorkerSignals()
        
        # Connect signals
        self.signals.show_overlay.connect(self.overlay.show_suggestion)
        self.overlay.accepted.connect(self.handle_accept)
        
        # Setup System Tray
        self.tray_icon = QSystemTrayIcon(self.app)
        # We need an icon. For now, we'll use a standard system icon or create a simple pixmap if needed.
        # But QSystemTrayIcon might not show without a valid icon. 
        # Let's try to use a standard one if possible, or just proceed.
        # On Windows, it might be invisible if no icon is set.
        # Let's create a simple colored pixmap for the icon.
        from PyQt6.QtGui import QPixmap, QColor
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor("green"))
        self.tray_icon.setIcon(QIcon(pixmap))
        
        menu = QMenu()
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.app.quit)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        
        # Setup Hotkey
        # We use on_press_key to aggressively suppress the keys and manually check modifiers
        # This prevents the '1' or '2' from leaking to the focused app
        try:
            keyboard.on_press_key('1', self.check_hotkey_1, suppress=True)
            keyboard.on_press_key('!', self.check_hotkey_1, suppress=True)
            keyboard.on_press_key('2', self.check_hotkey_2, suppress=True)
            keyboard.on_press_key('@', self.check_hotkey_2, suppress=True)
        except Exception as e:
            print(f"Failed to set hotkey: {e}")
        
        print("Grammar Fix App is running...")

    def check_hotkey_1(self, e):
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('shift'):
            # Run in a separate thread to not block the hook
            threading.Thread(target=self.process_selection).start()
        else:
            # Not our hotkey, re-send the key
            keyboard.press(e.name)
            keyboard.release(e.name)

    def check_hotkey_2(self, e):
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('shift'):
            threading.Thread(target=self.process_translation).start()
        else:
            keyboard.press(e.name)
            keyboard.release(e.name)

    def process_selection(self):
        print("Grammar Hotkey detected!")
        # Small delay to ensure modifiers are released or processed
        import time
        time.sleep(0.5)
        
        text = get_selected_text()
        if text:
            print(f"Selected text: {text[:50]}...")
            corrected = self.groq.fix_grammar(text)
            if corrected:
                self.signals.show_overlay.emit(text, corrected)
            else:
                print("No correction returned or error.")
        else:
            print("No text selected.")

    def process_translation(self):
        print("Translation Hotkey detected!")
        # Small delay to ensure modifiers are released or processed
        import time
        time.sleep(0.5)
        
        text = get_selected_text()
        if text:
            print(f"Selected text for translation: {text[:50]}...")
            translated = self.groq.translate_text(text)
            if translated:
                self.signals.show_overlay.emit(text, translated)
            else:
                print("No translation returned or error.")
        else:
            print("No text selected.")

    def handle_accept(self, new_text):
        replace_selected_text(new_text)

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = GrammarFixApp()
    app.run()
