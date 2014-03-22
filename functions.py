# coding: utf-8

import re
import sys
import math
import time
import pygame
import ctypes
import StringIO
import threading
import multiprocessing


def python_frozen():
    return hasattr(sys, "frozen")
    
def install_hacks(log = ""):
    multiprocessing.freeze_support() # Freeze support
    if log: # Log
        sys.stdout = sys.stderr = Logger(log)
    try: # UTF-8 hack
        if python_frozen():
            sys.setdefaultencoding("UTF-8")
            print "UTF-8 hack installed."
    except AttributeError:
        print "UTF-8 hack not installed!"
    
def alert(msg = "Alert!", title = "Alert", a = 0, b = 0x00001000):
        #ctypes.windll.user32.MessageBoxA(a, msg, title, b)
        return SubProces(ctypes.windll.user32.MessageBoxA, 0, 0, a, msg, title, b)
    

        

def va2xy(v, a):
    return v * math.cos(a), v * math.sin(a)

def xy2va(x, y):
    return math.hypot(x, y), math.atan2(y, x)

def normaliserad(rad): # zamienia podaną liczbę radianów na liczbę z przedziału <0, 2*pi)
    while rad<0:
        rad+=2*math.pi
    while rad>=2*math.pi:
        rad-=2*math.pi
    return rad


def tuc(s):
    try:
        return unicode(s, "UTF-8")
    except:
        try:
            return unicode(str(s), "UTF-8")
        except:
            return s

def between(s, start, end):
    try:
        i1 = s.index(start) + len(start)
        i2 = s.index(end, i1)
        return s[i1:i2]
    except:
        return ""
    
def fill_to(v, ln, f = " "):
    v = str(v)
    if len(v) > ln:
        return v[:ln]
    return v + f * (ln - len(v))

def color_from_str(s):
    if s[0] == "(":
        s = s[1:]
    if s[-1] == ")":
        s = s[:-1]
    c = []
    for v in s.split(","):
        v = int(v)
        #if v < 0 or v > 255:
        #    print "Warning: "
        c.append(v)
    #return pygame.color.Color(*c)
    return tuple(c)

def invert_color(c):
    return tuple(map(lambda x: 255 - x, c))


def key_name(key):
    k = pygame.key.name(key)
    return k[0].upper() + k[1:].lower()

                    
def load_image(content, name=".jpg"):
    return pygame.image.load(StringIO.StringIO(content), name)

def load_ld(content):
    return eval(content)

def load_config(config):
    c = {}
    for l in config.splitlines(False):
        if re.match(r"^\s*#.*$", l):
            continue
        #m = re.match(r"^\s*(\w+)\s*=\s*(.*)\s*$", l)
        m = re.match(r"^(\w+)=(.*)$", l)
        if m:
            c[m.group(1)] = m.group(2)
    return c

def make_config(config):
    r = ""
    for k, v in config.iteritems():
        r += "%s=%s\n" % (k, v)
    return r


def my_exec(code):
    d = {}
    d["__builtins__"] = __builtins__
    c = "__builtins__.__import__=None\n" + code
    exec c in d
    d.pop("__builtins__")
    return d



class Controls(object):
    def __init__(self, *functions_to_control):
        self.fns = functions_to_control

    def __getitem__(self, index):
        return self.fns[index][0]

    def __call__(self, t, *ifs):
        x = 0
        while x < len(ifs):
            if ifs[x]:
                self.fns[x](t)
            x += 1


class SubProces(threading.Thread):
            def __init__(self, function, lag = 0, maxduration = 0, *args, **kwargs):
                threading.Thread.__init__(self)
                self.function = function
                self.result = None
                self.running = 2
                self.a = args
                self.k = kwargs
                self.lag = lag / 1000.0
                self.stoper = None
                self.start()
                #if maxduration:
                #    self.stoper = SubProces(self.stop, maxduration, 0)
                    
          
            def run(self):
                self.running = 1
                if self.lag:
                    time.sleep(self.lag)
                self.result = self.function(*self.a, **self.k)
                #if self.stoper:
                #    self.stoper.stop()
                self.running = 0
                
            
            def stop(self):
                if self.running:
                    self.running = 0
                    #if self.stoper:
                    #    self.stoper.stop()
                    self.join()
                    self.join(0)
                    self.join(1)
                
            def get_result(self):
                if self.running:
                    raise RuntimeError("Function didn't finish yet!")
                else:
                    return self.result
            
            def wait_for_result(self, sleep = 0.0001):
                while not self.running:
                    if sleep:
                        time.sleep(sleep)
                return self.result



class Logger(object):
    def __init__(self, filename, std = None):
        if std is None:
            std = sys.stdout
        self.terminal = std
        self.log = open(filename, "w", 0)
        self.log.write(time.ctime() + "\n")
        self._lc = "\n"

    def write(self, message):
        self.terminal.write(message)
        if self._lc == "\n":
            self.log.write(fill_to("%f" % time.clock(), 15, " ") + ": ")
        if message:
            self._lc = message[-1]
        self.log.write(message)
        
    def flush(self):
        self.terminal.flush()
        self.log.flush()


