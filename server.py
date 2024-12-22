import socket
import threading
import random
import logging
from logging.handlers import RotatingFileHandler
import shutil
import os
from datetime import datetime

# Configuration du logger avec rotation des fichiers de log
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Générer un timestamp pour le nom du fichier de log
timestamp = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
log_file = os.path.join(log_dir, f"server_{timestamp}.log")

handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=3, encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    handler,
    logging.StreamHandler()
])

clients = {}
used_names = set()

phonetic_alphabet = [
    'Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliet',
    'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa', 'Quebec', 'Romeo', 'Sierra', 'Tango',
    'Uniform', 'Victor', 'Whiskey', 'X-ray', 'Yankee', 'Zulu'
]

def assign_unique_name():
    available_names = list(set(phonetic_alphabet) - used_names)
    if available_names:
        name = random.choice(available_names)
        used_names.add(name)
        return name
    else:
        return "Utilisateur"

def broadcast(message, sender_socket=None):
    for client_socket in clients.values():
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode('utf-8'))
            except Exception as e:
                logging.error(f"Error sending message to a client: {e}")

def send_private_message(sender_name, recipient_name, message):
    if recipient_name in clients:
        try:
            clients[recipient_name].send(f"PRIVATE:{sender_name}:{message}".encode('utf-8'))
        except Exception as e:
            logging.error(f"Error sending private message to {recipient_name}: {e}")

def broadcast_user_list():
    user_list = ",".join(clients.keys())
    broadcast(f"USER_LIST:{user_list}")

def handle_client(client_socket, client_name):
    try:
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                if message.startswith("PRIVATE:"):
                    _, recipient_name, private_message = message.split(":", 2)
                    send_private_message(client_name, recipient_name, private_message)
                else:
                    full_message = f"{client_name}: {message}"
                    broadcast(full_message, client_socket)
            except Exception as e:
                logging.error(f"Error receiving message from {client_name}: {e}")
                break
    finally:
        leave_message = f"{client_name} a quitté le chat."
        broadcast(leave_message)
        remove_client(client_socket, client_name)

def remove_client(client_socket, client_name):
    if client_name in clients:
        del clients[client_name]
        used_names.discard(client_name)
        client_socket.close()
        logging.info(f"Client {client_name} has been removed.")
        broadcast_user_list()

def archive_old_logs():
    log_files = sorted([f for f in os.listdir(log_dir) if f.startswith("server_") and f.endswith(".log")], key=lambda x: os.path.getmtime(os.path.join(log_dir, x)))
    if len(log_files) > 3:
        oldest_log = log_files[0]
        archive_dir = os.path.join(log_dir, "archive")
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
        shutil.move(os.path.join(log_dir, oldest_log), os.path.join(archive_dir, oldest_log))

def start_server():
    archive_old_logs()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 6969))
    server_socket.listen()
    logging.info("Le serveur est démarré, en attente de connexions...")

    while True:
        try:
            client_socket, addr = server_socket.accept()
            logging.info(f"Connexion acceptée de {addr}")

            client_name = assign_unique_name()
            clients[client_name] = client_socket
            logging.info(f"Client {client_name} connected from {addr}")

            welcome_message = f"{client_name} a rejoint le chat."
            broadcast(welcome_message)
            broadcast_user_list()

            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_name))
            client_thread.start()
        except Exception as e:
            logging.error(f"Error accepting connection: {e}")

if __name__ == "__main__":
    start_server()