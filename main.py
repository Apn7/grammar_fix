import sys
import threading

import keyboard
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from clipboard_utils import get_selected_text, replace_selected_text
from groq_client import GroqClient
from overlay import OverlayWindow


class WorkerSignals(QObject):
    show_loading = pyqtSignal(int, str)
    update_original = pyqtSignal(int, str)
    show_result = pyqtSignal(int, str, str, str)
    show_error = pyqtSignal(int, str, str, str)


class GrammarFixApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.groq = GroqClient()
        self.overlay = OverlayWindow()
        self.signals = WorkerSignals()

        self.request_counter = 0
        self.active_request_id = None

        self.signals.show_loading.connect(self.handle_show_loading)
        self.signals.update_original.connect(self.handle_update_original)
        self.signals.show_result.connect(self.handle_show_result)
        self.signals.show_error.connect(self.handle_show_error)
        self.overlay.accepted.connect(self.handle_accept)
        self.overlay.dismissed.connect(self.handle_dismiss)

        self.setup_tray()
        self.setup_hotkeys()
        self.app.aboutToQuit.connect(self.cleanup_hotkeys)

        print("Grammar Fix App is running...")

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self.app)
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor("#22c55e"))
        self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.setToolTip("Grammar Fix")

        menu = QMenu()
        show_action = menu.addAction("Show Panel")
        show_action.triggered.connect(self.show_panel)

        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.app.quit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def setup_hotkeys(self):
        try:
            keyboard.add_hotkey(
                "ctrl+shift+1",
                lambda: self.start_request("grammar"),
                suppress=True,
                trigger_on_release=True,
            )
            keyboard.add_hotkey(
                "ctrl+shift+2",
                lambda: self.start_request("translation"),
                suppress=True,
                trigger_on_release=True,
            )
        except Exception as error:
            print(f"Failed to set hotkeys: {error}")

    def cleanup_hotkeys(self):
        try:
            keyboard.clear_all_hotkeys()
        except Exception as error:
            print(f"Failed to clear hotkeys: {error}")

    def show_panel(self):
        if self.overlay.state == "idle":
            self.overlay.set_idle_state()
        self.overlay.present(activate=True)

    def start_request(self, mode):
        self.request_counter += 1
        request_id = self.request_counter
        self.active_request_id = request_id

        worker = threading.Thread(
            target=self.process_request,
            args=(request_id, mode),
            daemon=True,
        )
        worker.start()

        self.signals.show_loading.emit(request_id, mode)

    def process_request(self, request_id, mode):
        text = get_selected_text()
        self.signals.update_original.emit(request_id, text or "")

        if request_id != self.active_request_id:
            return

        if text is None:
            self.signals.show_error.emit(
                request_id,
                mode,
                "Select text in the target app, then try the shortcut again.",
                "",
            )
            return

        try:
            if mode == "translation":
                result = self.groq.translate_text(text)
            else:
                result = self.groq.fix_grammar(text)
        except Exception as error:
            result = None
            print(f"Unexpected processing error: {error}")

        if request_id != self.active_request_id:
            return

        if result:
            self.signals.show_result.emit(request_id, mode, text, result)
            return

        self.signals.show_error.emit(
            request_id,
            mode,
            "No result came back. Check your Groq API key or network connection and try again.",
            text,
        )

    def handle_show_loading(self, request_id, mode):
        if request_id != self.active_request_id:
            return
        self.overlay.show_loading(mode)

    def handle_update_original(self, request_id, text):
        if request_id != self.active_request_id:
            return
        self.overlay.update_original_text(text)

    def handle_show_result(self, request_id, mode, original, result):
        if request_id != self.active_request_id:
            return
        self.overlay.show_result(mode, original, result)

    def handle_show_error(self, request_id, mode, message, original_text):
        if request_id != self.active_request_id:
            return
        self.overlay.show_error(mode, message, original_text)

    def handle_dismiss(self):
        self.active_request_id = None

    def handle_accept(self, new_text):
        self.active_request_id = None
        replace_selected_text(new_text)

    def run(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app = GrammarFixApp()
    app.run()
