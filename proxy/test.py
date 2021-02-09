import socket
import time
tcp_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_cli.connect(('localhost', 30000))
tcp_cli.send(b"hello")
buff = tcp_cli.recv(8192)
print(buff)
time.sleep(100)

tcp_cli.close()
