import sys
import threading
import re

import keyboard
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from clipboard_utils import get_selected_text, replace_selected_text
from control_center import ControlCenterWindow
from groq_client import GroqClient
from overlay import OverlayWindow
from startup_manager import is_startup_enabled, set_startup_enabled


class WorkerSignals(QObject):
    show_loading = pyqtSignal(int, str)
    update_original = pyqtSignal(int, str)
    show_result = pyqtSignal(int, str, str, str)
    show_error = pyqtSignal(int, str, str, str)


class GrammarFixApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.app_icon = self.build_app_icon()
        self.app.setWindowIcon(self.app_icon)

        self.groq = GroqClient()
        self.overlay = OverlayWindow()
        self.overlay.setWindowIcon(self.app_icon)
        self.control_center = ControlCenterWindow()
        self.control_center.setWindowIcon(self.app_icon)
        self.signals = WorkerSignals()

        self.request_counter = 0
        self.active_request_id = None
        self.startup_enabled = is_startup_enabled()

        self.signals.show_loading.connect(self.handle_show_loading)
        self.signals.update_original.connect(self.handle_update_original)
        self.signals.show_result.connect(self.handle_show_result)
        self.signals.show_error.connect(self.handle_show_error)
        self.overlay.accepted.connect(self.handle_accept)
        self.overlay.dismissed.connect(self.handle_dismiss)
        self.control_center.request_mode.connect(self.start_request)
        self.control_center.startup_toggled.connect(self.toggle_startup)
        self.control_center.quit_requested.connect(self.app.quit)
        self.control_center.hide_requested.connect(self.handle_hide_to_tray)

        self.control_center.set_startup_enabled(self.startup_enabled)
        self.control_center.set_status(
            "Ready in tray",
            "Click the light-blue G in the system tray any time to reopen this control center.",
            tone="info",
        )

        self.setup_tray()
        self.setup_hotkeys()
        self.app.aboutToQuit.connect(self.cleanup_hotkeys)

        print("Grammar Fix App is running...")

    def build_app_icon(self):
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, size, size)
        gradient.setColorAt(0.0, QColor("#7dd3fc"))
        gradient.setColorAt(1.0, QColor("#38bdf8"))

        path = QPainterPath()
        path.addRoundedRect(4, 4, size - 8, size - 8, 18, 18)
        painter.fillPath(path, gradient)

        painter.setPen(QPen(QColor("#e0f2fe"), 1.5))
        painter.drawPath(path)

        font = QFont("Segoe UI", 28)
        font.setWeight(QFont.Weight.Black)
        painter.setFont(font)
        painter.setPen(QColor("#082f49"))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "G")

        painter.end()
        return QIcon(pixmap)

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self.app_icon, self.app)
        self.tray_icon.setToolTip("Grammar Fix")
        self.tray_icon.activated.connect(self.handle_tray_activation)

        menu = QMenu()

        open_action = menu.addAction("Open Control Center")
        open_action.triggered.connect(self.show_control_center)

        grammar_action = menu.addAction("Fix Selected Text")
        grammar_action.triggered.connect(lambda: self.start_request("grammar"))

        translation_action = menu.addAction("Translate Selection")
        translation_action.triggered.connect(lambda: self.start_request("translation"))

        explain_action = menu.addAction("Explain Selected Code")
        explain_action.triggered.connect(lambda: self.start_request("code_explain"))

        smart_text_action = menu.addAction("Summarize or Explain Text")
        smart_text_action.triggered.connect(lambda: self.start_request("smart_text"))

        menu.addSeparator()

        self.startup_action = menu.addAction("Start With Windows")
        self.startup_action.setCheckable(True)
        self.startup_action.setChecked(self.startup_enabled)
        self.startup_action.toggled.connect(self.toggle_startup)

        menu.addSeparator()

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
            keyboard.add_hotkey(
                "ctrl+shift+3",
                lambda: self.start_request("code_explain"),
                suppress=True,
                trigger_on_release=True,
            )
            keyboard.add_hotkey(
                "ctrl+shift+4",
                lambda: self.start_request("smart_text"),
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

    def handle_tray_activation(self, reason):
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.show_control_center()

    def show_control_center(self):
        self.control_center.present()

    def handle_hide_to_tray(self):
        self.control_center.set_status(
            "Ready in tray",
            "Grammar Fix is still running in the tray and ready for shortcuts.",
            tone="info",
        )

    def get_action_message(self, mode):
        if mode == "translation":
            return "Capturing your selection for translation."
        if mode == "code_explain":
            return "Capturing your selected code for line-by-line explanation."
        if mode == "smart_text":
            return "Reading your selected text and deciding whether a summary or explanation will help more."
        return "Capturing your selection for grammar fix."

    def get_ready_message(self, mode):
        if mode == "translation":
            return "Translation is ready to review."
        if mode == "code_explain":
            return "Code explanation is ready to review."
        if mode == "smart_summary":
            return "Bullet summary is ready to review."
        if mode == "smart_explain":
            return "Text explanation is ready to review."
        return "Grammar suggestion is ready to review."

    def infer_text_assist_mode(self, text):
        normalized = text.strip()
        if not normalized:
            return "smart_explain"

        words = len(normalized.split())
        lines = [line for line in normalized.splitlines() if line.strip()]
        sentences = len(re.findall(r"[.!?]+", normalized))
        average_line_length = words / max(len(lines), 1)

        if words >= 120 or len(lines) >= 8 or sentences >= 4 or average_line_length >= 22:
            return "smart_summary"
        return "smart_explain"

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
        self.control_center.set_status("Working", self.get_action_message(mode), tone="warning")

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
            elif mode == "code_explain":
                result = self.groq.explain_code(text)
            elif mode == "smart_text":
                mode = self.infer_text_assist_mode(text)
                if mode == "smart_summary":
                    result = self.groq.summarize_text(text)
                else:
                    result = self.groq.explain_text(text)
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

    def toggle_startup(self, enabled):
        success, message = set_startup_enabled(enabled)
        self.startup_enabled = is_startup_enabled()

        self.startup_action.blockSignals(True)
        self.startup_action.setChecked(self.startup_enabled)
        self.startup_action.blockSignals(False)

        self.control_center.set_startup_enabled(self.startup_enabled)
        tone = "success" if success else "warning"
        title = "Startup updated" if success else "Startup issue"
        self.control_center.set_status(title, message, tone=tone)

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
        self.control_center.set_status("Ready", self.get_ready_message(mode), tone="success")

    def handle_show_error(self, request_id, mode, message, original_text):
        if request_id != self.active_request_id:
            return
        self.overlay.show_error(mode, message, original_text)
        self.control_center.set_status("Needs attention", message, tone="warning")

    def handle_dismiss(self):
        self.active_request_id = None
        self.control_center.set_status(
            "Ready in tray",
            "The request was dismissed. Select text any time and try again.",
            tone="info",
        )

    def handle_accept(self, mode, new_text):
        self.active_request_id = None
        if mode in {"code_explain", "smart_summary", "smart_explain"}:
            QApplication.clipboard().setText(new_text)
            if mode == "smart_summary":
                message = "The summary was copied to your clipboard."
            elif mode == "smart_explain":
                message = "The explanation was copied to your clipboard."
            else:
                message = "The code explanation was copied to your clipboard."
            self.control_center.set_status(
                "Copied",
                message,
                tone="success",
            )
            return

        replace_selected_text(new_text)
        self.control_center.set_status(
            "Inserted",
            "The result was pasted back into the active app.",
            tone="success",
        )

    def run(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app = GrammarFixApp()
    app.run()
