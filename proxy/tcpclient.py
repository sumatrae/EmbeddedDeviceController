from config import cfg_parser
import socket

class tcpClient():
    def __init__(self):
        server_ip = "localhost"
        server_port = 30000
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((server_ip, server_port))

    def send(self, msg):
        self.client.send(msg.encode("utf-8"))
        recv = self.client.recv(1024).decode("utf-8")
        return recv


