import socket
import threading

def receive_messages(client_socket):
    """Recevoir et afficher les messages du serveur."""
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break  # Si le serveur ferme la connexion, sortir de la boucle
            print(message)
        except:
            # Si une erreur survient, fermer la connexion proprement
            print("Connexion perdue avec le serveur.")
            client_socket.close()
            break

def send_messages(client_socket):
    """Envoyer des messages au serveur."""
    while True:
        message = input('> ')  # L'utilisateur tape son message
        
        # Si l'utilisateur tape 'exit()', il envoie le message au serveur et ferme la connexion
        if message.strip().lower() == 'exit()':
            client_socket.send('exit()'.encode('utf-8'))  # Envoyer exit() au serveur
            print("Vous avez quitté le chat.")
            client_socket.close()  # Fermer la connexion du côté client
            break  # Quitter la boucle pour arrêter l'envoi de messages
        
        try:
            client_socket.send(message.encode('utf-8'))  # Envoyer le message au serveur
        except:
            print("Erreur lors de l'envoi du message.")
            break

def start_client():
    """Démarrer le client et se connecter au serveur."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = input("Saisir l'addresse IP du serveur: ")
    try:
        client_socket.connect((ip, 6969))  # Remplacer par l'IP et le port du serveur
        print("Connecté au serveur.")
        
        # Lancer le thread pour recevoir des messages
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        # Gérer l'envoi des messages depuis le client principal
        send_messages(client_socket)
        
    except Exception as e:
        print(f"Impossible de se connecter au serveur : {e}")
        client_socket.close()

if __name__ == "__main__":
    start_client()
