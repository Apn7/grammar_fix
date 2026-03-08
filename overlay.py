from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QCursor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class OverlayWindow(QWidget):
    accepted = pyqtSignal(str)
    dismissed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        self.original_text = ""
        self.corrected_text = ""
        self.mode = "grammar"
        self.state = "idle"

        self.loading_frames = [
            "Refining your text",
            "Refining your text.",
            "Refining your text..",
            "Refining your text...",
        ]
        self.loading_frame_index = 0

        self.loading_timer = QTimer(self)
        self.loading_timer.setInterval(220)
        self.loading_timer.timeout.connect(self.advance_loading_frame)

        self.fade_animation = QPropertyAnimation(self, b"windowOpacity", self)
        self.fade_animation.setDuration(140)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.init_ui()

        QShortcut(QKeySequence("Escape"), self, activated=self.on_dismiss)
        QShortcut(QKeySequence("Return"), self, activated=self.on_accept)
        QShortcut(QKeySequence("Enter"), self, activated=self.on_accept)

    def init_ui(self):
        self.setStyleSheet(
            """
            QWidget {
                color: #e8eef7;
                font-family: "Segoe UI";
                background-color: #111827;
            }
            QFrame#container {
                background-color: #111827;
                border: 1px solid #243041;
                border-radius: 18px;
            }
            QLabel#eyebrow {
                color: #8fb7ff;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }
            QLabel#title {
                color: #f8fafc;
                font-size: 24px;
                font-weight: 700;
            }
            QLabel#subtitle {
                color: #9fb0c7;
                font-size: 13px;
            }
            QLabel#sectionTitle {
                color: #d9e2ef;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#statusBadge {
                background-color: #1d4ed8;
                color: white;
                border-radius: 11px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
            }
            QFrame#textPanel {
                background-color: #0b1220;
                border: 1px solid #223149;
                border-radius: 16px;
            }
            QPlainTextEdit {
                background: transparent;
                border: none;
                color: #f8fafc;
                font-size: 14px;
                selection-background-color: #2563eb;
                padding: 0;
            }
            QProgressBar {
                border: 1px solid #223149;
                border-radius: 7px;
                background-color: #0b1220;
                text-align: center;
                color: transparent;
                min-height: 12px;
                max-height: 12px;
            }
            QProgressBar::chunk {
                border-radius: 6px;
                background-color: #60a5fa;
            }
            QPushButton {
                min-height: 42px;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 700;
                padding: 0 18px;
            }
            QPushButton#primary {
                background-color: #2563eb;
                color: white;
                border: none;
            }
            QPushButton#primary:hover {
                background-color: #1d4ed8;
            }
            QPushButton#secondary {
                background-color: #172235;
                color: #e8eef7;
                border: 1px solid #293a54;
            }
            QPushButton#secondary:hover {
                background-color: #1f2d44;
            }
            QPushButton#ghost {
                background-color: transparent;
                color: #9fb0c7;
                border: 1px solid #293a54;
            }
            QPushButton#ghost:hover {
                color: #f8fafc;
                border-color: #4c6489;
            }
            QPushButton:disabled {
                background-color: #1e293b;
                color: #71839b;
                border-color: #243041;
            }
            """
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.container = QFrame(self)
        self.container.setObjectName("container")
        main_layout.addWidget(self.container)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(24, 22, 24, 24)
        container_layout.setSpacing(18)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(4)

        self.eyebrow_label = QLabel("Grammar Fix")
        self.eyebrow_label.setObjectName("eyebrow")
        header_text_layout.addWidget(self.eyebrow_label)

        self.title_label = QLabel("Ready when you are")
        self.title_label.setObjectName("title")
        self.title_label.setWordWrap(True)
        header_text_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel("Use the shortcut to refine selected text.")
        self.subtitle_label.setObjectName("subtitle")
        self.subtitle_label.setWordWrap(True)
        header_text_layout.addWidget(self.subtitle_label)

        header_layout.addLayout(header_text_layout, 1)

        self.status_badge = QLabel("Idle")
        self.status_badge.setObjectName("statusBadge")
        self.status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.status_badge, 0, Qt.AlignmentFlag.AlignTop)

        container_layout.addLayout(header_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.hide()
        container_layout.addWidget(self.progress_bar)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)

        self.original_panel = self.build_text_panel("Original")
        self.result_panel = self.build_text_panel("Result")
        self.original_edit = self.original_panel.findChild(QPlainTextEdit)
        self.result_edit = self.result_panel.findChild(QPlainTextEdit)

        content_layout.addWidget(self.original_panel)
        content_layout.addWidget(self.result_panel)
        container_layout.addLayout(content_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.dismiss_btn = QPushButton("Close")
        self.dismiss_btn.setObjectName("ghost")
        self.dismiss_btn.clicked.connect(self.on_dismiss)
        button_layout.addWidget(self.dismiss_btn)

        button_layout.addStretch(1)

        self.copy_btn = QPushButton("Copy Result")
        self.copy_btn.setObjectName("secondary")
        self.copy_btn.clicked.connect(self.copy_result)
        button_layout.addWidget(self.copy_btn)

        self.accept_btn = QPushButton("Replace Selection")
        self.accept_btn.setObjectName("primary")
        self.accept_btn.clicked.connect(self.on_accept)
        button_layout.addWidget(self.accept_btn)

        container_layout.addLayout(button_layout)

        self.resize(860, 420)
        self.setMinimumWidth(760)

        self.set_idle_state()

    def build_text_panel(self, title):
        panel = QFrame()
        panel.setObjectName("textPanel")
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)

        text_edit = QPlainTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFrameStyle(0)
        text_edit.setPlaceholderText(f"{title} text will appear here.")
        layout.addWidget(text_edit, 1)

        return panel

    def set_idle_state(self):
        self.state = "idle"
        self.mode = "grammar"
        self.original_text = ""
        self.corrected_text = ""
        self.set_mode_labels()
        self.set_status_badge("Idle", "#334155")
        self.title_label.setText("Ready when you are")
        self.subtitle_label.setText(
            "Press Ctrl+Shift+1 for grammar or Ctrl+Shift+2 for translation."
        )
        self.original_edit.setPlainText("")
        self.result_edit.setPlainText("")
        self.progress_bar.hide()
        self.copy_btn.setEnabled(False)
        self.accept_btn.setEnabled(False)

    def set_mode_labels(self):
        if self.mode == "translation":
            self.eyebrow_label.setText("Instant Translation")
            self.accept_btn.setText("Insert Translation")
        else:
            self.eyebrow_label.setText("Grammar Fix")
            self.accept_btn.setText("Replace Selection")

    def set_status_badge(self, text, color):
        self.status_badge.setText(text)
        self.status_badge.setStyleSheet(
            "background-color: {color}; color: white; border-radius: 11px; "
            "padding: 4px 10px; font-size: 11px; font-weight: 700;".format(
                color=color
            )
        )

    def show_loading(self, mode, original_text=""):
        self.mode = mode
        self.state = "loading"
        self.original_text = original_text or ""
        self.corrected_text = ""
        self.set_mode_labels()
        self.set_status_badge("Working", "#1d4ed8")
        self.title_label.setText("Getting your result ready")
        self.subtitle_label.setText(
            "Capturing your selection and preparing the result."
        )
        self.original_edit.setPlainText(self.original_text or "Capturing your selected text...")
        self.result_edit.setPlainText("Working on it...")
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.copy_btn.setEnabled(False)
        self.accept_btn.setEnabled(False)
        self.loading_frame_index = 0
        self.loading_timer.start()
        self.present(activate=False)

    def update_original_text(self, text):
        self.original_text = text
        if self.state == "loading":
            self.original_edit.setPlainText(text or "No text selected.")

    def show_result(self, mode, original, corrected):
        self.mode = mode
        self.state = "result"
        self.original_text = original
        self.corrected_text = corrected
        self.loading_timer.stop()
        self.set_mode_labels()
        self.set_status_badge("Ready", "#047857")
        self.title_label.setText("Review before you replace")
        self.subtitle_label.setText(
            "You can copy the result or insert it directly into the active app."
        )
        self.original_edit.setPlainText(original)
        self.result_edit.setPlainText(corrected)
        self.progress_bar.hide()
        self.copy_btn.setEnabled(True)
        self.accept_btn.setEnabled(True)
        self.present(activate=True)

    def show_error(self, mode, message, original_text=""):
        self.mode = mode
        self.state = "error"
        self.original_text = original_text or ""
        self.corrected_text = ""
        self.loading_timer.stop()
        self.set_mode_labels()
        self.set_status_badge("Needs Attention", "#b45309")
        self.title_label.setText("We hit a snag")
        self.subtitle_label.setText(message)
        self.original_edit.setPlainText(self.original_text or "No text was captured.")
        self.result_edit.setPlainText("Try again after selecting text in the target app.")
        self.progress_bar.hide()
        self.copy_btn.setEnabled(False)
        self.accept_btn.setEnabled(False)
        self.present(activate=True)

    def advance_loading_frame(self):
        frame = self.loading_frames[self.loading_frame_index]
        self.loading_frame_index = (self.loading_frame_index + 1) % len(
            self.loading_frames
        )
        self.result_edit.setPlainText(frame)

    def present(self, activate=True):
        self.position_near_cursor()
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, not activate)
        if not self.isVisible():
            self.setWindowOpacity(0.0)
            self.show()
        else:
            self.show()
        if activate:
            self.raise_()
            self.activateWindow()
        self.fade_animation.stop()
        self.fade_animation.start()

    def position_near_cursor(self):
        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos) or QApplication.primaryScreen()
        if screen is None:
            return

        available = screen.availableGeometry()
        width = min(max(self.minimumWidth(), 760), available.width() - 40)
        preferred_height = min(420, available.height() - 40)
        self.resize(width, max(360, preferred_height))

        target_x = cursor_pos.x() - (self.width() // 2)
        target_y = cursor_pos.y() - 70

        x = max(
            available.left() + 20,
            min(target_x, available.right() - self.width() - 20),
        )
        y = max(
            available.top() + 20,
            min(target_y, available.bottom() - self.height() - 20),
        )
        self.move(x, y)

    def copy_result(self):
        if not self.corrected_text:
            return
        QApplication.clipboard().setText(self.corrected_text)
        self.set_status_badge("Copied", "#4338ca")

    def on_accept(self):
        if self.state != "result" or not self.corrected_text:
            return
        self.hide()
        self.accepted.emit(self.corrected_text)

    def on_dismiss(self):
        self.loading_timer.stop()
        self.hide()
        self.dismissed.emit()
