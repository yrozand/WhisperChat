import socket
import threading

# Configuration du serveur
IP = '0.0.0.0'  # Adresse IP du serveur (0.0.0.0 pour accepter toutes les connexions)
PORT = 9001  # Port d'écoute du serveur
SERVER_ADDRESS = (IP, PORT)

# Initialisation du socket serveur
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(SERVER_ADDRESS)
server_socket.listen()

# Liste des clients connectés
clients = []

# Fonction de gestion des connexions clients
def handle_client_connection(client_socket, client_address):
    print(f"Nouvelle connexion : {client_address}")
    client_name = client_socket.recv(1024).decode()  # Récupération du nom du client
    clients.append((client_socket, client_name))

    while True:
        try:
            message = client_socket.recv(1024).decode()  # Récupération du message envoyé par le client
            if not message:
                break

            # Envoi du message à tous les autres clients
            for client in clients:
                if client[0] != client_socket:
                    client[0].send(f"{client_name}: {message}".encode())

        except ConnectionResetError:
            break

    # Suppression du client de la liste des clients connectés
    clients.remove((client_socket, client_name))
    print(f"Déconnexion : {client_address}")

# Boucle d'attente de nouvelles connexions clients
print(f"Serveur en attente de connexions sur {IP}:{PORT}")
while True:
    client_socket, client_address = server_socket.accept()
    client_socket.send("Bienvenue sur FreyaTalk !".encode())
    client_socket.send("".encode())
    client_socket.send("".encode())
    client_socket.send("Vous pouvez discuté ici tranquilement.".encode())

    # Création d'un thread pour gérer la connexion client
    client_thread = threading.Thread(target=handle_client_connection, args=(client_socket, client_address))
    client_thread.start()