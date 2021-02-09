from proxy.config import cfg_parser
import socket


class UDPClient():
    def __init__(self):
        # ipaddr = "localhost"
        udpport = 23333
        self.client = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM)
            # socket.IPPROTO_UDP)
        # self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # self.client.setblocking(0)
        self.client.bind(("", udpport))

    def received(self):
        recv, addr = self.client.recvfrom(1024)
        recv = recv.decode("ascii")
        return recv
