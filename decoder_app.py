import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QTextEdit, QGroupBox)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor

# Import your decoder module
import decoder

class DecoderThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self, config_file, sniff_filter, timeout):
        QThread.__init__(self)
        self.config_file = config_file
        self.sniff_filter = sniff_filter
        self.timeout = timeout

    def run(self):
        def packet_callback(message):
            self.message_received.emit(message)

        decoder.start_decoder(
            config_file=self.config_file,
            sniff_filter=self.sniff_filter,
            timeout=self.timeout,
            callback=packet_callback
        )

class PacketDecoderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Packet Decoder")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Configuration Group
        config_group = QGroupBox("Decoder Configuration")
        config_layout = QVBoxLayout(config_group)

        self.config_file_input = QLineEdit('config.txt')
        config_layout.addWidget(QLabel("Config File:"))
        config_layout.addWidget(self.config_file_input)

        self.sniff_filter_input = QLineEdit()
        config_layout.addWidget(QLabel("Sniff Filter (optional):"))
        config_layout.addWidget(self.sniff_filter_input)

        self.timeout_input = QLineEdit()
        config_layout.addWidget(QLabel("Timeout (optional):"))
        config_layout.addWidget(self.timeout_input)

        main_layout.addWidget(config_group)

        # Control Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Decoding")
        self.start_button.clicked.connect(self.start_decoding)
        self.stop_button = QPushButton("Stop Decoding")
        self.stop_button.clicked.connect(self.stop_decoding)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        main_layout.addLayout(button_layout)

        # Message Display
        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        main_layout.addWidget(QLabel("Decoded Messages:"))
        main_layout.addWidget(self.message_display)

        # Status Label
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)

        self.decoder_thread = None
        self.accumulated_message = ""

    def start_decoding(self):
        config_file = self.config_file_input.text()
        sniff_filter = self.sniff_filter_input.text() or None
        timeout = self.timeout_input.text()
        timeout = int(timeout) if timeout else None

        self.message_display.clear()
        self.accumulated_message = ""
        self.status_label.setText("Decoding started...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.decoder_thread = DecoderThread(config_file, sniff_filter, timeout)
        self.decoder_thread.message_received.connect(self.update_message_display)
        self.decoder_thread.finished.connect(self.decoding_finished)
        self.decoder_thread.start()

    def stop_decoding(self):
        if self.decoder_thread and self.decoder_thread.isRunning():
            self.decoder_thread.terminate()
            self.decoder_thread.wait()
            self.decoding_finished()

    def update_message_display(self, message):
        self.accumulated_message += message
        self.message_display.setText(self.accumulated_message)
        # Ensure the latest text is visible
        self.message_display.moveCursor(QTextCursor.End)

    def decoding_finished(self):
        self.status_label.setText("Decoding stopped")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PacketDecoderApp()
    window.show()
    sys.exit(app.exec_())