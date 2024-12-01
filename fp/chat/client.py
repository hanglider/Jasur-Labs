import socket
from threading import Thread
from datetime import datetime

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5002
separator_token = "<SEP>"

s = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")

def listen_for_messages():
    while True:
        try:
            message = s.recv(1024).decode()
            print("\n" + message)
        except ConnectionResetError:
            print("[INFO] Server closed the connection.")
            break

t = Thread(target=listen_for_messages)
t.daemon = True
t.start()

while True:
    room = input("Enter your room: ")
    s.send(f"/join {room}\n".encode())

    while True:
        to_send = input()
        if to_send.lower() == "/exit":
            s.send("/exit\n".encode())
            print("[INFO] Left the room. Choose another room.")
            break
        if to_send.lower() == "/quit":
            s.send("/quit\n".encode())
            print("[INFO] Disconnected from the server.")
            s.close()
            exit()
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        to_send = f"[{date_now}] {to_send}"
        s.send(to_send.encode())