import os
import threading
from time import sleep
from os import path

class IIOCollector(object):
    def __init__(self, device):
        self.device = device
        self.collecting = True
        self.thread = None
        self.dev_path = path.join('/dev', device.sys_id)
        self.inp = os.open(self.dev_path, os.O_RDONLY | os.O_NONBLOCK)
        self.data = []

    def __del__(self):
        os.close(self.inp)

    def collect_data(self):
        while self.collecting:
            try:
                data = os.read(self.inp, self.device.buffer_size)
                n = 0
                row = {}
                for el in sorted(self.device.channels, key=lambda x: x.index):
                    n += el.parse_data(data[n:])
                    row[el.name] = el.value
                self.data.append(row)
            except OSError:
                sleep(.1)

    def get_data(self):
        d = self.data
        self.data = []
        return d

    def start(self):
        self.thread = threading.Thread(target=self.collect_data)
        self.thread.start()

    def stop(self):
        self.collecting = False
        self.thread.join()
