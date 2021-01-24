import logging
import threading
import time
import socket
import select

from com import ComMessenger

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s")

class Proxy(object):

    def __init__(self, host, port, com_messenger):
        self.LISTEN_NO = 20
        self.MAX_BUF_SZ = 8192
        self.address = (host, port)

        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxy.bind(self.address)
        self.proxy.listen(self.LISTEN_NO)

        self.comconn = com_messenger

        self.read_list = [self.proxy]
        self.write_list = []

        self.msg_id = 1

    def serve(self):
        logging.info("Proxy listen on: {}:{}".format(self.address[0], self.address[1]))
        # multi-PC
        to_process_msgs = {} # msg_id_str: connection
        processed_msgs = {} # connection: [msg_to_reply]

        while True:
            # read from PC & write to PC
            readset, writeset, _ = select.select(self.read_list, self.write_list, [])
            
            # accept new connection and read data
            for sock in readset:
                if sock == self.proxy:
                    conn, address = self.proxy.accept()
                    logging.info("Accept connection from {}".format(address))
                    self.read_list.append(conn)
                else:
                    data = self.receive(sock)
                    if data:
                        logging.info("Read data: {}".format(data))
                        
                        # send to board
                        msg_id_str = self.__new_msgid_str()
                        self.comconn.send(msg_id_str, data)
                        to_process_msgs[msg_id_str] = sock
                    else:
                        self.closeConn(sock)

            # write data to clients
            for sock in writeset:
                if sock in processed_msgs.keys():
                    for msg in processed_msgs[sock]:
                        self.send(sock, msg)
                    del processed_msgs[sock]
                self.write_list.remove(sock)

            # check if COM replies
            for msg_id_str in to_process_msgs.keys():
                if self.comconn.is_ok(msg_id_str):
                    sock = to_process_msgs[msg_id_str]
                    if sock in processed_msgs.keys():
                        processed_msgs[sock].append(self.comconn.recv(msg_id_str))
                    else:
                        processed_msgs[sock] = [self.comconn.recv(msg_id_str)]
                    del to_process_msgs[msg_id_str]
            
            # add replies from COM to send queue
            for sock in processed_msgs.keys():
                if sock not in self.write_list:
                    self.write_list.append(sock)

    def __new_msgid_str(self):
        msg_id_str = "TCP_{}".format(self.msg_id)
        self.msg_id += 1
        return msg_id_str

    def send(self, conn, data):
        if isinstance(data, str) is True:
            data = bytes(data, "ascii")
        try:
            conn.sendall(data)
        except Exception as e:
            logging.error(e)
            self.closeConn(conn)

    def receive(self, conn):
        data = None
        try:
            data = conn.recv(self.MAX_BUF_SZ)
        except Exception as e:
            logging.error(e)
            self.closeConn(conn)

        return data.decode("ascii")

    def closeConn(self, conn):
        logging.info("Closing one connection: {}".format(conn))
        try:
            conn.close()
            if conn in self.read_list:
                self.read_list.remove(conn)
            if conn in self.write_list:
                self.write_list.remove(conn)
        except Exception as e:
            logging.error(e)


class UDPServer():
    def __init__(self, broadcast_port, com_messenger):
        # set up UDP
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.broadcast_port = broadcast_port

        # set up com 
        self.comconn = com_messenger

        self.BOARDCAST_INTERVAL = 1/3
        self.GET_INFO_INTERVAL = 1
        # bit 1 - 1, bit 2~3: mode (1,2,3) ,  bit 4: 0 if working, 1 otherwise
        self.board_status = (0b00000000).to_bytes(1, "big")

    def serve(self):
        # args is a tuple
        thread_broadcast = threading.Thread(target= UDPServer.broadcast, args=(self, ), daemon=True)
        thread_get_info = threading.Thread(target= UDPServer.get_board_status, args=(self, ), daemon=True)

        thread_broadcast.start() 
        thread_get_info.start() 
    
    def broadcast(self):
        #enable broadcast
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while True:
            self.server.sendto(self.board_status, ('<broadcast>', self.broadcast_port))
            print("message sent! @ {}".format(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())))
            time.sleep(self.BOARDCAST_INTERVAL)

    def get_board_status(self):
        status_cmd = "*STB?\n"
        msg_id_str = "UDP_1"
        msg_id = 1

        self.comconn.send(msg_id_str, status_cmd)

        while True:            
            if self.comconn.is_ok(msg_id_str):
                recv = self.comconn.recv(msg_id_str).encode('ascii')
                self.board_status = recv

                msg_id += 1
                msg_id_str = "UDP_{}".format(msg_id)
                self.comconn.send(msg_id_str, status_cmd)

            time.sleep(self.GET_INFO_INTERVAL)

if __name__ == "__main__":
    com = "COM7"
    udp_broadcast_port = 23333

    com_messenger = ComMessenger(com)
    proxy_server = Proxy("localhost", 30000, com_messenger)
    udp_server = UDPServer(udp_broadcast_port, com_messenger)
    
    proxy_server.serve()
    udp_server.serve()
