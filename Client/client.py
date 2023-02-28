import socket
import threading
import tkinter as tk

# Configuration du client
PORT = 9001  # Port d'écoute du serveur
SERVER_ADDRESS = ""  # Adresse IP du serveur à renseigner par l'utilisateur

# Initialisation de la connexion client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Fonction pour envoyer le message
def send_message():
    message = message_entry.get()
    client_socket.send(message.encode())
    messages_text.insert("\n")
    messages_text.insert(tk.END, f"Vous: {message}\n")
    message_entry.delete(0, tk.END)

# Fonction pour recevoir les messages du serveur
def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode()
            messages_text.insert(tk.END, message)
        except ConnectionAbortedError:
            break

# Fonction pour se connecter au serveur
def connect_to_server():
    global SERVER_ADDRESS
    SERVER_ADDRESS = ip_entry.get()
    client_socket.connect((SERVER_ADDRESS, PORT))
    name = name_entry.get()
    client_socket.send(name.encode())

    connect_frame.pack_forget()
    chat_frame.pack(expand=True, fill="both")

    # Création d'un thread pour recevoir les messages du serveur
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

# Fonction pour quitter l'application
def quit_app():
    client_socket.close()
    root.destroy()

# Fonction pour se déconnecter du serveur
def disconnect():
    client_socket.send("exit".encode())
    client_socket.close()
    chat_frame.pack_forget()
    connect_frame.pack(expand=True, fill="both")
    
# Interface graphique
root = tk.Tk()
root.title("FreyaTalk Client")
# Frame de connexion
connect_frame = tk.Frame(root)
connect_frame.pack(expand=True, fill="both")

ip_label = tk.Label(connect_frame, text="Adresse IP du serveur :")
ip_label.pack()

ip_entry = tk.Entry(connect_frame)
ip_entry.pack(pady="5")

name_label = tk.Label(connect_frame, text="Votre nom :")
name_label.pack()

name_entry = tk.Entry(connect_frame)
name_entry.pack(pady="5")

connect_button = tk.Button(connect_frame, text="Se connecter", command=connect_to_server)
connect_button.pack(pady="10")

# Frame de chat
chat_frame = tk.Frame(root)

messages_label = tk.Label(chat_frame, text="Messages :")
messages_label.pack(anchor="center")

messages_text = tk.Text(chat_frame, height=15, width=60)
messages_text.pack(pady="5")

message_label = tk.Label(chat_frame, text="Votre message :")
message_label.pack(anchor="center")

message_entry = tk.Entry(chat_frame, width=50)
message_entry.pack(pady="5")

buttons_frame = tk.Frame(chat_frame)
buttons_frame.pack(pady="10")

send_button = tk.Button(buttons_frame, text="Envoyer", command=send_message)
send_button.pack(side="left")

disconnect_button = tk.Button(buttons_frame, text="Déconnecter", command=disconnect)
disconnect_button.pack(side="right")

quit_button = tk.Button(root, text="Quitter", command=quit_app)
quit_button.pack(side="bottom")

root.mainloop()