# coding: utf-8

import sys
import math
import pygame
import StringIO

from .dataprovider import load_config
#load_config

def python_frozen():
    return hasattr(sys, "frozen")
    

def va2xy(v, a):
    return v * math.cos(a), v * math.sin(a)

def xy2va(x, y):
    return math.hypot(x, y), math.atan2(y, x)

def between(s, start, end):
    try:
        i1 = s.index(start) + len(start)
        i2 = s.index(end, i1)
        return s[i1:i2]
    except:
        return ""

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
                    

def tuc(s):
    try:
        return unicode(s, "UTF-8")
    except:
        try:
            return unicode(str(s), "UTF-8")
        except:
            return s

def load_image(content, name=".jpg"):
    return pygame.image.load(StringIO.StringIO(content), name)

def load_ld(content):
    return eval(content)

def my_exec(code):
    d = {}
    d["__builtins__"] = __builtins__
    c = "__builtins__.__import__=None\n" + code
    exec c in d
    d.pop("__builtins__")
    return d


