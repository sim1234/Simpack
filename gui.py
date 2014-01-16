# coding: utf-8

import pygame
import random
import re
from .functions import tuc, key_name, invert_color



class CObj(object):
    def __init__(self):
        pass

    def blit(self, bit):
        pass

    def event(self, event):
        pass

class ClickArea(object):
    def __init__(self, (px, py, w, h)):
        self.px, self.py, self.w, self.h = (px, py, w, h)
        self.bd = [0,0,0,0,0,0,0,0,0,0]

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            px, py = event.pos # pygame.mouse.get_pos()
            if self.check_in(px, py):
                self.bd[event.button] = 1
                #print self.bd
        if event.type == pygame.MOUSEBUTTONUP:
            r = 0
            px, py = event.pos # pygame.mouse.get_pos()
            if self.check_in(px, py):
                if self.bd[event.button]:
                    r = event.button
            self.bd[event.button] = 0
            #self.bd = [0,0,0,0,0,0,0,0,0,0]
            return r

        return None

    def check_in(self, px, py):
        return self.px < px < self.px + self.w and self.py < py < self.py + self.h

    def get_rect(self):
        return (self.px, self.py, self.w, self.h)


class CLabel(CObj):
    def __init__(self, text, (px, py, w, h), fsize = 15, color = (0,0,0), bgcolor = (0,0,0,0)):
        CObj.__init__(self)
        self.px, self.py, self.w, self.h = (px, py, w, h)
        self.fsize = fsize
        self.color = color
        self.bgcolor = bgcolor
        self.set_text(text)

    def set_text(self, text):
        self.text = tuc(text) # text.decode('UTF-8')
        font = pygame.font.Font(pygame.font.match_font('doesNotExist, Arial'), self.fsize)
        fb = font.render(self.text, True, self.color, self.bgcolor)
        textRect = fb.get_rect()
        textRect.x = self.w/2-textRect.width/2
        textRect.y = self.h/2-textRect.height/2
        self.bit = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        if self.bgcolor:
            self.bit.fill(self.bgcolor)
        if text:
            self.bit.blit(fb, textRect)
        #pygame.draw.rect(self.bit, (255,255,255), (0, 0, self.w-1, self.h-1), 2)

    def blit(self, bit):
        CObj.blit(self, bit)
        textRect = self.bit.get_rect()
        textRect.x = self.px
        textRect.y = self.py
        bit.blit(self.bit, textRect)


class CButton(CLabel):
    def __init__(self, OnClick, text, (px, py, w, h), fsize = 15, color = (0,0,0), bgcolor = (0,0,0,0), color2 = (0,0,0), bgcolor2 = (0,0,0,0)):
        self.color2 = color2
        self.bgcolor2 = bgcolor2
        CLabel.__init__(self, text, (px, py, w, h), fsize, color, bgcolor)
        self.oc = OnClick
        self.ca = ClickArea((px, py, w, h))

    def event(self, event):
        CLabel.event(self, event)
        if self.ca.event(event) == 1:
            self.oc()

    def set_text(self, text):
        CLabel.set_text(self, text)
        self.text = tuc(text) # text.decode('UTF-8')
        font = pygame.font.Font(pygame.font.match_font('doesNotExist, Arial'), self.fsize)
        fb = font.render(self.text, True, self.color2, self.bgcolor2)
        textRect = fb.get_rect()
        textRect.x = self.w/2-textRect.width/2
        textRect.y = self.h/2-textRect.height/2
        self.bit2 = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        if self.bgcolor2:
            self.bit2.fill(self.bgcolor2)
        if text:
            self.bit2.blit(fb, textRect)
        #pygame.draw.rect(self.bit, (255,255,255), (0, 0, self.w-1, self.h-1), 2)

    def blit(self, bit):
        b = None
        if self.ca.check_in(*pygame.mouse.get_pos()):
            b = self.bit2
        else:
            b = self.bit
        CObj.blit(self, bit)
        textRect = self.bit.get_rect()
        textRect.x = self.px
        textRect.y = self.py
        bit.blit(b, textRect)


