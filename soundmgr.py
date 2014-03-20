# coding: utf-8

import pygame

class SoundManager(object):
    def __init__(self):
        pygame.mixer.init(buffer=512)
        #pygame.mixer.init() # Just f*****g windows
        self.sounds = {}
        self.mixer = pygame.mixer
        
        
    def load_sounds(self, data, folder = "sound", prefix = ""):
        for p, f in data.list_datas_as_files(folder):
            try:
                s = pygame.mixer.Sound(f)
                n = p.split(".")[0]
                if n.startswith(folder):
                    n = n[len(folder)+1:]
                self.sounds[prefix + n] = s
                #print "Loaded %s as '%s'" % (p, n)
            except Exception:
                print "Failed to load", p
        

    def get(self, n):
        try:
            return self.sounds[n]
        except Exception:
            print "No sound named %s !" % n
            s = pygame.mixer.Sound("")
            self.sounds[n] = s
            return s


    def play(self, n, loops=0, maxtime=0, fade_ms=0): #, store=False):
        r = self.get(n).play(loops, maxtime, fade_ms)
        #if store:
        #    pass
        return r

    def stop(self, n):
        self.get(n).stop()
        
    #def pause(self, n):
    #    self.get(n).pause()
    #    
    #def unpause(self, n):
    #    self.get(n).unpause()
        
    def fadeout(self, n, time):
        self.get(n).fadeout(time)


