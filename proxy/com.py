import serial
import time
import threading
import logging
from config import cfg_parser

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s")


class COM():
	def __init__(self, com, interval=0, baudrate=115200, commad_timeout=1):
		self.timeout = commad_timeout
		self.command_interval = interval
		self.conn = serial.Serial(com, baudrate, timeout=self.timeout)

	def send(self, str):
		if not isinstance(str, bytes):
			str = str.encode("ascii")
		self.conn.write(str)
		self.conn.flush()

	def receive(self):
		time.sleep(self.command_interval)
		return self.conn.readall()
		# return "".join([line.decode("ascii") for line in self.conn.readlines()])


comport = cfg_parser.get("COM", "comport")
if comport is None:
	raise Exception("Please check comport in config file")
com = COM(comport)