class CColorPick(CObj):
    SEQ = (0,64,128,192,255)
    def __init__(self, (px, py, w, h), color = None, bgcolor = (0,0,0,0)):
        CObj.__init__(self)
        self.px, self.py, self.w, self.h = (px, py, w, h)
        if not color:
            self.randomize_color()
        else:
            self.rc, self.gc, self.bc = (color[0] + 1) / 64, (color[1] + 1) / 64, (color[2] + 1) / 64
            self.updateclr()
        self.bgcolor = bgcolor
        mw = self.w / 8
        mh = self.h / 6
        self.csum = ClickArea((px + mw, py + mh, 6 * mw, 2 * mh))
        self.cr = ClickArea((px + mw, py + 3 * mh, 2 * mw, 2 * mh))
        self.cg = ClickArea((px + 3 * mw, py + 3 * mh, 2 * mw, 2 * mh))
        self.cb = ClickArea((px + 5 * mw, py + 3 * mh, 2 * mw, 2 * mh))

    def updateclr(self):
        self.r = self.SEQ[self.rc]
        self.g = self.SEQ[self.gc]
        self.b = self.SEQ[self.bc]

    def randomize_color(self):
        l = len(self.SEQ) - 1
        self.rc = random.randint(0, l)
        self.gc = random.randint(0, l)
        self.bc = random.randint(0, l)
        self.updateclr()

    def _norm(self, v):
        l = len(self.SEQ)
        while v >= l:
            v -= l
        while v < 0:
            v += l
        return v

    def event(self, event):
        CObj.event(self, event)
        if self.csum.event(event) == 1:
            self.randomize_color()
        r = self.cr.event(event)
        if r == 1:
            self.rc = self._norm(self.rc + 1)
            self.updateclr()
        elif r == 3:
            self.rc = self._norm(self.rc - 1)
            self.updateclr()
        r = self.cg.event(event)
        if r == 1:
            self.gc = self._norm(self.gc + 1)
            self.updateclr()
        elif r == 3:
            self.gc = self._norm(self.gc - 1)
            self.updateclr()
        r = self.cb.event(event)
        if r == 1:
            self.bc = self._norm(self.bc + 1)
            self.updateclr()
        elif r == 3:
            self.bc = self._norm(self.bc - 1)
            self.updateclr()


    def blit(self, bit):
        CObj.blit(self, bit)
        pygame.draw.rect(bit, self.get_color(), self.csum.get_rect(), 0)
        pygame.draw.rect(bit, (self.r,0,0), self.cr.get_rect(), 0)
        pygame.draw.rect(bit, (0,self.g,0), self.cg.get_rect(), 0)
        pygame.draw.rect(bit, (0,0,self.b), self.cb.get_rect(), 0)

    def get_color(self):
        return (self.r, self.g, self.b)


