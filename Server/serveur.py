import tkinter as tk
import socket
import threading

IP = '0.0.0.0'
PORT = 9001
SERVER_ADDRESS = (IP, PORT)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(SERVER_ADDRESS)
server_socket.listen()

clients = []

def handle_client_connection(client_socket, client_address):
    print(f"Nouvelle connexion : {client_address}")
    client_name = client_socket.recv(1024).decode()
    clients.append((client_socket, client_name))

    while True:
        try:
            message = client_socket.recv(1024).decode()
            print(f"{client_name}: {message}.")
            if not message:
                break

            for client in clients:
                if client[0] != client_socket:
                    client[0].send(f"{client_name}: {message}".encode())

        except ConnectionResetError:
            break

    clients.remove((client_socket, client_name))
    print(f"Déconnexion : {client_address}")

def start_server():
    server_socket.bind(SERVER_ADDRESS)
    server_socket.listen()
    global server_thread
    server_thread = threading.Thread(target=server_socket.serve_forever)
    server_thread.start()
    print(f"Serveur démarré sur {IP}:{PORT}")

def stop_server():
    server_socket.shutdown(socket.SHUT_RDWR)
    server_socket.close()
    server_thread.join()
    print("Serveur arrêté")

def update_textbox():
    # Ajoutez le code ici pour mettre à jour le contenu de la zone de texte
    pass

# Créez la fenêtre principale
root = tk.Tk()
root.title("Mon application")

# Créez un bouton pour démarrer le serveur
start_button = tk.Button(root, text="Démarrer le serveur", command=start_server)
start_button.pack()

# Créez un bouton pour arrêter le serveur
stop_button = tk.Button(root, text="Arrêter le serveur", command=stop_server)
stop_button.pack()

# Créez une zone de texte pour afficher les événements du serveur
textbox = tk.Text(root, width=50, height=20)
textbox.pack()

# Créez une fonction de rappel pour mettre à jour la zone de texte
root.after(1000, update_textbox)

# Lancez la boucle principale de l'interface graphique
root.mainloop()
