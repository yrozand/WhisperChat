import socket
import threading
import random

clients = {}
used_names = set()  # Pour suivre les noms déjà attribués

phonetic_alphabet = [
    'Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliet',
    'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa', 'Quebec', 'Romeo', 'Sierra', 'Tango',
    'Uniform', 'Victor', 'Whiskey', 'X-ray', 'Yankee', 'Zulu'
]

def assign_unique_name():
    """Assigner un nom unique à partir de l'Alphabet Phonétique International."""
    available_names = list(set(phonetic_alphabet) - used_names)
    if available_names:
        name = random.choice(available_names)
        used_names.add(name)  # Marquer le nom comme utilisé
        return name
    else:
        return "Utilisateur"  # En cas de panne de noms (improbable)

def broadcast(message, sender_socket=None):
    """Diffuser un message à tous les clients, sauf éventuellement l'expéditeur."""
    for client in clients.values():
        if client != sender_socket:
            try:
                client.send(message)
            except:
                remove_client(client)

def handle_client(client_socket, addr):
    """Gérer la communication avec un client."""
    try:
        # Assigner un nom unique au client
        client_name = assign_unique_name()
        clients[client_name] = client_socket  # Associer le nom au socket du client

        # Envoyer un message de bienvenue
        welcome_message = f"Bienvenue, {client_name} ! Tapez 'exit()' pour quitter."
        client_socket.send(welcome_message.encode('utf-8'))

        # Informer les autres clients qu'un nouveau participant a rejoint
        join_message = f"{client_name} a rejoint le chat !".encode('utf-8')
        broadcast(join_message, client_socket)

        # Gérer les messages reçus du client
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                
                # Vérifier si le client a tapé 'exit()' pour se déconnecter
                if message.strip().lower() == 'exit()':
                    break  # Quitter la boucle pour déconnecter le client
                
                # Diffuser le message à tous les autres clients avec le nom du client
                full_message = f"{client_name}: {message}".encode('utf-8')
                broadcast(full_message, client_socket)
            except:
                break  # En cas d'erreur, quitter la boucle
    finally:
        # Informer les autres clients que le participant a quitté
        leave_message = f"{client_name} a quitté le chat.".encode('utf-8')
        broadcast(leave_message)

        # Fermer la connexion et retirer le client
        remove_client(client_socket, client_name)

def remove_client(client_socket, client_name):
    """Enlever un client de la liste et fermer sa connexion."""
    if client_name in clients:
        del clients[client_name]  # Supprimer le client du dictionnaire
        used_names.discard(client_name)  # Libérer le nom pour qu'il puisse être réutilisé
        client_socket.close()  # Fermer la connexion du client

def start_server():
    """Démarrer le serveur et accepter les connexions des clients."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 6969))  # Remplacer par l'adresse IP et le port de ton serveur
    server_socket.listen()

    print("Le serveur est démarré, en attente de connexions...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Client connecté depuis {addr}")

        # Lancer un thread pour gérer ce client
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
