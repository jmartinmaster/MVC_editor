from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QStatusBar
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import pyqtSignal, Qt

class EditorView(QMainWindow):
    """
    View representing the user interface of the editor.
    Implements high-fidelity CSS styling for a dark-mode theme.
    """
    open_triggered = pyqtSignal()
    save_triggered = pyqtSignal(str)
    text_user_edited = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MVC Editor")
        self.resize(900, 650)
        self.init_ui()

    def init_ui(self):
        # Global dark-theme stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QWidget {
                color: #cdd6f4;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            }
            QTextEdit {
                background-color: #181825;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', 'Fira Code', 'Courier New', monospace;
                font-size: 14px;
                selection-background-color: #45475a;
                selection-color: #f5c2e7;
            }
            QTextEdit:focus {
                border: 1.5px solid #cba6f7;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
            QLabel {
                font-size: 13px;
                color: #a6adc8;
            }
            QStatusBar {
                background-color: #11111b;
                color: #a6adc8;
                border-top: 1px solid #313244;
            }
        """)

        # Main Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main Layout
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(20, 20, 20, 15)
        layout.setSpacing(12)

        # Header Row
        header_layout = QHBoxLayout()
        self.header_label = QLabel("Welcome to MVC Editor - Start typing or open a file")
        self.header_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.header_label.setStyleSheet("color: #f5c2e7;")
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Main Text Editor Area
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Write your code or text here...")
        self.text_edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.text_edit)

        # Bottom Button Row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.open_button = QPushButton("Open File")
        self.open_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_button.clicked.connect(self.open_triggered.emit)
        
        self.save_button = QPushButton("Save File")
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.clicked.connect(self._on_save_clicked)
        
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _on_text_changed(self):
        # Notify the controller about user's edit
        self.text_user_edited.emit(self.text_edit.toPlainText())

    def _on_save_clicked(self):
        self.save_triggered.emit(self.text_edit.toPlainText())

    def set_content(self, text: str):
        # Block signals temporarily to prevent circular updates
        self.text_edit.blockSignals(True)
        self.text_edit.setPlainText(text)
        self.text_edit.blockSignals(False)

    def set_file_path(self, path: str):
        self.header_label.setText(f"Editing: {path}")
        self.status_bar.showMessage(f"Path updated to: {path}")

    def show_message(self, message: str):
        self.status_bar.showMessage(message, 4000)
