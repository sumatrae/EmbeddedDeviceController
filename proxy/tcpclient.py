import socket


class TCPClient():
    def __init__(self):
        server_ip = "localhost"
        server_port = 30000
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((server_ip, server_port))

    def send(self, msg):
        self.client.send(msg.encode("ascii"))
        recv = self.client.recv(1024).decode("ascii")
        return recv
