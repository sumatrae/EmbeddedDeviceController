
from socketserver import BaseRequestHandler, TCPServer, ThreadingTCPServer
import threading
from proxy.config import cfg_parser
from proxy.com import com


class COMHandler(BaseRequestHandler):

	lock = threading.Lock()

	def handle(self):
		print('Got connection from', self.client_address)
		while True:
			msg_from_tcp = self.request.recv(8192)
			if not msg_from_tcp:
				continue
			print("msg_from_tcp:",msg_from_tcp)
			self.lock.acquire()
			com.send(msg_from_tcp)
			msg_from_com = com.receive()
			self.lock.release()
			print("msg_from_com:",msg_from_com)
			if not msg_from_com:
				continue

			self.request.send(msg_from_com)


if __name__ == '__main__':
	tcpport = cfg_parser.get("PROXY", "tcpport")
	if tcpport is None:
		raise Exception("Please check tcpport in config file")

	# serv = TCPServer(('', int(tcpport)), Handler)
	serv = ThreadingTCPServer(('', int(tcpport)), COMHandler)
	serv.serve_forever()

