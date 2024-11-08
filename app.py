import sys
import ipaddress
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QTextEdit, QGroupBox, 
                             QCheckBox, QSpinBox, QMessageBox)
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QRect

# Import your backend modules
import encoder
import decoder
import evaluate

class PacketVisualization(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_headers = {}
        self.setMinimumSize(400, 200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw packet outline
        painter.setPen(Qt.black)
        painter.drawRect(10, 10, self.width() - 20, self.height() - 20)

        # Draw header fields
        total_height = self.height() - 40
        y = 20
        for header, bits in self.selected_headers.items():
            if bits > 0:
                height = int((bits / 320) * total_height)  # Normalize to max 320 bits
                rect = QRect(20, y, self.width() - 40, height)
                painter.fillRect(rect, QColor(100, 200, 100, 100))
                painter.drawRect(rect)
                painter.drawText(rect, Qt.AlignCenter, f"{header}\n{bits} bits")
                y += height + 5

    def update_headers(self, headers):
        self.selected_headers = headers
        self.update()

class SteganographyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steganography System")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = QVBoxLayout()
        right_panel = QVBoxLayout()

        # Header Field Selection
        header_group = QGroupBox("Header Field Selection")
        header_layout = QVBoxLayout(header_group)
        self.header_checkboxes = {}
        self.header_spinboxes = {}
        headers = {
            'ipid': 16, 'ttl': 8, 'window': 16, 'tcp_reserved': 4,
            'tcp_options': 320, 'ip_options': 320, 'user_agent': 8
        }
        for header, max_bits in headers.items():
            row = QHBoxLayout()
            checkbox = QCheckBox(header)
            spinbox = QSpinBox()
            spinbox.setRange(0, max_bits)
            spinbox.setSingleStep(8)
            spinbox.setEnabled(False)
            checkbox.stateChanged.connect(lambda state, sb=spinbox: sb.setEnabled(state == Qt.Checked))
            checkbox.stateChanged.connect(self.update_visualization)
            spinbox.valueChanged.connect(self.update_visualization)
            row.addWidget(checkbox)
            row.addWidget(spinbox)
            header_layout.addLayout(row)
            self.header_checkboxes[header] = checkbox
            self.header_spinboxes[header] = spinbox
        left_panel.addWidget(header_group)

        # Message Input
        message_group = QGroupBox("Message Input")
        message_layout = QVBoxLayout(message_group)
        self.message_input = QTextEdit()
        message_layout.addWidget(self.message_input)
        left_panel.addWidget(message_group)

        # Destination Settings
        dest_group = QGroupBox("Destination Settings")
        dest_layout = QVBoxLayout(dest_group)
        self.ip_input = QLineEdit('192.168.1.100')
        self.port_input = QLineEdit('80')
        dest_layout.addWidget(QLabel("Destination IP:"))
        dest_layout.addWidget(self.ip_input)
        dest_layout.addWidget(QLabel("Destination Port:"))
        dest_layout.addWidget(self.port_input)
        left_panel.addWidget(dest_group)

        # Send Button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        left_panel.addWidget(self.send_button)

        # Status Area
        self.status_label = QLabel("Ready")
        left_panel.addWidget(self.status_label)

        # Packet Visualization
        self.visualization = PacketVisualization()
        right_panel.addWidget(self.visualization)

        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)

    def update_visualization(self):
        headers = {}
        for header, checkbox in self.header_checkboxes.items():
            if checkbox.isChecked():
                headers[header] = self.header_spinboxes[header].value()
        self.visualization.update_headers(headers)
        self.validate_inputs()

    def validate_inputs(self):
        total_bits = sum(self.header_spinboxes[h].value() for h in self.header_checkboxes if self.header_checkboxes[h].isChecked())
        message = self.message_input.toPlainText()
        message_bits = len(message) * 8

        # if message_bits > total_bits+100000:
        #     self.status_label.setText(f"Warning: Message too long ({message_bits} bits) for selected headers ({total_bits} bits)")
        #     self.send_button.setEnabled(False)
        if (total_bits % 8 != 0):
            self.status_label.setText(f"Warning: Total number of bits must be a multiple of 8 ({total_bits} bits)")
            self.send_button.setEnabled(False)
        elif not self.is_valid_ip(self.ip_input.text()) or not self.is_valid_port(self.port_input.text()):
            self.status_label.setText("Invalid IP address or port")
            self.send_button.setEnabled(False)
        else:
            self.status_label.setText("Ready to send")
            self.send_button.setEnabled(True)

    def is_valid_ip(self, ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def is_valid_port(self, port):
        try:
            port_num = int(port)
            return 0 < port_num < 65536
        except ValueError:
            return False

    def send_message(self):
        try:
            message = self.message_input.toPlainText()
            destination_ip = self.ip_input.text()
            destination_port = int(self.port_input.text())

            selected_headers = []
            for header, checkbox in self.header_checkboxes.items():
                if checkbox.isChecked():
                    selected_headers.append((header, self.header_spinboxes[header].value()))

            # Here you would call your encoder function
            # For demonstration, we'll just print the values
            print(f"Encoding message: {message}")
            print(f"Using headers: {selected_headers}")
            print(f"Sending to: {destination_ip}:{destination_port}")
            evaluate.save_to_config(destination_ip, destination_port, selected_headers)
            encoder.start_encoder(
                load_config=True,
                use_noise=False,
                messages=[message]
            )

            # Simulate sending
            # In a real scenario, you would call your encoder and sending functions here
            # encoder.encode_and_send(message, selected_headers, destination_ip, destination_port)

            self.status_label.setText("Message sent successfully!")
            QMessageBox.information(self, "Success", "Message encoded and sent successfully!")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SteganographyApp()
    window.show()
    sys.exit(app.exec_())