import time
import socket
import select
from com import COM
import threading

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(level)s %(filename)s:%(lineno)d - %(message)s")

def main():
    comport = "COM7"
    proxy_server.serve()
    com = COM(comport)
    udpport = 23333
    proxy_server = Proxy("localhost", 30000, comport)    
    udp_server = UDPServer(udpport, com)
    udp_server.broadcast(udpport)

class Proxy(object):
    
    def __init__(self, host, port, com, interval = 0, baudrate = 115200):
        self.LISTEN_NO = 20
        self.MAX_BUF_SZ = 8192
        self.address = (host, port)
        # set up TCP connection
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxy.bind(self.address)
        self.proxy.listen(self.LISTEN_NO)

        self.read_list = [self.proxy]
        self.write_list = []

        self.comconn = COM(com, interval, baudrate)

    def serve(self):
        logging.info("Proxy listen on: {}:{}".format(self.address[0], self.address[1]))

        while True:
            # new socket
            readset, _, _ = select.select(self.read_list, self.write_list, [])
            
            for sock in readset:
                if sock == self.proxy:
                    conn, address = self.proxy.accept()
                    logging.info("Accept connection from {}".format(address))
                    self.read_list.append(conn)
                else:
                    data = self.receive(sock)
                    if data:
                        logging.info("Read data: {}".format(str(data, encoding="utf-8")))
                        # send to board
                        self.comconn.send(data)
                        # receive from board
                        recv = self.comconn.receive().encode('ascii')
                        # send to pc
                        self.send(conn, recv)
                    else:
                        self.close_conntion(sock)

    def send(self, conn, data):
        try:
            conn.sendall(data)
        except Exception as e:
            logging.error(e)
            self.close_conntion(conn)

    def receive(self, conn):
        data = None
        try:
            data = conn.recv(self.MAX_BUF_SZ)
        except Exception as e:
            logging.error(e)
            self.close_conntion(conn)

        return data

    def close_conntion(self, conn):
        try:
            conn.close()
            self.read_list.remove(conn)
        except Exception as e:
            logging.error(e)

class UDPServer():
    def __init__(self, port, com, interval = 0, baudrate = 115200):
        # set up UDP
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # set up com 
        self.comconn = COM(com, interval, baudrate)
        self.BOARDCAST_INTERVAL = 1/3
        self.GET_INFO_INTERVAL = 1
        # bit 1 - 1, bit 2~3: mode (1,2,3) ,  bit 4: 0 if working, 1 otherwise
        self.board_status = (0b00000000).to_bytes(1, "big")

    def serve(self):
        # args is a tuple
        thread_broadcast = threading.Thread(target= UDPServer.broadcast, args=(self, ))
        thread_get_info = threading.Thread(target= UDPServer.get_board_status, args=(self, ))

        thread_broadcast.start() #Deamon
        thread_get_info.start() #Deamon
        thread_broadcast.join()
        thread_get_info.join()

    
    def broadcast(self, port):
        #enable broadcast
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        cmd = b"*STB?\n"
        self.get_board_status(cmd)
        while True:
            self.server.sendto(self.board_status, ('<broadcast>', port))
            print("message sent! @ {}".format(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())))
            time.sleep(self.BOARDCAST_INTERVAL)

    def get_board_status(self, cmd):
        while True:
            self.comconn.send(cmd)
            recv = self.comconn.receive().encode('ascii')
            self.board_status = recv
            sleep(self.GET_INFO_INTERVAL)

if __name__ == "__main__":
    main()