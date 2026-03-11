import sys
import asyncio
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agency.apollo_core import ApolloCore

class ApolloWorker(QObject):
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.core = ApolloCore()

    def process_text(self, text):
        """
        Runs the async process_command using asyncio.run().
        """
        if text.strip():
            try:
                asyncio.run(self.core.process_command(text))
            except Exception as e:
                print(f"Worker Error: {e}")
        self.finished.emit()

class CommandBar(QWidget):
    command_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.worker = ApolloWorker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()
        
        # Connect signals
        self.command_signal.connect(self.worker.process_text)
        self.worker.finished.connect(self.on_processing_finished)

        # Auto-submit Timer
        self.typing_timer = QTimer()
        self.typing_timer.setSingleShot(True)
        self.typing_timer.timeout.connect(self.handle_enter)
        self.input_field.textChanged.connect(self.reset_typing_timer)

    def reset_typing_timer(self):
        if self.input_field.text().strip():
            self.typing_timer.start(2000) # 2.0 seconds delay
        else:
            self.typing_timer.stop()

    def initUI(self):
        # Window Flags
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Geometry (Top Center)
        screen = QApplication.primaryScreen().geometry()
        width = 800
        height = 60
        self.setGeometry((screen.width() - width) // 2, 50, width, height)

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Input Field
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Listening to Windows Dictation (Win+H)...")
        self.input_field.setFont(QFont("Consolas", 14))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(20, 20, 20, 240);
                color: #00FF00;
                border: 2px solid #333;
                border-radius: 10px;
                padding: 10px;
                selection-background-color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #00FF00;
            }
        """)
        self.input_field.returnPressed.connect(self.handle_enter)
        
        layout.addWidget(self.input_field)

    def handle_enter(self):
        text = self.input_field.text()
        if text:
            self.input_field.clear()
            self.input_field.setPlaceholderText("Processing...")
            self.input_field.setDisabled(True)
            self.command_signal.emit(text)

    def on_processing_finished(self):
        self.input_field.setDisabled(False)
        self.input_field.setPlaceholderText("Listening to Windows Dictation (Win+H)...")
        self.input_field.setFocus()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = event.globalPos() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    bar = CommandBar()
    bar.show()
    sys.exit(app.exec_())
