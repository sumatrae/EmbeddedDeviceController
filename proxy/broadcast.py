import logging
import threading
import time
from config import cfg_parser
import socket

from threading import Timer


class BroadcastServer():
	boardcast_interval = 0.33
	status_cmd = b"*STB?\n"

	def __init__(self, broadcast_port, tcp_server_port,timer_peroid = 5.0):
		# set up UDP
		self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # enable broadcast
		self.broadcast_port = int(broadcast_port)
		self.tcpport = int(tcp_server_port)
		self.timer_peroid = timer_peroid
		self.board_status = 0x80

		self.t = Timer(self.timer_peroid, self.get_board_status)
		self.t.start()

	def serve(self):
		while True:
			# print(type(self.board_status),self.board_status)
			self.server.sendto(bytes([self.board_status]),
			                   ('<broadcast>', self.broadcast_port))
			time.sleep(self.boardcast_interval)

	def get_board_status(self):
		tcp_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcp_cli.connect(('localhost', self.tcpport))
		tcp_cli.send(self.status_cmd)
		buff = tcp_cli.recv(8192)
		print(buff)
		if buff is not None and len(buff) == 2 and buff[1] == 13:
			print("board_status updated")
			self.board_status = buff[0]

		tcp_cli.close()

		self.t = Timer(self.timer_peroid, self.get_board_status)
		self.t.start()


if __name__ == "__main__":
	tcp_server_port = cfg_parser.get("PROXY", "tcpport")
	if tcp_server_port is None:
		raise Exception("Please check tcpport in config file")

	broadcast_port = cfg_parser.get("PROXY", "udpport")
	if broadcast_port is None:
		raise Exception("Please check udpport in config file")
	broadcast_server = BroadcastServer(broadcast_port, tcp_server_port)
	broadcast_server.serve()
