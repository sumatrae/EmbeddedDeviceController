import serial
import time 

class COM():
    def __init__(self, com, interval = 0, baudrate=115200):
        self.command_interval = interval
        self.conn = serial.Serial(com, baudrate, timeout=0)

    def send(self, str):
        if not isinstance(str, bytes):
            str = str.encode("ascii")

        self.conn.write(str)
        self.conn.flush()

    def receive(self):
        time.sleep(self.command_interval)
        return "".join([line.decode("ascii") for line in self.conn.readlines()])
