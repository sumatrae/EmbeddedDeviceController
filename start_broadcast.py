from proxy import cfg_parser
from proxy import BroadcastServer


def main():
	tcp_server_port = cfg_parser.get("PROXY", "tcpport")
	if tcp_server_port is None:
		raise Exception("Please check tcpport in config file")

	broadcast_port = cfg_parser.get("PROXY", "udpport")
	if broadcast_port is None:
		raise Exception("Please check udpport in config file")
	broadcast_server = BroadcastServer(broadcast_port, tcp_server_port)
	broadcast_server.serve()


if __name__ == '__main__':
	main()