from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QCursor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QBoxLayout,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ControlCenterWindow(QWidget):
    request_mode = pyqtSignal(str)
    provider_changed = pyqtSignal(str)
    provider_model_changed = pyqtSignal(str, str)
    startup_toggled = pyqtSignal(bool)
    quit_requested = pyqtSignal()
    hide_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setObjectName("root")
        self.setWindowTitle("Grammar Fix")
        self.resize(720, 520)
        self.setMinimumSize(620, 440)
        self.setWindowState(Qt.WindowState.WindowNoState)
        self.init_ui()
        self.update_responsive_layouts()

        QShortcut(QKeySequence("Escape"), self, activated=self.hide_to_tray)

    def init_ui(self):
        self.setStyleSheet(
            """
            QWidget {
                color: #d9e7fb;
                font-family: "Segoe UI";
                background: transparent;
            }
            QWidget#root {
                background-color: #08111f;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QFrame#surface {
                background-color: #0d1a2d;
                border: 1px solid #1b3151;
                border-radius: 24px;
            }
            QFrame#card {
                background-color: #0f213b;
                border: 1px solid #203857;
                border-radius: 20px;
            }
            QLabel#eyebrow {
                color: #7dd3fc;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }
            QLabel#title {
                color: #f8fbff;
                font-size: 34px;
                font-weight: 700;
            }
            QLabel#subtitle {
                color: #9bb2d3;
                font-size: 14px;
                line-height: 1.35;
            }
            QLabel#sectionTitle {
                color: #f8fbff;
                font-size: 17px;
                font-weight: 700;
            }
            QLabel#body {
                color: #9bb2d3;
                font-size: 13px;
                line-height: 1.35;
            }
            QLabel#statusPill {
                background-color: #0a7b68;
                color: #e8fff8;
                border-radius: 14px;
                padding: 7px 14px;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#shortcutLabel {
                color: #f8fbff;
                font-size: 14px;
                font-weight: 600;
            }
            QLabel#shortcutBadge {
                background-color: #08111f;
                color: #8fd9ff;
                border: 1px solid #21415f;
                border-radius: 12px;
                padding: 9px 12px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton {
                min-height: 46px;
                border-radius: 14px;
                padding: 0 18px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton#primary {
                background-color: #46c4ff;
                color: #08243a;
                border: none;
            }
            QPushButton#primary:hover {
                background-color: #7dd3fc;
            }
            QPushButton#secondary {
                background-color: #183252;
                color: #e7f0ff;
                border: 1px solid #2d5076;
            }
            QPushButton#secondary:hover {
                background-color: #214066;
            }
            QPushButton#ghost {
                background-color: transparent;
                color: #d9e7fb;
                border: 1px solid #2d5076;
            }
            QPushButton#ghost:hover {
                border-color: #7dd3fc;
                color: #f8fbff;
            }
            QCheckBox {
                color: #f8fbff;
                font-size: 14px;
                font-weight: 600;
                spacing: 12px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 1px solid #43658e;
                background-color: #08111f;
            }
            QCheckBox::indicator:checked {
                background-color: #46c4ff;
                border: 1px solid #46c4ff;
            }
            QRadioButton {
                color: #f8fbff;
                font-size: 14px;
                font-weight: 600;
                spacing: 10px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 1px solid #43658e;
                background-color: #08111f;
            }
            QRadioButton::indicator:checked {
                border: 5px solid #46c4ff;
                background-color: #08111f;
            }
            QComboBox {
                min-height: 42px;
                border-radius: 12px;
                padding: 0 14px;
                font-size: 13px;
                font-weight: 600;
                color: #f8fbff;
                background-color: #132844;
                border: 1px solid #2d5076;
            }
            QComboBox::drop-down {
                border: none;
                width: 28px;
            }
            QComboBox QAbstractItemView {
                color: #f8fbff;
                background-color: #0f213b;
                border: 1px solid #2d5076;
                selection-background-color: #214066;
            }
            """
        )

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 12, 12, 12)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root_layout.addWidget(self.scroll_area)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        surface = QFrame(scroll_content)
        surface.setObjectName("surface")
        surface.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        scroll_layout.addWidget(surface)
        self.scroll_area.setWidget(scroll_content)

        layout = QVBoxLayout(surface)
        layout.setContentsMargins(22, 22, 22, 20)
        layout.setSpacing(14)

        self.header_row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.header_row.setSpacing(16)

        header_text = QVBoxLayout()
        header_text.setSpacing(6)

        eyebrow = QLabel("Control Center")
        eyebrow.setObjectName("eyebrow")
        header_text.addWidget(eyebrow)

        self.title_label = QLabel("Grammar Fix")
        self.title_label.setObjectName("title")
        header_text.addWidget(self.title_label)

        subtitle = QLabel(
            "A polished tray companion for fixing grammar, translating text, explaining code, and making dense text easier to understand."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        header_text.addWidget(subtitle)

        self.header_row.addLayout(header_text, 1)

        self.status_pill = QLabel("Ready in tray")
        self.status_pill.setObjectName("statusPill")
        self.status_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_pill.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.header_row.addWidget(self.status_pill)

        layout.addLayout(self.header_row)

        provider_card = self.build_card(
            "AI Provider",
            "Choose which provider powers all four shortcuts across the app.",
        )
        provider_layout = provider_card.layout()

        self.provider_row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.provider_row.setSpacing(18)

        self.provider_group = QButtonGroup(self)
        self.provider_group.setExclusive(True)

        self.groq_radio = QRadioButton("Groq")
        self.google_radio = QRadioButton("Google Gemini")
        self.provider_group.addButton(self.groq_radio)
        self.provider_group.addButton(self.google_radio)
        self.provider_row.addWidget(self.groq_radio)
        self.provider_row.addWidget(self.google_radio)
        self.provider_row.addStretch(1)

        self.groq_radio.toggled.connect(lambda checked: self.on_provider_selected("groq", checked))
        self.google_radio.toggled.connect(lambda checked: self.on_provider_selected("google", checked))

        provider_layout.addLayout(self.provider_row)

        self.provider_hint_label = QLabel("Groq is active for all shortcuts.")
        self.provider_hint_label.setObjectName("body")
        self.provider_hint_label.setWordWrap(True)
        provider_layout.addWidget(self.provider_hint_label)

        provider_models_grid = QGridLayout()
        provider_models_grid.setHorizontalSpacing(12)
        provider_models_grid.setVerticalSpacing(10)

        groq_model_label = QLabel("Groq model")
        groq_model_label.setObjectName("body")
        provider_models_grid.addWidget(groq_model_label, 0, 0)

        self.groq_model_combo = QComboBox()
        self.groq_model_combo.currentTextChanged.connect(
            lambda model: self.on_provider_model_changed("groq", model)
        )
        provider_models_grid.addWidget(self.groq_model_combo, 1, 0)

        google_model_label = QLabel("Google model")
        google_model_label.setObjectName("body")
        provider_models_grid.addWidget(google_model_label, 0, 1)

        self.google_model_combo = QComboBox()
        self.google_model_combo.currentTextChanged.connect(
            lambda model: self.on_provider_model_changed("google", model)
        )
        provider_models_grid.addWidget(self.google_model_combo, 1, 1)

        provider_layout.addLayout(provider_models_grid)

        layout.addWidget(provider_card)

        quick_actions = self.build_card(
            "Quick Actions",
            "Launch the core workflows directly from here or keep using the global shortcuts.",
        )
        quick_layout = quick_actions.layout()

        self.quick_button_row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.quick_button_row.setSpacing(12)

        grammar_button = QPushButton("Fix Selected Text")
        grammar_button.setObjectName("primary")
        grammar_button.clicked.connect(lambda: self.request_mode.emit("grammar"))
        self.quick_button_row.addWidget(grammar_button)

        translation_button = QPushButton("Translate Selection")
        translation_button.setObjectName("secondary")
        translation_button.clicked.connect(lambda: self.request_mode.emit("translation"))
        self.quick_button_row.addWidget(translation_button)

        explain_button = QPushButton("Explain Selected Code")
        explain_button.setObjectName("ghost")
        explain_button.clicked.connect(lambda: self.request_mode.emit("code_explain"))
        self.quick_button_row.addWidget(explain_button)

        smart_text_button = QPushButton("Summarize or Explain Text")
        smart_text_button.setObjectName("secondary")
        smart_text_button.clicked.connect(lambda: self.request_mode.emit("smart_text"))
        self.quick_button_row.addWidget(smart_text_button)

        quick_layout.addLayout(self.quick_button_row)
        layout.addWidget(quick_actions)

        self.middle_row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.middle_row.setSpacing(14)

        startup_card = self.build_card(
            "Launch Behavior",
            "Keep Grammar Fix ready after sign-in so the shortcuts are always available.",
        )
        startup_layout = startup_card.layout()

        self.startup_checkbox = QCheckBox("Open automatically when Windows starts")
        self.startup_checkbox.toggled.connect(self.startup_toggled.emit)
        startup_layout.addWidget(self.startup_checkbox)

        self.startup_hint = QLabel("Startup is currently disabled.")
        self.startup_hint.setObjectName("body")
        self.startup_hint.setWordWrap(True)
        startup_layout.addWidget(self.startup_hint)
        startup_layout.addStretch(1)
        self.middle_row.addWidget(startup_card, 1)

        shortcuts_card = self.build_card(
            "Keyboard Shortcuts",
            "Use these from anywhere after selecting text in the target app.",
        )
        shortcuts_layout = shortcuts_card.layout()

        shortcuts_grid = QGridLayout()
        shortcuts_grid.setHorizontalSpacing(10)
        shortcuts_grid.setVerticalSpacing(10)
        shortcuts_grid.addWidget(self.build_shortcut_item("Grammar fix", "Ctrl+Shift+1"), 0, 0)
        shortcuts_grid.addWidget(self.build_shortcut_item("Translate selection", "Ctrl+Shift+2"), 0, 1)
        shortcuts_grid.addWidget(self.build_shortcut_item("Explain code", "Ctrl+Shift+3"), 1, 0)
        shortcuts_grid.addWidget(self.build_shortcut_item("Smart text help", "Ctrl+Shift+4"), 1, 1)
        shortcuts_layout.addLayout(shortcuts_grid)
        shortcuts_layout.addStretch(1)
        self.middle_row.addWidget(shortcuts_card, 1)

        layout.addLayout(self.middle_row)

        tray_card = self.build_card(
            "Tray Experience",
            "Click the light-blue G in the tray to reopen this control center, or use the tray menu for grammar, translation, code explanation, smart text help, startup, and quit.",
        )
        layout.addWidget(tray_card)

        footer_card = QFrame()
        footer_card.setObjectName("card")
        self.footer_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight, footer_card)
        self.footer_layout.setContentsMargins(18, 16, 18, 16)
        self.footer_layout.setSpacing(12)

        self.message_label = QLabel(
            "Select text in any app and use the shortcuts when you are ready."
        )
        self.message_label.setObjectName("body")
        self.message_label.setWordWrap(True)
        self.footer_layout.addWidget(self.message_label, 1)

        hide_button = QPushButton("Hide to Tray")
        hide_button.setObjectName("ghost")
        hide_button.clicked.connect(self.hide_to_tray)
        self.footer_layout.addWidget(hide_button)

        quit_button = QPushButton("Quit App")
        quit_button.setObjectName("secondary")
        quit_button.clicked.connect(self.quit_requested.emit)
        self.footer_layout.addWidget(quit_button)

        layout.addWidget(footer_card)

    def build_card(self, title, body):
        card = QFrame()
        card.setObjectName("card")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        body_label = QLabel(body)
        body_label.setObjectName("body")
        body_label.setWordWrap(True)
        layout.addWidget(body_label)

        return card

    def build_shortcut_item(self, label_text, shortcut_text):
        item = QFrame()
        item.setObjectName("card")
        item.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout = QVBoxLayout(item)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        label = QLabel(label_text)
        label.setObjectName("shortcutLabel")
        label.setWordWrap(True)
        layout.addWidget(label)

        badge = QLabel(shortcut_text)
        badge.setObjectName("shortcutBadge")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setWordWrap(True)
        layout.addWidget(badge)

        hint = QLabel("Select text first, then run the shortcut.")
        hint.setObjectName("body")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        return item

    def update_responsive_layouts(self):
        content_width = self.scroll_area.viewport().width() or self.width()
        header_compact = content_width < 760
        provider_compact = content_width < 760
        quick_compact = content_width < 980
        middle_compact = content_width < 760
        footer_compact = content_width < 760

        self.header_row.setDirection(
            QBoxLayout.Direction.TopToBottom if header_compact else QBoxLayout.Direction.LeftToRight
        )
        self.provider_row.setDirection(
            QBoxLayout.Direction.TopToBottom if provider_compact else QBoxLayout.Direction.LeftToRight
        )
        self.quick_button_row.setDirection(
            QBoxLayout.Direction.TopToBottom if quick_compact else QBoxLayout.Direction.LeftToRight
        )
        self.middle_row.setDirection(
            QBoxLayout.Direction.TopToBottom if middle_compact else QBoxLayout.Direction.LeftToRight
        )
        self.footer_layout.setDirection(
            QBoxLayout.Direction.TopToBottom if footer_compact else QBoxLayout.Direction.LeftToRight
        )

        if header_compact:
            self.header_row.setAlignment(self.status_pill, Qt.AlignmentFlag.AlignLeft)
        else:
            self.header_row.setAlignment(self.status_pill, Qt.AlignmentFlag.AlignTop)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_responsive_layouts()

    def set_startup_enabled(self, enabled):
        self.startup_checkbox.blockSignals(True)
        self.startup_checkbox.setChecked(enabled)
        self.startup_checkbox.blockSignals(False)

        if enabled:
            self.startup_hint.setText(
                "Grammar Fix will launch automatically the next time Windows starts."
            )
        else:
            self.startup_hint.setText(
                "Grammar Fix will stay off until you launch it yourself."
            )

    def on_provider_selected(self, provider, checked):
        if checked:
            self.provider_changed.emit(provider)

    def on_provider_model_changed(self, provider, model):
        if model:
            self.provider_model_changed.emit(provider, model)

    def set_selected_provider(self, provider):
        selected = provider if provider in {"groq", "google"} else "groq"
        self.groq_radio.blockSignals(True)
        self.google_radio.blockSignals(True)
        self.groq_radio.setChecked(selected == "groq")
        self.google_radio.setChecked(selected == "google")
        self.groq_radio.blockSignals(False)
        self.google_radio.blockSignals(False)

        if selected == "google":
            self.provider_hint_label.setText(
                "Google Gemini will handle grammar, translation, code explanation, and smart text help."
            )
            self.groq_model_combo.setEnabled(False)
            self.google_model_combo.setEnabled(True)
        else:
            self.provider_hint_label.setText(
                "Groq will handle grammar, translation, code explanation, and smart text help."
            )
            self.groq_model_combo.setEnabled(True)
            self.google_model_combo.setEnabled(False)

    def set_model_options(self, provider, models, selected_model):
        combo = self.google_model_combo if provider == "google" else self.groq_model_combo
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(models)
        if selected_model in models:
            combo.setCurrentText(selected_model)
        elif models:
            combo.setCurrentIndex(0)
        combo.blockSignals(False)

    def set_status(self, title, message, tone="info"):
        palette = {
            "info": (title, "#0b4a6f", "#e0f2fe"),
            "success": (title, "#0a7b68", "#e8fff8"),
            "warning": (title, "#8a5a10", "#fff3d6"),
        }
        pill_text, bg_color, fg_color = palette.get(tone, palette["info"])
        self.status_pill.setText(pill_text)
        self.status_pill.setStyleSheet(
            "background-color: {bg}; color: {fg}; border-radius: 14px; padding: 7px 14px; font-size: 12px; font-weight: 700;".format(
                bg=bg_color,
                fg=fg_color,
            )
        )
        self.message_label.setText(message)

    def present(self):
        if not self.isVisible():
            self.setWindowState(Qt.WindowState.WindowNoState)
            self.showNormal()

        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos) or QApplication.primaryScreen()
        if screen is not None and not self.isMaximized():
            geometry = screen.availableGeometry()
            x = geometry.left() + (geometry.width() - self.width()) // 2
            y = geometry.top() + (geometry.height() - self.height()) // 2
            self.move(x, y)

        self.show()
        self.raise_()
        self.activateWindow()

    def hide_to_tray(self):
        self.hide()
        self.hide_requested.emit()

    def closeEvent(self, event: QCloseEvent):
        event.ignore()
        self.hide_to_tray()
