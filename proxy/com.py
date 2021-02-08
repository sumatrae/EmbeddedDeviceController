import serial
import time 
import threading
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s")

class COM():
    def __init__(self, com, interval = 0, baudrate=115200, commad_timeout=0.01):
        self.TIMEOUT = commad_timeout
        self.command_interval = interval
        self.conn = serial.Serial(com, baudrate, timeout=self.TIMEOUT)

    def send(self, str):
        if not isinstance(str, bytes):
            str = str.encode("ascii")

        self.conn.write(str)
        self.conn.flush()

    def receive(self):
        # return empty string "" when timeout?
        time.sleep(self.command_interval)
        return "".join([line.decode("ascii") for line in self.conn.readlines()])

    def flush(self):
        self.conn.flushInput()
        self.conn.flushOutput()


class ComMessenger():
    # message status
    MSG_PROCESSING = 0
    MSG_READY = 2
    MSG_EXPIRED = 3

    def __init__(self, com, interval = 0, baudrate=115200):
        self.INVALID_REPLY = ""
        self.POLL_INTERVAL = 0.1

        self.com_conn = COM(com, interval, baudrate)
        self.schedule_queue = list()
        self.to_process_dict = dict()
        self.processed_dict = dict()
        self.buffer_dict = dict()
        self.buffer_schedule = list()

        self.lock = threading.Lock()
        self.buffer_lock = threading.Lock()

        self.thread_polling = threading.Thread(target=ComMessenger.poll, args=(self,), daemon=True)
        self.thread_polling.start()

    def poll(self):
        while True:
            if len(self.buffer_dict) > 0:
                self.buffer_lock.acquire()
                self.lock.acquire()
                
                self.to_process_dict.update(self.buffer_dict)
                self.schedule_queue += self.buffer_schedule
                self.buffer_dict.clear()
                self.buffer_schedule.clear()

                self.lock.release()                
                self.buffer_lock.release()

            if len(self.schedule_queue) > 0:
                finished_msgs = []
                self.lock.acquire()
                try:
                    for msg_id in self.schedule_queue:
                        self.com_conn.send(self.to_process_dict[msg_id])
                        reply = self.com_conn.receive()

                        if reply:
                            self.processed_dict[msg_id] = {"msg": reply, 
                                                            "status": self.MSG_READY}
                        else:
                            # timeout, no reply
                            self.processed_dict[msg_id] = {"msg": self.INVALID_REPLY, 
                                                            "status": self.MSG_EXPIRED}
                        # flush per round end 
                        self.com_conn.flush()
                        finished_msgs.append(msg_id)
                    
                    for msg_id in finished_msgs:
                        del self.to_process_dict[msg_id]
                        self.schedule_queue.remove(msg_id)
                finally:
                    self.lock.release()
            else:
                time.sleep(self.POLL_INTERVAL)

    def send(self, msg_id, msg):
        if msg_id in self.to_process_dict.keys() or msg_id in self.buffer_dict.keys():
            logging.warn("Msg_id '{}' already exists, ignore.".format(msg_id))
        else:
            self.buffer_lock.acquire()
            self.buffer_dict[msg_id] = msg
            self.buffer_schedule.append(msg_id)
            # self.schedule_queue.append(msg_id)
            # self.to_process_dict[msg_id] = msg
            self.buffer_lock.release()

    def get_msg_status(self, msg_id):
        # If message of msg_id is expired, this msg_id will be 
        # deleted after call get_msg_status(). So do not call
        # get_msg_status() twice if the msg_id is expired.

        if msg_id in self.processed_dict.keys():
            if self.processed_dict[msg_id]["status"] == self.MSG_READY:
                return self.MSG_READY
            else:
                # delete expired message from processed_queue
                self.lock.acquire()
                del self.processed_dict[msg_id]
                self.lock.release()
                return self.MSG_EXPIRED
        else:
            return self.MSG_PROCESSING
            
    def recv(self, msg_id):
        # call get_msg_status() and make sure msg status is 
        # MSG_READY before calling recv().
        if msg_id in self.processed_dict.keys():
            result = self.processed_dict[msg_id]["msg"]
            self.lock.acquire()
            del self.processed_dict[msg_id]
            self.lock.release()
        else:
            result = self.INVALID_REPLY
        return result
