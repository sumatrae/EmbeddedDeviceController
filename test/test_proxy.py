# import nose
from proxy.udpclient import UDPClient
# from proxy import Proxy
# from com import ComMessenger
# from udpclient import UDPClient

# def test_tcp():
#     print("============tcp test==============")
#     tcpclient = tcpClient()
#     assert tcpclient.send("hey") == "msg received"

# test_tcp()


def test_udp():
    print("===============udp test==========")
    udpclient = UDPClient()
    while True:
        recv = udpclient.received()
        print(recv)
        assert recv == "msg received"

test_udp()
