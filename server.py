import random
import string
import socket
import threading
import datetime
from queue import Queue

def random_name():
    return ''.join(random.choices(string.ascii_letters, k=8))

def broadcast():
    while True:
        if not message_queue.empty():
            client_name, message = message_queue.get()
            with message_lock:
                timestamp = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
                for client in clients:
                    print(f'{timestamp} {client_name}: {message}')
                    try:
                        client.send(f'{timestamp} {client_name}: {message}'.encode())
                    except socket.error as e:
                        print("Error sending message: ", e)
                        clients.pop(client)
                        message_queue.put(('Server', f"{client_name} has disconnected!"))
                with open("messages.txt", "a") as log_file:
                    try:
                        log_file.write(f"{timestamp} {client_name}: {message}\n")
                    except Exception as e:
                        print("Error writing to log file: ", e)

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            message_queue.put((client_name, message))
        except ConnectionResetError as e:
            print("Error receiving message: ", e)
            message_queue.put(('Server', f"{client_name} has disconnected!"))
            break

def handle_server():
    while True:
        message = input()
        message_queue.put(('Server', message))

clients = {}
message_queue = Queue()
message_lock = threading.Lock()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 1234))
server_socket.listen()

print("Server is listening on 0.0.0.0:1234")

threading.Thread(target=handle_server).start()

while True:
    client_socket, client_address = server_socket.accept()
    client_name = random_name()
    print(f'{client_name} connected')
    client_socket.send(f'Welcome, your name is {client_name}. Number of users online: {len(clients)}'.encode())
    message_queue.put(('Server', f"{client_name} has joined the room!"))
    try:
        clients[client_socket] = client_name
        threading.Thread(target=handle_client, args=(client_socket,)).start()
        threading.Thread(target=broadcast).start()
    except Exception as e:
        print("Error adding client to list: ", e)
        client_socket.close()
