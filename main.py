import sys
import threading
import re

import keyboard
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from clipboard_utils import get_selected_text, replace_selected_text
from control_center import ControlCenterWindow
from overlay import OverlayWindow
from provider_manager import ProviderManager
from settings_manager import (
    get_selected_model,
    get_selected_provider,
    set_selected_model,
    set_selected_provider,
)
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

        self.provider_manager = ProviderManager()
        self.overlay = OverlayWindow()
        self.overlay.setWindowIcon(self.app_icon)
        self.control_center = ControlCenterWindow()
        self.control_center.setWindowIcon(self.app_icon)
        self.signals = WorkerSignals()

        self.request_counter = 0
        self.active_request_id = None
        self.startup_enabled = is_startup_enabled()
        self.selected_provider = get_selected_provider()
        self.active_request_provider = self.selected_provider
        self.selected_models = {
            "groq": get_selected_model("groq"),
            "google": get_selected_model("google"),
        }
        self.available_models = {
            "groq": self.provider_manager.refresh_models("groq"),
            "google": self.provider_manager.refresh_models("google"),
        }
        self.normalize_selected_models()

        self.signals.show_loading.connect(self.handle_show_loading)
        self.signals.update_original.connect(self.handle_update_original)
        self.signals.show_result.connect(self.handle_show_result)
        self.signals.show_error.connect(self.handle_show_error)
        self.overlay.accepted.connect(self.handle_accept)
        self.overlay.dismissed.connect(self.handle_dismiss)
        self.control_center.request_mode.connect(self.start_request)
        self.control_center.provider_changed.connect(self.change_provider)
        self.control_center.provider_model_changed.connect(self.change_provider_model)
        self.control_center.startup_toggled.connect(self.toggle_startup)
        self.control_center.quit_requested.connect(self.app.quit)
        self.control_center.hide_requested.connect(self.handle_hide_to_tray)

        self.control_center.set_startup_enabled(self.startup_enabled)
        self.control_center.set_selected_provider(self.selected_provider)
        self.sync_model_ui()
        self.control_center.set_status(
            "Ready in tray",
            f"Click the light-blue G in the system tray any time to reopen this control center. Active provider: {self.get_provider_label(self.selected_provider)} using {self.get_selected_provider_model(self.selected_provider)}.",
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

        provider_menu = menu.addMenu("AI Provider")
        self.provider_groq_action = provider_menu.addAction("Groq")
        self.provider_groq_action.setCheckable(True)
        self.provider_groq_action.triggered.connect(lambda: self.change_provider("groq"))

        self.provider_google_action = provider_menu.addAction("Google Gemini")
        self.provider_google_action.setCheckable(True)
        self.provider_google_action.triggered.connect(lambda: self.change_provider("google"))

        self.sync_provider_ui()

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
            f"Grammar Fix is still running in the tray and ready for shortcuts. Active provider: {self.get_provider_label(self.selected_provider)}.",
            tone="info",
        )

    def get_provider_label(self, provider):
        return self.provider_manager.get_provider_label(provider)

    def normalize_selected_models(self):
        for provider in ("groq", "google"):
            models = self.available_models.get(provider) or self.provider_manager.get_cached_models(provider)
            self.available_models[provider] = models
            selected = self.selected_models.get(provider)
            if selected not in models:
                selected = models[0]
                self.selected_models[provider] = selected
                set_selected_model(provider, selected)

    def get_selected_provider_model(self, provider):
        return self.selected_models.get(provider, self.provider_manager.get_default_model(provider))

    def sync_model_ui(self):
        self.control_center.set_model_options(
            "groq",
            self.available_models["groq"],
            self.selected_models["groq"],
        )
        self.control_center.set_model_options(
            "google",
            self.available_models["google"],
            self.selected_models["google"],
        )

    def sync_provider_ui(self):
        groq_selected = self.selected_provider == "groq"
        self.provider_groq_action.blockSignals(True)
        self.provider_google_action.blockSignals(True)
        self.provider_groq_action.setChecked(groq_selected)
        self.provider_google_action.setChecked(not groq_selected)
        self.provider_groq_action.blockSignals(False)
        self.provider_google_action.blockSignals(False)
        self.control_center.set_selected_provider(self.selected_provider)
        self.sync_model_ui()

    def change_provider(self, provider):
        self.selected_provider = set_selected_provider(provider)
        self.sync_provider_ui()
        self.control_center.set_status(
            "Provider updated",
            f"{self.get_provider_label(self.selected_provider)} is now active for all four tasks using {self.get_selected_provider_model(self.selected_provider)}.",
            tone="success",
        )

    def change_provider_model(self, provider, model):
        if model not in self.available_models.get(provider, []):
            return
        self.selected_models[provider] = set_selected_model(provider, model)
        if provider == self.selected_provider:
            self.control_center.set_status(
                "Model updated",
                f"{self.get_provider_label(provider)} will now use {model} for all four tasks.",
                tone="success",
            )

    def get_action_message(self, mode, provider):
        provider_label = self.get_provider_label(provider)
        model = self.get_selected_provider_model(provider)
        if mode == "translation":
            return f"Capturing your selection for translation with {provider_label} using {model}."
        if mode == "code_explain":
            return f"Capturing your selected code for line-by-line explanation with {provider_label} using {model}."
        if mode == "smart_text":
            return f"Reading your selected text and deciding whether a summary or explanation will help more with {provider_label} using {model}."
        return f"Capturing your selection for grammar fix with {provider_label} using {model}."

    def get_ready_message(self, mode, provider):
        provider_label = self.get_provider_label(provider)
        if mode == "translation":
            return f"Translation from {provider_label} is ready to review."
        if mode == "code_explain":
            return f"Code explanation from {provider_label} is ready to review."
        if mode == "smart_summary":
            return f"Bullet summary from {provider_label} is ready to review."
        if mode == "smart_explain":
            return f"Text explanation from {provider_label} is ready to review."
        return f"Grammar suggestion from {provider_label} is ready to review."

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
        provider = self.selected_provider
        self.active_request_provider = provider
        selected_model = self.get_selected_provider_model(provider)

        worker = threading.Thread(
            target=self.process_request,
            args=(request_id, mode, provider, selected_model),
            daemon=True,
        )
        worker.start()

        self.signals.show_loading.emit(request_id, mode)
        self.control_center.set_status("Working", self.get_action_message(mode, provider), tone="warning")

    def process_request(self, request_id, mode, provider, selected_model):
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
            client = self.provider_manager.get_client(provider, selected_model)
            if mode == "translation":
                result = client.translate_text(text)
            elif mode == "code_explain":
                result = client.explain_code(text)
            elif mode == "smart_text":
                mode = self.infer_text_assist_mode(text)
                if mode == "smart_summary":
                    result = client.summarize_text(text)
                else:
                    result = client.explain_text(text)
            else:
                result = client.fix_grammar(text)
        except ValueError:
            self.signals.show_error.emit(
                request_id,
                mode,
                f"{self.get_provider_label(provider)} is not configured yet. Add its API key to your local .env file and try again.",
                text,
            )
            return
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
            f"No result came back from {self.get_provider_label(provider)} using {selected_model}. Check that provider's API key, selected model, and your network connection, then try again.",
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
        self.control_center.set_status(
            "Ready",
            self.get_ready_message(mode, self.active_request_provider),
            tone="success",
        )

    def handle_show_error(self, request_id, mode, message, original_text):
        if request_id != self.active_request_id:
            return
        self.overlay.show_error(mode, message, original_text)
        self.control_center.set_status("Needs attention", message, tone="warning")

    def handle_dismiss(self):
        self.active_request_id = None
        self.active_request_provider = self.selected_provider
        self.control_center.set_status(
            "Ready in tray",
            "The request was dismissed. Select text any time and try again.",
            tone="info",
        )

    def handle_accept(self, mode, new_text):
        self.active_request_id = None
        self.active_request_provider = self.selected_provider
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
