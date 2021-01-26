import nose
from tcpclient import tcpClient
from proxy import Proxy
from com import ComMessenger
from udpclient import udpClient

# def test_tcp():
#     print("============tcp test==============")
#     tcpclient = tcpClient()
#     assert tcpclient.send("hey") == "msg received"

# test_tcp()


def test_udp():
    print("===============udp test==========")
    udpclient = udpClient()
    recv = udpclient.received()
    print(recv)
    assert recv == "msg received"

test_udp()
