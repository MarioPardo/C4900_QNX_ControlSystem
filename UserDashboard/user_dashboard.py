import sys
import json
import socket
import threading

from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, Signal

class Dashboard(QWidget):

    # signal used to safely update UI from network thread
    packet_received = Signal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("QNX Vehicle Dashboard")
        self.setGeometry(200, 200, 420, 300)

        # connect signal to UI processor
        self.packet_received.connect(self.process_packet)

        # Speed Display
        self.speed_label = QLabel("0")
        self.speed_label.setAlignment(Qt.AlignCenter)
        self.speed_label.setStyleSheet("""
            font-size: 72px;
            font-weight: bold;
            color: #38bdf8;
        """)

        self.kmh_label = QLabel("km/h")
        self.kmh_label.setAlignment(Qt.AlignCenter)
        self.kmh_label.setStyleSheet("font-size: 20px; color: #94a3b8;")

        # Warning Indicator 
        self.warning_label = QLabel("SYSTEM OK")
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setStyleSheet("""
            font-size: 18px;
            padding: 8px;
            border-radius: 8px;
            background-color: #16a34a;
            color: white;
        """)

        # Driver Input Display 
        self.input_label = QLabel("Driver Input: None")
        self.input_label.setAlignment(Qt.AlignCenter)
        self.input_label.setStyleSheet("font-size: 16px; color: #e2e8f0;")

        # Layout 
        main_layout = QVBoxLayout()
        center_layout = QHBoxLayout()

        center_layout.addStretch()
        center_layout.addWidget(self.speed_label)
        center_layout.addStretch()

        main_layout.addLayout(center_layout)
        main_layout.addWidget(self.kmh_label)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.warning_label)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.input_label)

        self.setLayout(main_layout)

        # Dark Theme 
        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                color: white;
                font-family: Arial;
            }
        """)

        # start listening to ECU
        self.start_network()

   
    # Network connection 
    def start_network(self):
        thread = threading.Thread(target=self.network_listener, daemon=True)
        thread.start()

    def network_listener(self):
        HOST = "127.0.0.1"
        PORT = 5000

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Connecting to ECU...")
        client.connect((HOST, PORT))
        print("Connected to ECU")

        buffer = ""

        while True:
            data = client.recv(1024).decode()
            buffer += data

            # messages separated by newline
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                self.packet_received.emit(line)
    # Process incoming JSON
    
    def process_packet(self, json_data):
        data = json.loads(json_data)

        # update speed
        self.speed_label.setText(str(int(data['speed'])))

        # update warning indicator
        if data["warning"]:
            self.warning_label.setText("SENSOR FAILURE")
            self.warning_label.setStyleSheet("""
                font-size: 18px;
                padding: 8px;
                border-radius: 8px;
                background-color: #dc2626;
                color: white;
            """)
        else:
            self.warning_label.setText("SYSTEM OK")
            self.warning_label.setStyleSheet("""
                font-size: 18px;
                padding: 8px;
                border-radius: 8px;
                background-color: #16a34a;
                color: white;
            """)
    # Keyboard input (driver controls)

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_W:
            self.input_label.setText("Driver Input: Accelerate")

        elif event.key() == Qt.Key_S:
            self.input_label.setText("Driver Input: Brake")

        elif event.key() == Qt.Key_A:
            self.input_label.setText("Driver Input: Steer Left")

        elif event.key() == Qt.Key_D:
            self.input_label.setText("Driver Input: Steer Right")

app = QApplication(sys.argv)
window = Dashboard()
window.show()
sys.exit(app.exec())
