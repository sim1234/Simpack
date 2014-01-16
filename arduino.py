# coding:utf-8

import serial
from threading import Thread

class Serial(object):
    
    def __init__(self, port = 3, speed = 9600):
        self.port = port
        self.speed = speed
        self.serial = serial.Serial(port - 1, speed)
        self.data = ""
        
        self.thread = None
  

    def recive(self):
        d = self.serial.read(self.serial.inWaiting())
        self.data += d
        return d
    
    def split_data(self, d = "\n"):
        while d in self.data:
            r, self.data = self.data.split(d, 1)
            yield r

    def send(self, data):
        return self.serial.write(data)
    
    def _async(self):
        self.recive()
        for l in self.split_data("\n"):
            print "<`%s`" % l
    
    def print_async(self):
        self.thread = Thread(target = self._async)
        self.thread.start()
        
        
        
        
        
        

        
        



