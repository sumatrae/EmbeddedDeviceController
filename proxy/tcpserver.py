from com import com
from socketserver import BaseRequestHandler, TCPServer

from config import cfg_parser


class Handler(BaseRequestHandler):
	def handle(self):
		print('Got connection from', self.client_address)
		while True:
			msg_from_tcp = self.request.recv(8192)
			print(msg_from_tcp)
			com.send(msg_from_tcp)
			msg_from_com = com.receive()
			print(msg_from_com)
			if not msg_from_com:
				break

			self.request.send(msg_from_com)


if __name__ == '__main__':
	tcpport = cfg_parser.get("PROXY", "tcpport")
	if tcpport is None:
		raise Exception("Please check tcpport in config file")

	try:
		serv = TCPServer(('', tcpport), Handler)
		serv.serve_forever()
	finally:
		serv.server_close()
