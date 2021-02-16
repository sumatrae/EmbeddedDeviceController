
from socketserver import ThreadingTCPServer
from proxy import COMHandler
from proxy import cfg_parser


def main():
    tcpport = cfg_parser.get("PROXY", "tcpport")
    if tcpport is None:
        raise Exception("Please check tcpport in config file")

    print("starting tcp server")
    serv = ThreadingTCPServer(('', int(tcpport)), COMHandler)
    serv.serve_forever()


if __name__ == '__main__':
    main()
