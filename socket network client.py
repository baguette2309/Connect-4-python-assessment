import socket
from _thread import *
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.198.13"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.id = self.connect()
        start_new_thread(self.recieve_server, ())

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            pass
    
    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
        except socket.error as e:
            print(e)
    
    def recieve_server(self):
        while True:
            data = self.client.recv(2048)
            print(f"recieve: {pickle.loads(data)}")

n = Network()
while True:
    item = input("Send to server: ")
    if item == "":
        continue
    n.send(item)

    if item == "break":
        break

n.client.close()
