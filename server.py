import argparse
import logging
import os
import socket
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create log directory if it doesn't exist
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Generate a timestamp for the log file name
timestamp = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
log_file = os.path.join(log_dir, f"server_{timestamp}.log")

handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=3, encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    handler,
    logging.StreamHandler()
])

clients = {}

def broadcast(message, sender_socket=None):
    for client_socket in clients.keys():
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode('utf-8'))
            except Exception as e:
                logging.error(f"Error broadcasting message: {e}")

def send_private_message(sender_name, recipient_name, message):
    for client_socket, client_name in clients.items():
        if client_name == recipient_name:
            try:
                client_socket.send(f"Private message from {sender_name}: {message}".encode('utf-8'))
                return True
            except Exception as e:
                logging.error(f"Error sending private message: {e}")
                return False
    return False

def handle_client(client_socket, addr):
    logging.info(f"New connection from {addr}")
    try:
        username = client_socket.recv(1024).decode('utf-8')
        clients[client_socket] = username
        broadcast_user_list()
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message.startswith("/pm"):
                parts = message.split(" ", 2)
                if len(parts) == 3:
                    recipient_name = parts[1]
                    private_message = parts[2]
                    if not send_private_message(clients[client_socket], recipient_name, private_message):
                        client_socket.send(f"User {recipient_name} not found.".encode('utf-8'))
            else:
                broadcast(f"{clients[client_socket]}: {message}", client_socket)
    except Exception as e:
        logging.error(f"Error handling client {addr}: {e}")
    finally:
        logging.info(f"Connection closed for {addr}")
        clients.pop(client_socket, None)
        client_socket.close()
        broadcast_user_list()

def broadcast_user_list():
    user_list = "listmembre " + " ".join(clients.values())
    broadcast(user_list)

def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    logging.info(f"Server started on port {port}")

    while True:
        try:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.start()
        except Exception as e:
            logging.error(f"Error accepting connection: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FreyaTalk Server")
    parser.add_argument('--port', type=int, default=6969, help='Port to run the server on')
    args = parser.parse_args()
    start_server(args.port)