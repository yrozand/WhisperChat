import sys
import socket
import threading
import logging
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QDialog, QMessageBox, QHBoxLayout, QComboBox, QSystemTrayIcon, QMenu, QFileDialog, QMainWindow, QListWidget, QSplitter, QListWidgetItem, QTabWidget
from PyQt5.QtGui import QIcon, QColor, QDesktopServices
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, Qt, QUrl
import re

# Configuration du logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConnectDialog(QDialog):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setWindowTitle("Connect to Server")
        self.setGeometry(200, 200, 300, 200)
        self.setWindowIcon(QIcon('discord.ico'))  # Set custom icon
        layout = QVBoxLayout()

        self.server_ip_label = QLabel("Server IP:", self)
        self.server_ip_input = QLineEdit(self)
        self.server_ip_input.setPlaceholderText("Enter server IP")

        self.server_port_label = QLabel("Server Port:", self)
        self.server_port_input = QLineEdit(self)
        self.server_port_input.setPlaceholderText("Enter server port")

        self.username_label = QLabel("Username:", self)
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Enter username")

        self.connect_button = QPushButton("Connect", self)
        self.connect_button.clicked.connect(self.connect_to_server)

        layout.addWidget(self.server_ip_label)
        layout.addWidget(self.server_ip_input)
        layout.addWidget(self.server_port_label)
        layout.addWidget(self.server_port_input)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)
        self.apply_dark_theme()

    def connect_to_server(self):
        server_ip = self.server_ip_input.text()
        server_port = self.server_port_input.text()
        username = self.username_input.text()
        if self.client:
            success = self.client.connect_to_server(server_ip, server_port, username)
            if success:
                self.accept()
            else:
                QMessageBox.critical(self, "Connection Error", "Failed to connect to the server. Please check the IP, port, and username.")

    def apply_dark_theme(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #2C2F33;
            color: #FFFFFF;
        }
        QLineEdit, QTextEdit {
            background-color: #23272A;
            color: #FFFFFF;
        }
        QPushButton {
            background-color: #7289DA;
            color: #FFFFFF;
        }
        QLabel {
            color: #FFFFFF;
        }
        """)

class FreyaTalkClient(QMainWindow):
    message_received = pyqtSignal(str)
    user_list_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.username = "User"
        self.server_ip = None
        self.is_dark_theme = False
        self.history_file = "chat_history.txt"
        self.private_windows = {}
        self.assigned_name = None
        self.initUI()
        self.message_received.connect(self.log_message)
        self.user_list_updated.connect(self.update_user_list)

    def initUI(self):
        self.setWindowTitle("FreyaTalk Chat")
        self.setGeometry(200, 200, 1280, 720)
        self.setWindowIcon(QIcon('discord.png'))  # Set custom icon

        # Main layout
        main_layout = QVBoxLayout()

        # Splitter for sidebar and chat area
        splitter = QSplitter(Qt.Horizontal)

        # Sidebar for user list
        self.user_list = QListWidget()
        self.user_list.setFixedWidth(200)
        self.user_list.itemClicked.connect(self.open_private_message_tab)
        splitter.addWidget(self.user_list)

        # Tab widget for chat areas
        self.chat_tabs = QTabWidget()
        splitter.addWidget(self.chat_tabs)

        # Main chat tab
        self.main_chat_tab = QWidget()
        self.main_chat_layout = QVBoxLayout(self.main_chat_tab)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.main_chat_layout.addWidget(self.chat_display)

        # Message input and send button layout
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon("paper-plane.png"))
        self.send_button.setFixedSize(50, 50)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        self.main_chat_layout.addLayout(input_layout)

        # Settings, Donation, and Quit buttons layout
        buttons_layout = QHBoxLayout()

        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon("settings-sliders.png"))
        self.settings_button.setFixedSize(50, 50)
        buttons_layout.addWidget(self.settings_button)

        self.donation_button = QPushButton()
        self.donation_button.setIcon(QIcon("donate.png"))
        self.donation_button.setFixedSize(50, 50)
        self.donation_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://ko-fi.com/yrozand")))
        buttons_layout.addWidget(self.donation_button)

        self.quit_button = QPushButton()
        self.quit_button.setIcon(QIcon("power.png"))
        self.quit_button.setFixedSize(50, 50)
        self.quit_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.quit_button)

        self.main_chat_layout.addLayout(buttons_layout)

        self.chat_tabs.addTab(self.main_chat_tab, "Main Chat")

        main_layout.addWidget(splitter)

        # Set main layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Apply dark theme
        self.apply_dark_theme()

        # Initialize system tray icon
        self.tray_icon = QSystemTrayIcon(QIcon('discord.png'), self)
        tray_menu = QMenu()
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def apply_dark_theme(self):
        dark_stylesheet = """
        QWidget {
            background-color: #2C2F33;
            color: #FFFFFF;
        }
        QLineEdit, QTextEdit {
            background-color: #23272A;
            color: #FFFFFF;
        }
        QPushButton {
            background-color: #7289DA;
            color: #FFFFFF;
        }
        QListWidget {
            background-color: #2C2F33;
            color: #FFFFFF;
        }
        QTabBar::tab {
            background: #2C2F33;
            color: #FFFFFF;
        }
        QTabBar::tab:selected {
            background: #23272A;
            color: #FFFFFF;
        }
        QTabBar::tab[private-message] {
            color: #000000;  /* Set text color to black for private message tabs */
        }
        """
        self.setStyleSheet(dark_stylesheet)

    def send_message(self):
        message = self.message_input.text()
        if message:
            self.chat_display.append(f"{self.username}: {message}")
            self.client_socket.send(message.encode('utf-8'))
            self.message_input.clear()

    def log_message(self, message):
        if message.startswith("PRIVATE:"):
            _, sender, private_message = message.split(":", 2)
            if sender not in self.private_windows:
                self.private_windows[sender] = self.create_private_message_tab(sender)
            self.private_windows[sender].append(f"{sender}: {private_message}")
        elif message.startswith("ASSIGNED_NAME:"):
            self.assigned_name = message.split(":", 1)[1]
        else:
            self.chat_display.append(message)

    def update_user_list(self, users):
        self.user_list.clear()
        for user in users:
            if user != self.assigned_name:
                item = QListWidgetItem(user)
                self.user_list.addItem(item)

    def create_private_message_tab(self, recipient):
        private_tab = QWidget()
        private_tab.setObjectName("private-message")  # Set object name for stylesheet
        private_layout = QVBoxLayout(private_tab)

        private_display = QTextEdit()
        private_display.setReadOnly(True)
        private_layout.addWidget(private_display)

        private_input = QLineEdit()
        private_input.setPlaceholderText("Type your message here...")
        private_input.returnPressed.connect(lambda: self.send_private_message(recipient, private_input, private_display))
        private_layout.addWidget(private_input)

        private_send_button = QPushButton("Send")
        private_send_button.clicked.connect(lambda: self.send_private_message(recipient, private_input, private_display))
        private_layout.addWidget(private_send_button)

        index = self.chat_tabs.addTab(private_tab, recipient)
        self.chat_tabs.tabBar().setTabData(index, "private-message")  # Set tab data for stylesheet
        return private_display

    def send_private_message(self, recipient, input_field, display_field):
        message = input_field.text()
        if message:
            self.client_socket.send(f"PRIVATE:{recipient}:{message}".encode('utf-8'))
            display_field.append(f"You: {message}")
            input_field.clear()

    def open_private_message_tab(self, item):
        recipient = item.text()
        if recipient not in self.private_windows:
            self.private_windows[recipient] = self.create_private_message_tab(recipient)
        self.chat_tabs.setCurrentWidget(self.private_windows[recipient].parentWidget())

    def connect_to_server(self, server_ip, server_port, username):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_ip, int(server_port)))
            self.client_socket.send(username.encode('utf-8'))
            self.username = username
            logging.info(f"Connected to server at {server_ip}:{server_port}")

            # Start a thread to listen for messages from the server
            threading.Thread(target=self.listen_for_messages, daemon=True).start()
            return True
        except Exception as e:
            logging.error(f"Error connecting to server: {e}")
            return False

    def listen_for_messages(self):
        try:
            while True:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message.startswith("USER_LIST:"):
                    users = message[len("USER_LIST:"):].split(",")
                    self.user_list_updated.emit(users)
                else:
                    self.message_received.emit(message)
        except Exception as e:
            logging.error(f"Error receiving message: {e}")

    def disconnect(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        self.hide()
        connection_window = ConnectDialog(self)
        if connection_window.exec_() == QDialog.Accepted:
            self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = FreyaTalkClient()
    dialog = ConnectDialog(client)
    if dialog.exec_() == QDialog.Accepted:
        client.show()
    sys.exit(app.exec_())