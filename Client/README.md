# FreyaTalk Client
This code provides a graphical user interface for a client to connect to a chat server and send/receive messages. The client uses sockets to communicate with the server and tkinter library for the GUI.

## Installation

Pour utiliser FreyaTalk Client. Installés Python et Git.

Python: https://www.python.org/downloads/ 

Git: https://git-scm.com/downloads


Procédure d'installation: 
```bash
  mkdir FreyaTalk
  cd FreyaTalk
  git clone https://github.com/yrozand/FreyaTalk.git
  pip install -r requirements.txt
```
Démarée la partie serveur
```
    python serveur.py
```
Démarée une client:
```
    python client.py
```

Amusez vous ! à discuté avec vos amis
## Usage/Examples

- Démarrez le serveur de chat sur une machine séparée ou sur la même machine.
- Exécutez le code client en exécutant la commande : python chat_client.py
- Saisissez l'adresse IP du serveur de chat dans le champ de saisie prévu à cet effet et cliquez sur le bouton "Connect".
- Saisissez votre nom dans le champ de saisie prévu à cet effet et cliquez sur le bouton "Connecter".
- Tapez votre message dans le champ de saisie et cliquez sur le bouton "Send" pour envoyer le message au serveur de chat.
- Pour vous déconnecter du serveur de chat, cliquez sur le bouton "Disconnect".
- Pour quitter l'application, cliquez sur le bouton "Quitter".


## Authors

- [@yrozand](https://www.github.com/yrozand)


## Documentation

## Documentation du code Imports
Le module socket est utilisé pour créer des connexions réseau entre des machines. Le module threading permet de créer des threads pour exécuter plusieurs tâches en parallèle. Le module tkinter est utilisé pour créer une interface graphique.

```
import socket
import threading
import tkinter as tk
```
## Configuration
Le port d'écoute du serveur et l'adresse IP du serveur sont configurés.

```
PORT = 9001
SERVER_ADDRESS = ""
```
Une socket est créée pour établir une connexion client.

```
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```
## Fonction pour envoyer un message
Cette fonction récupère le message tapé dans l'interface graphique et l'envoie au serveur via la socket du client. Elle affiche ensuite le message envoyé dans l'interface graphique.

```
def send_message():
    message = message_entry.get()
    client_socket.send(message.encode())
    messages_text.insert(tk.END, f"Vous: {message}\n")
    message_entry.delete(0, tk.END)
```
## Fonction pour recevoir des messages
Cette fonction est exécutée dans un thread séparé pour permettre au client de recevoir des messages du serveur en continu. Elle affiche les messages reçus dans l'interface graphique.

```
def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode()
            messages_text.insert(tk.END, message)
        except ConnectionAbortedError:
            break
```
## Fonction pour se connecter au serveur
Cette fonction est appelée lorsque l'utilisateur clique sur le bouton de connexion. Elle récupère l'adresse IP du serveur et le nom de l'utilisateur dans l'interface graphique. Elle établit ensuite une connexion avec le serveur en utilisant la socket du client. Elle cache ensuite la frame de connexion et affiche la frame de chat. Elle crée également un thread pour recevoir des messages du serveur.

```
def connect_to_server():
    global SERVER_ADDRESS
    SERVER_ADDRESS = ip_entry.get()
    client_socket.connect((SERVER_ADDRESS, PORT))
    name = name_entry.get()
    client_socket.send(name.encode())

    connect_frame.pack_forget()
    chat_frame.pack(expand=True, fill="both")

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()
```
## Fonction pour quitter l'application
Cette fonction est appelée lorsque l'utilisateur clique sur le bouton pour quitter l'application. Elle ferme la socket du client et détruit la fenêtre de l'interface graphique.

```
    def quit_app():
    client_socket.close()
    root.destroy()
```
## Fonction pour se déconnecter du serveur
Cette fonction est appelée lorsque l'utilisateur clique sur le bouton pour se déconnecter du serveur. Elle envoie un message "exit" au serveur via la socket du client pour signaler que l'utilisateur se déconnecte. Elle ferme ensuite la socket du client et cache la frame de chat pour afficher la frame de connexion.

```
def disconnect():
    client_socket.send("exit".encode())
    client_socket.close()
    chat_frame.pack_forget()
    connect_frame.pack(expand=True, fill="both")
```
## Interface graphique
Une fenêtre principale est créée à l'aide de la classe Tk.

```
root = tk.Tk()
root.title("FreyaTalk")
```

