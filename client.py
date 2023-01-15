import socket
import threading

def handle_input():
    while True:
        message = input()
        client_socket.send(message.encode())

def handle_server():
    while True:
        message = client_socket.recv(1024).decode()
        print(message)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 1234))

print(client_socket.recv(1024).decode())

threading.Thread(target=handle_input).start()
threading.Thread(target=handle_server).start()