class CTextBox(CObj):
    def __init__(self, (px, py, w, h), text="", maxchars=None, allow_number=True, allow_letter=True, allow_special=True, fsize = 15, color = (0,0,0), bgcolor = (0,0,0,0), color2 = (0,0,0), bgcolor2 = (0,0,0,0)):
        CObj.__init__(self)
        self.px, self.py, self.w, self.h = px, py, w, h
        self.on = 1
        self.text = tuc(text) # text.decode('UTF-8')
        self.maxchars = maxchars
        #self.border = border
        self.color1 = color
        self.bgcolor1 = bgcolor
        self.color2 = color2
        self.bgcolor2 = bgcolor2
        self.text_size = fsize
        self.anumber = allow_number
        self.aletter = allow_letter
        self.aspecial = allow_special
        self.bit = pygame.Surface((self.w, self.h), flags=pygame.HWSURFACE)
        self.font = pygame.font.Font(pygame.font.match_font('doesNotExist, Arial'), self.text_size)
        self.e = None
        self.charw = 9
        self.selected = False
        self.ca = ClickArea((self.px, self.py, self.w, self.h))
        self.pos_ = (0, 0)
        self.updatebit()


    def event(self, event):
        CObj.event(self, event)
        r = self.ca.event(event)
        if r == 1:
            self.selected = True
            self.updatebit()
        elif r == 0:
            self.selected = False
            self.updatebit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    if self.selected:
                        self.text = tuc(self.text[:-1]) # self.text[:-1].decode('UTF-8')
                        self.updatebit()
            elif event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.selected = False
                self.updatebit()
            else:
                if self.selected:
                    if (self.anumber or not len(re.findall("\d", event.unicode))) and (self.aletter or not len(re.findall("[a-zA-Z]", event.unicode))) and (self.aspecial or len(re.findall("[0-9a-zA-Z]", event.unicode))):
                        if self.maxchars is None or len(self.text) < self.maxchars:
                            self.text = tuc(self.text + event.unicode) #.decode('UTF-8')
                            #self.text.decode('UTF-8')
                            #"".
                            #self.text.join(event.unicode.decode('UTF-8'))
                            self.updatebit()

    def blit(self, bit):
        CObj.blit(self, bit)
        bit.blit(self.bit, (self.px, self.py))
        if self.selected and pygame.time.get_ticks() % 1500 < 800:
            ren = self.font.render("|", 1, self.color2)
            bit.blit(ren, self.pos_)


    def updatebit(self):
        color = None
        if not self.selected:
            self.bit.fill(self.bgcolor1)
            color = self.color1
        else:
            self.bit.fill(self.bgcolor2)
            color = self.color2
        lt = 0
        while self.font.size(tuc(self.text[lt:] + "|"))[0] > self.w + 1:
            lt += 1
        ren = self.font.render(tuc(self.text[lt:]), 1, color)
        textRect = ren.get_rect()#topleft = (self.px, self.py))
        #textRect.x = self.w/2-textRect.width/2
        textRect.y = self.h/2-textRect.height/2
        self.pos_ = (self.px + textRect.width, self.py + textRect.y)
        self.bit.blit(ren, textRect)

    def get_text(self):
        return tuc(self.text)


class CPlayer(object):
    def __init__(self, idd, name, p_color, (px, py), num_ctrl = 2, keys=[], fsize = 15, color = (0,0,0), bgcolor = (0,0,0,0), color2 = (0,0,0), bgcolor2 = (0,0,0,0)):
        self.tryb = 0
        self.id = idd
        self.name = tuc(name)
        self.b = CTextBox((px, py, 100, 40), self.name, 20, 1, 1, 1, fsize, color, bgcolor, color2, bgcolor2)
        self.c = CColorPick((px + 120, py, 80, 40), color = p_color, bgcolor = bgcolor)
        self.ctrl = []
        self.keys = []
        for x in xrange(num_ctrl):
            k = ""
            try:
                k = int(keys[x])
            except (ValueError, TypeError, IndexError):
                self.keys.append(None)
            else:
                self.keys.append(k)
                k = key_name(k)
            self.ctrl.append(CButton(self.click, k, (px + 220 + 120 * x, py, 100, 40), fsize, color, bgcolor, color2, bgcolor2))



    def click(self):
        # TO DO
        self.tryb = 1
        self.ctrl[0].set_text("???")


    def event(self, event):
        self.b.event(event)
        self.c.event(event)
        for c in self.ctrl:
            c.event(event)
        if self.tryb:
            if event.type == pygame.KEYDOWN:
                if self.tryb and event.key != pygame.K_ESCAPE:
                    self.tryb += 1
                    self.keys[self.tryb - 2] = event.key
                    self.ctrl[self.tryb - 2].set_text(key_name(event.key))
                    if self.tryb <= len(self.ctrl):
                        self.ctrl[self.tryb - 1].set_text("???")
                    else:
                        self.tryb = 0

            elif event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                self.ctrl[self.tryb - 1].set_text(key_name(self.keys[self.tryb - 1]))
                self.tryb = 0
                #self.keys = [None for x in self.ctrl]
                #for c in self.ctrl:
                #    c.set_text("")

    def blit(self, bit):
        self.b.blit(bit)
        self.c.blit(bit)
        for c in self.ctrl:
            c.blit(bit)

    def get_state(self):
        return [self.id, self.b.get_text(), self.c.get_color()] + self.keys


