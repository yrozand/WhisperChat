import argparse
import socket
import threading
import logging
import os
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
                logging.error(f"Error sending message to a client: {e}")

def send_private_message(sender_name, recipient_name, message):
    for client_socket, client_name in clients.items():
        if client_name == recipient_name:
            try:
                client_socket.send(f"PRIVATE:{sender_name}:{message}".encode('utf-8'))
                return True
            except Exception as e:
                logging.error(f"Error sending private message to {recipient_name}: {e}")
                return False
    return False

def handle_client(client_socket, addr):
    try:
        username = client_socket.recv(1024).decode('utf-8')
        if username in clients.values():
            client_socket.send("USERNAME_TAKEN".encode('utf-8'))
            client_socket.close()
            return
        clients[client_socket] = username
        logging.info(f"{username} connected from {addr}")

        welcome_message = f"{username} a rejoint le chat."
        broadcast(welcome_message, client_socket)
        broadcast_user_list()

        # Send the user list to the newly connected client
        user_list = ",".join(clients.values())
        client_socket.send(f"USER_LIST:{user_list}".encode('utf-8'))

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            logging.info(f"Received message from {username}: {message}")
            broadcast(f"{username}: {message}", client_socket)
    except Exception as e:
        logging.error(f"Error handling client {addr}: {e}")
    finally:
        if client_socket in clients:
            del clients[client_socket]
        client_socket.close()
        logging.info(f"{username} disconnected")
        broadcast(f"{username} a quitté le chat.")
        broadcast_user_list()

def broadcast_user_list():
    user_list = ",".join(clients.values())
    broadcast(f"USER_LIST:{user_list}")

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
    parser.add_argument('--port', type=int, default=12345, help='Port to run the server on')
    args = parser.parse_args()
    start_server(args.port)