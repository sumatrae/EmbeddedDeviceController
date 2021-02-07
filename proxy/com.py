import time
import threading
import logging
import serial

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s")


class COM():
    def __init__(self, com, interval=0, baudrate=115200):
        self.TIMEOUT = 0
        self.command_interval = interval
        self.conn = serial.Serial(com, baudrate, timeout=self.TIMEOUT)

    def send(self, str):
        if not isinstance(str, bytes):
            str = str.encode("ascii")

        self.conn.write(str)
        self.conn.flush()

    def receive(self):
        time.sleep(self.command_interval)
        return "".join([line.decode("ascii")
                        for line in self.conn.readlines()])


class ComMessenger():
    # message status
    MSG_PROCESSING = 0
    MSG_READY = 2
    MSG_EXPIRED = 3

    def __init__(self, com_conn):
        self.INVALID_REPLY = ""
        self.POLL_INTERVAL = 0.1

        self.com_conn = com_conn
        # unreplied
        self.to_process_queue = dict()
        # replied
        self.processed_queue = dict()

        self.thread_polling = threading.Thread(
            target=ComMessenger.poll, args=(
                self,), daemon=True)
        self.thread_polling.start()

    def poll(self):
        while True:
            if len(self.to_process_queue) > 0:
                finished_msgs = []
                for msg_id in self.to_process_queue.keys():
                    self.com_conn.send(self.to_process_queue[msg_id])
                    reply = self.com_conn.receive()
                    # print(reply)

                    if reply:
                        self.processed_queue[msg_id] = {"msg": reply,
                                                        "status": self.MSG_READY}
                    else:
                        # timeout, no reply
                        self.processed_queue[msg_id] = {"msg": self.INVALID_REPLY,
                                                        "status": self.MSG_EXPIRED}
                    finished_msgs.append(msg_id)

                for msg_id in finished_msgs:
                    del self.to_process_queue[msg_id]
            else:
                time.sleep(self.POLL_INTERVAL)

    def send(self, msg_id, msg):
        if msg_id in self.to_process_queue.keys():
            logging.warn("Msg_id '{}' already exists, ignore.".format(msg_id))
        else:
            self.to_process_queue[msg_id] = msg

    def get_msg_status(self, msg_id):
        # If message of msg_id is expired, this msg_id will be
        # deleted after call get_msg_status(). So do not call
        # get_msg_status() twice if the msg_id is expired.

        if msg_id in self.processed_queue.keys():
            if self.processed_queue[msg_id]["status"] == self.MSG_READY:
                return self.MSG_READY
            else:
                # delete expired message from processed_queue
                del self.processed_queue[msg_id]
                return self.MSG_EXPIRED
        else:
            return self.MSG_PROCESSING

    def recv(self, msg_id):
        # call get_msg_status() and make sure msg status is
        # MSG_READY before calling recv().
        if msg_id in self.processed_queue.keys():
            result = self.processed_queue[msg_id]["msg"]
            del self.processed_queue[msg_id]
        else:
            result = self.INVALID_REPLY
        return result
