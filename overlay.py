from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QApplication, QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

class OverlayWindow(QWidget):
    accepted = pyqtSignal(str)
    dismissed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.init_ui()
        self.original_text = ""
        self.corrected_text = ""

    def init_ui(self):
        # Main layout container with styling
        self.container = QWidget(self)
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            QWidget#container {
                background-color: #2D2D2D;
                border: 1px solid #444;
                border-radius: 10px;
            }
            QLabel {
                color: #AAAAAA;
                font-size: 12px;
            }
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QPushButton#dismiss {
                background-color: #444;
            }
            QPushButton#dismiss:hover {
                background-color: #666;
            }
        """)
        
        layout = QVBoxLayout(self.container)
        
        # Header
        self.header_label = QLabel("Grammar Fix Suggestion")
        layout.addWidget(self.header_label)
        
        # Text Display
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFixedHeight(100)
        layout.addWidget(self.text_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.accept_btn = QPushButton("Fix & Replace")
        self.accept_btn.clicked.connect(self.on_accept)
        
        self.dismiss_btn = QPushButton("Dismiss")
        self.dismiss_btn.setObjectName("dismiss")
        self.dismiss_btn.clicked.connect(self.on_dismiss)
        
        button_layout.addWidget(self.dismiss_btn)
        button_layout.addWidget(self.accept_btn)
        
        layout.addLayout(button_layout)
        
        # Main window layout to hold the container
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.resize(400, 200)

    def show_suggestion(self, original, corrected):
        self.original_text = original
        self.corrected_text = corrected
        self.text_edit.setText(corrected)
        
        # Center on screen or near mouse (for simplicity, center on screen for now)
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
        self.show()
        self.activateWindow()

    def on_accept(self):
        self.hide()
        self.accepted.emit(self.corrected_text)

    def on_dismiss(self):
        self.dismissed.emit()
        self.hide()
