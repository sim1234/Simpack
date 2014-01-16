# coding: utf-8

import sys
import pygame
from .functions import python_frozen


class GameBase(object):
    CHANGE_GAMEPART_EVENT_ID = 27

    def __init__(self):
        try:
            if python_frozen(): # UTF-8 hack
                sys.setdefaultencoding("UTF-8")
        except AttributeError:
            print "Error in UTF-8 hack"
        
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        #pygame.key.set_repeat(1, 1)
        self.config = self.load_config()
        self.width = int(self.config["width"])
        self.height = int(self.config["height"])
        self.working = False
        self.fps = int(self.config["maxfps"])
        self.keys = pygame.key.get_pressed()
        self.fpsclock = pygame.time.Clock()
        self.caption = self.config["caption"]
        self.fullscreen = self.config["fullscreen"] == "True"

        self.gameparts = {}
        self.gamepart = self.add_gamepart("Exit", ExitGamePart)
        self.last_return = {"_from" : self.gamepart._name}
        self.gamepart._start(self.last_return)
        self.init_display()
        self.init()
        #self.get_current_gamepart()._start(self._last_return)

    def init_display(self):
        if self.fullscreen:
            self.window = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.caption)
        self.screen = pygame.display.get_surface()
        self.bufor = pygame.Surface((self.width, self.height), flags=pygame.HWSURFACE)


    def print_text(self, px, py, text, bit = None, size=10, color=(0,0,0), bgcolor=(200,200,200)):
        if bit == None:
            bit = self.bufor
        font = pygame.font.Font(pygame.font.match_font('doesNotExist,Arial'), size)
        text = font.render(text, True, color)
        if bgcolor is not None:
            text = font.render(text, True, color, bgcolor)
        textRect = text.get_rect()
        textRect.x = px
        textRect.y = py
        bit.blit(text, textRect)

    def frame(self):
        self.gamepart._frame(self.bufor)

        self.keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.change_gamepart("Exit")
            elif event.type == self.CHANGE_GAMEPART_EVENT_ID:
                self.working = bool(self.change_gamepart_to(event.new_gp_name))
                break
            else:
                self.gamepart.event(event)

        if self.keys[pygame.K_BACKQUOTE]: # FPS
            self.print_text(self.width-18, self.height-10, str(int(self.fpsclock.get_fps())))

        self.screen.blit(self.bufor, (0,0))
        pygame.display.flip()
        #self.bufor.fill((255,255,255))
        self.fpsclock.tick(self.fps)
        #pygame.time.wait(1)

    def add_gamepart(self, name, gameparttype, *args, **kwargs):
        g = gameparttype(self, name, *args, **kwargs)
        self.gameparts[name] = g
        return g

    def change_gamepart(self, new_gp_name):
        if not self.gameparts.has_key(new_gp_name):
            raise IndexError("No GamePart named '%s'!" % new_gp_name)
        pygame.event.post(pygame.event.Event(self.CHANGE_GAMEPART_EVENT_ID, {"new_gp_name" : new_gp_name}))

    def change_gamepart_to(self, new_gp_name):
        self._last_return = self.gamepart._stop()
        self.gamepart = self.gameparts[new_gp_name]
        if self.gamepart:
            self.gamepart._start(self._last_return)
        pygame.event.clear()
        return self.gamepart


    def fast_run(self, name):
        self._last_return = self.gamepart._stop()
        self.gameparts[name]._start(self._last_return)
        self._last_return = self.gameparts[name]._stop()
        self.gamepart._start(self._last_return)


    def _main_loop(self):
        self.working = True
        while self.working:
            self.frame()
        pygame.mixer.fadeout(100) # Fade out sound in 0.1s and quit in 0.2s
        pygame.time.wait(200)     #

    def main_loop(self, debug = False):
        if debug:
            try:
                self._main_loop()
                print "Normal Exit."
                return 0
            except (SystemExit, KeyboardInterrupt):
                print "System Exit."
                return 1
            except:
                import sys
                import traceback
                print >> sys.stderr, "Error in game:"
                traceback.print_exc()
                return 2
        else:
            self._main_loop()
            return 0


    def init(self):
        pass
        # Override to initialize game [add gameparts]

    def load_config(self):
        return {
                "width" : "640",
                "height" : "480",
                "caption" : "Game",
                "maxfps" : "120",
                "fullscreen" : "False"
                }
        # Override to configure game





class GamePart(object):
    
    def init(self):
        pass
        # Override to configure gamepart     

    def start(self, data):
        pass
        # Override to initialize gamepart
    
    def first_frame(self, bufor):
        pass
        # Override to display first frame
        
    def frame(self, bufor):
        pass
        # Override to generate frames

    def event(self, event):
        pass
        # Override to process events
            
    def stop(self):
        return {}
        # Override to uninitialize gamepart
        
    
    
    def __init__(self, topgame, name):
        self._topgame = topgame
        self._name = name
        self._first = True
        self._return = {}
        self.init()
        
    def change_gamepart(self, new_gp_name):
        self._topgame.change_gamepart(new_gp_name)
    
    def get_last_gamepart(self):
        return self._return.get("_from", "Exit")

    def _start(self, data):
        self._return = data
        self._first = True
        self.start(data)
    

    def _stop(self):
        self._return["_from"] = self._name
        self._return.update(self.stop())
        return self._return
    

    def _frame(self, bufor):
        if self._first:
            self.first_frame(bufor)
            self._first = False
        self.frame(bufor)    

    def __nonzero__(self):
        return True

    def __repr__(self):
        return "<%s GamePart>" % self._name




class ExitGamePart(GamePart):
    def __nonzero__(self):
        return False




"""
class Return(object):
    def __init__(self, **kvars):
        self.data = kvars

    def update(self, iterable):
        self.data.update(iterable)

    def add(self, key, value):
        self.data[key] = value

    def has_key(self, key):
        return self.data.has_key(key)

    def get_data(self):
        return self.data

    def get(self, key, default = None):
        return self.data.get(key, default)

    def __getitem__(self, key):
        return self.data.get(key, None)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        self.pop(key)

    def pop(self, key):
        self.data.pop(key)

    def __repr__(self):
        return "<Return object: %s>" % str(self.data)
"""