class CShip(CObj):
    offset = (10,20)
    
    def __init__(self, OnClick, dictt, (px, py, w, h), fsize = 15, color = (0,0,0), bgcolor = (0,0,0,0), bgcolor2 = (255,255,255), bgcolor3 = (255,255,255)):
        self.px, self.py, self.w, self.h = px, py, w, h
        self.dictt = dictt
        self.text = dictt['name']
        self.ship = dictt['image']
        self.fsize = fsize
        self.mouseover = False
        self.selected = False
        self.clrs = [color, bgcolor, bgcolor2, bgcolor3]
        self.init_display()
        self.oc = OnClick
        self.ca = ClickArea((px, py, w, h))

    def init_display(self):
        self.bit1 = self._render_bit(self.clrs[0], self.clrs[1])
        self.bit2 = self._render_bit(self.clrs[0], self.clrs[2])
        self.bit3 = self._render_bit(self.clrs[0], self.clrs[3])


    def event(self, event):
        r = self.ca.event(event)
        if r == 1:
            #if self.selected:
            #    self.unselect()
            #else:
            self.oc(self.dictt)
            self.selected = True

        self.mouseover = self.ca.check_in(*pygame.mouse.get_pos())


    def unselect(self):
        self.selected = False

    def _render_bit(self, text_color, bg):
        font = pygame.font.Font(pygame.font.match_font('doesNotExist, Arial'), self.fsize)
        fb = font.render(self.text, True, text_color, bg)
        textRect = fb.get_rect()
        textRect.x = self.w/2-textRect.width/2
        textRect.y = 2
        bit = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        if bg:
            bit.fill(bg)
        bit.blit(fb, textRect)
        bit.blit(self.ship, self.offset)
        return bit


    def blit(self, bit):
        CObj.blit(self, bit)
        r = self.bit1.get_rect()
        r.x, r.y = self.px, self.py
        if self.mouseover:
            bit.blit(self.bit2, r)
        elif self.selected:
            bit.blit(self.bit3, r)
        else:
            bit.blit(self.bit1, r)
            
class CMap(CShip):
    offset = (0,20)
    
    def __init__(self, OnClick, dictt, (px, py, w, h), fsize = 15, color = (0,0,0), bgcolor = (0,0,0,0), bgcolor2 = (255,255,255), bgcolor3 = (255,255,255)):
        CShip.__init__(self, OnClick, dictt, (px, py, w, h), fsize, color, bgcolor, bgcolor2, bgcolor3)
        self.ship = pygame.transform.scale(dictt['image'], (100, 100))
        self.init_display()

class PlayerUI(CObj):
    text_h = 30
    margin = 2
    c1 = (255,100,100)
    c2 = (100,0,0)
    c3 = (255,0,0)
    def __init__(self, (px, py, w, h), playername, color, ship):
        #CLabel.__init__(self, playername, (px, py, w, 30), 15, (255,255,255), (100,100,100))
        self.px, self.py, self.w, self.h = px, py, w, h
        self.name = CLabel(playername, (px, py, w, self.text_h), 15, invert_color(color), color)
        self.set_name = self.name.set_text
        self.ship = ship
    
    def blit(self, bit):
        mxh = self.h - self.text_h - 2 * self.margin
        h = min((mxh * self.ship.hp) / self.ship.maxhp, mxh)
        h2 = min(mxh - h, mxh)
        pygame.draw.rect(bit, self.c1, (self.px, self.py + self.text_h, self.w, self.h - self.text_h))
        if h2 > 0:
            pygame.draw.rect(bit, self.c2, (self.px + self.margin, self.py + self.margin + self.text_h, self.w - 2 * self.margin, h2))
        if h > 0:
            pygame.draw.rect(bit, self.c3, (self.px + self.margin, self.py + self.h - h - self.margin, self.w - 2 * self.margin, h))
        self.name.blit(bit)
        
    
        
