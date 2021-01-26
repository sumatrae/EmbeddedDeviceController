from com import ComMessenger
from proxy import Proxy, UDPServer
import threading 

class COM():
    def __init__(self, com, interval = 0, baudrate=115200):
        pass

    def send(self, str):
        print("send = {}".format(str))

    def receive(self):
        return "msg received"

if __name__ == "__main__":
    comport = "COM7"
    udp_broadcast_port = 23333
    com = COM(comport, interval = 0 , baudrate = 115200)
    com_messenger = ComMessenger(com)

    # proxy_server = Proxy("localhost", 30000, com_messenger)
    # proxy_server.serve()

    udp_server = UDPServer(udp_broadcast_port, com_messenger)
    udp_server.serve()
    udp_server.broadcast()
