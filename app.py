import sys
import ipaddress
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QTextEdit, QGroupBox, 
                             QCheckBox, QSpinBox, QMessageBox)
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QRect, QTimer, QDateTime
import matplotlib.pyplot as plt
from scapy.all import sniff, IP, TCP
from collections import defaultdict, deque
import threading
import datetime
import network_noise_generator  # Import the noise generation module

# Import your backend modules
import encoder
import decoder
import stego_utils

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

        # Noise Generation Checkbox
        self.noise_checkbox = QCheckBox("Enable Network Noise")
        self.noise_checkbox.stateChanged.connect(self.toggle_network_noise)
        left_panel.addWidget(self.noise_checkbox)

        # Send Button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        left_panel.addWidget(self.send_button)

        # Start/Stop Graph Button
        self.start_graph_button = QPushButton("Start Monitoring Packets")
        self.start_graph_button.clicked.connect(self.start_packet_monitoring)
        left_panel.addWidget(self.start_graph_button)

        # Stop Monitoring Button
        self.stop_graph_button = QPushButton("Stop Monitoring")
        self.stop_graph_button.clicked.connect(self.stop_packet_monitoring)
        self.stop_graph_button.setEnabled(False)
        left_panel.addWidget(self.stop_graph_button)

        # Status Area
        self.status_label = QLabel("Ready")
        left_panel.addWidget(self.status_label)

        # Packet Visualization
        self.visualization = PacketVisualization()
        right_panel.addWidget(self.visualization)

        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)

        self.packet_times = deque()
        self.monitoring = False
        self.monitor_thread = None
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.plot_packet_counts_over_time)

    def toggle_network_noise(self):
        """Start network noise generation when the checkbox is checked."""
        destination_ip = self.ip_input.text()
        destination_port = int(self.port_input.text())

        if self.noise_checkbox.isChecked():
            # Start generating noise when the checkbox is checked
            network_noise_generator.start_noise(destination_ip, destination_port)
            self.status_label.setText("Network noise generation started.")
            print(f"Network noise generation started for {destination_ip}:{destination_port}")
        else:
            self.status_label.setText("Network noise checkbox unchecked.")

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

            print(f"Encoding message: {message}")
            print(f"Using headers: {selected_headers}")
            print(f"Sending to: {destination_ip}:{destination_port}")
            stego_utils.save_to_config(destination_ip, destination_port, selected_headers)
            encoder.start_encoder(
                load_config=True,
                use_noise=True,
                messages=[message]
            )

            self.status_label.setText("Message sent successfully!")
            QMessageBox.information(self, "Success", "Message encoded and sent successfully!")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def packet_callback(self, packet):
        """Packet callback function to record timestamps of incoming packets."""
        if IP in packet and TCP in packet:
            timestamp = datetime.datetime.now()
            self.packet_times.append(timestamp)

    def start_packet_monitoring(self):
        """Start monitoring packets and updating the graph."""
        if not self.monitoring:
            self.monitoring = True
            self.packet_times.clear()
            self.status_label.setText("Monitoring packets...")
            self.start_graph_button.setEnabled(False)
            self.stop_graph_button.setEnabled(True)

            # Start the sniffing in a background thread
            self.monitor_thread = threading.Thread(target=self.sniff_packets)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()

            # Start updating the graph every 0.5 seconds
            self.update_timer.start(500)

    def stop_packet_monitoring(self):
        """Stop monitoring packets and updating the graph."""
        if self.monitoring:
            self.monitoring = False
            self.status_label.setText("Monitoring stopped.")
            self.start_graph_button.setEnabled(True)
            self.stop_graph_button.setEnabled(False)
            self.update_timer.stop()

    def sniff_packets(self):
        """Sniff packets in the background."""
        sniff(prn=self.packet_callback, filter="tcp and dst host 192.168.1.100 and dst port 80", stop_filter=lambda x: not self.monitoring)

    def plot_packet_counts_over_time(self):
        """Plot packet counts over time using matplotlib."""
        # Ensure there is always at least one point on the graph
        current_time = datetime.datetime.now().replace(microsecond=0)
        if not self.packet_times:
            self.packet_times.append(current_time)

        # Group packet times by second
        time_bins = defaultdict(int)
        for time in self.packet_times:
            rounded_time = time.replace(microsecond=0)
            time_bins[rounded_time] += 1

        # Fill in any gaps with zero counts
        start_time = min(time_bins.keys())
        end_time = current_time
        full_time_range = [start_time + datetime.timedelta(seconds=i) for i in range((end_time - start_time).seconds + 1)]
        counts = [time_bins.get(time, 0) for time in full_time_range]

        self.show_graph_over_time(full_time_range, counts)

    def show_graph_over_time(self, times, counts):
        """Display the graph of packet counts over time using matplotlib."""
        plt.gcf().clear()  # Clears the current figure instead of creating a new one
        plt.plot(times, counts, marker='o', linestyle='-', color='blue')
        plt.xlabel('Time')
        plt.ylabel('Number of Packets')
        plt.title('Number of Packets Over Time')
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.grid(True)
        plt.pause(0.001)  # Allow for dynamic updates in real-time


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SteganographyApp()
    window.show()
    plt.ion()  # Turn on interactive mode for real-time plotting
    sys.exit(app.exec_())
