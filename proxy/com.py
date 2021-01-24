import serial
import time 
import threading
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s")

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


class ComMessenger():
    def __init__(self, com, interval = 0, baudrate=115200):
        self.INVALID_RESULT = ""
        self.POLL_INTERVAL = 0.1

        self.com_conn = COM(com, interval, baudrate)
        # unreplied
        self.to_process_queue = dict()
        # replied
        self.processed_queue = dict()

        self.thread_polling = threading.Thread(target=ComMessenger.poll, args=(self,), daemon=True)
        self.thread_polling.start()

    def poll(self):
        while True:
            if len(self.to_process_queue) > 0:
                for msg_id in self.to_process_queue.keys():
                    self.com_conn.send(self.to_process_queue[msg_id])
                    reply = self.com_conn.receive()

                    self.processed_queue[msg_id] = reply
                    del self.to_process_queue[msg_id]
            else:
                time.sleep(self.POLL_INTERVAL)

    def send(self, msg_id, msg):
        if msg_id in self.to_process_queue.keys():
            logging.warn("Msg_id '{}' already exists, ignore.".format(msg_id))
        else:
            self.to_process_queue[msg_id] = msg

    # check whether replied
    def is_ok(self, msg_id):
        if msg_id in self.processed_queue:
            return True
        else:
            return False

    def recv(self, msg_id):
        # call is_ok() before recv()

        if msg_id in self.processed_queue:
            result = self.processed_queue[msg_id]
            del self.processed_queue[msg_id]
        else:
            result = self.INVALID_RESULT
        return result