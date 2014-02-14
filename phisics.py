# coding:utf-8

import time
import math
import pygame

def add_t(*tabless):
        return map(sum, zip(*tabless))

def mul_t(table, number = 1.0):
    return map(lambda x: x*number, table)


def iterate_over_PhisicsObjects(lista):
    x = 0
    while x < len(lista):
        o = lista[x]
        if o:
            x += 1
            yield o
        else:
            lista.pop(x)



class TimeManager(object):
    def __init__(self, time_quant = 0.01, *functions):
        self.time_quant = time_quant
        self.functions = list(functions)
        self.unpause()

    def register_function(self, function, *args, **kwargs):
        self.functions.append((function, args, kwargs))

    def pause(self):
        self.paused = True

    def unpause(self):
        self.time = time.clock()
        self.paused = False

    def tick(self):
        if not self.paused:
            new_time = time.clock()
            while self.time < new_time:
                self.time += self.time_quant
                for fn, a, kw in self.functions:
                    fn(*a, **kw)



class PhisicsManager(object):
    def __init__(self, time_quant = 0.01, *objects):
        self.objects = [list(objects), ]
        self.forces = []
        self.time = TimeManager(time_quant)
        self.time.register_function(self.process_objects)
        self.tick = self.time.tick
        self.pause = self.time.pause
        self.unpause = self.time.unpause
        self.register_function = self.time.register_function

    def register_object(self, obj):
        self.objects[0].append(obj)
        #obj._phisics_managers.append(self)

    #def _register_where_similar_object(self, obj, similar_object):
    #    for l in self.objects:
    #        if similar_object in l:
    #           l.append(obj)
    #            obj._phisics_managers.append(self)
    #            return 1
    #    self.register_object(obj)
    #    return 0


    def register_list(self, l):
        self.objects.append(l)
        #for obj in l:
        #    obj._phisics_managers.append(self)

    def register_forces(self, *forces):
        self.forces.extend(forces)

    def process_objects(self):
        for lista in self.objects:
            for obj in iterate_over_PhisicsObjects(lista):
                obj.apply_forces(self.time.time_quant, *self.forces)
                obj.tick(self.time.time_quant)
                #for sobj in obj.get_subobjects():
                #    sobj.apply_forces(self.time.time_quant, *self.forces)
                #    sobj.tick(self.time.time_quant)

    def truncate_objects(self):
        for lista in self.objects:
            for obj in lista:
                obj.delete()
        self.objects = []

    def truncate(self):
        self.truncate_objects()
        for f in self.forces:
            f.delete()
        self.forces = []

    def clean_up(self, d = False):
        if d:
            for lista in self.objects:
                for obj in lista:
                    obj.delete()
        for lista in self.objects:
            for obj in iterate_over_PhisicsObjects(lista):
                pass


class PhisicsObject(object):
    def __new__(cls, *args, **kwargs):
        obj = super(PhisicsObject, cls).__new__(cls, *args, **kwargs)
        obj._exists = True
        #obj._phisics_managers = []
        return obj

    def __init__(self):
        self._exists = True

    def tick(self, time):
        pass

    def delete(self):
        self._exists = False

    def register_to(self, *managers):
        for m in managers:
            m.register_object(self)
        return self

    #def get_subobjects(self):
    #    return ()

    #def new_obj(self, typ = None, *args, **kwargs):
    #    if typ is None:
    #        typ = type(self)
    #    obj = typ(*args, **kwargs)
    #    for phm in self._phisics_managers:
    #        phm._register_where_similar_object(self, obj, self)
    #    return obj

    def __nonzero__(self):
        return self._exists
    
    @staticmethod
    def if_alive(f):
        def ff(self, *args, **kwargs):
            if self._exists:
                return f(self, *args, **kwargs)
        return ff


class Acceleration(PhisicsObject):
    def __init__(self, fx, fy):
        self.fx = fx
        self.fy = fy

    def change_to(self, fx, fy):
        self.fx = fx
        self.fy = fy

    def change_by(self, dx, dy):
        self.fx += dx
        self.fy += dy

    def __str__(self):
        return "Acceleration(%f, %f)" % (self.fx, self.fy)


class PhisicalObject(PhisicsObject):
    def __init__(self, px=0, py=0, vx=0, vy=0):
        self.px = px
        self.py = py
        self.vx = vx
        self.vy = vy

    def tick(self, time):
        self.px += self.vx * time
        self.py += self.vy * time

    def apply_forces(self, time, *forces):
        for f in forces:
            self.vx += f.fx * time
            self.vy += f.fy * time

    def detach(self, typ = None, dx = 0, dy = 0, dvx = 0, dvy = 0, *args, **kwargs):
        if typ is None:
            typ = type(self)
        return typ(self.px + dx, self.py + dy, self.vx + dvx, self.vy + dvy, *args, **kwargs)

    def __str__(self):
        return "PhisicalObject in (%f, %f) with speed (%f, %f)" % (self.px, self.py, self.vx, self.vy)


class TexturedObject(PhisicalObject):
    def __init__(self, px, py, vx, vy, angle, image):
        PhisicalObject.__init__(self, px, py, vx, vy)
        self.image = image
        self.angle = angle
        self._image = pygame.Surface(image.get_size(), flags=pygame.HWSURFACE | pygame.SRCALPHA)
        self._image.blit(image, (0,0))
        self.make_image()

    def make_image(self):
        self.image = pygame.transform.rotate(self._image, math.degrees(self.angle))
        self.mask = pygame.mask.from_surface(self.image)
        self.image_w, self.image_h = self.image.get_size()

    def get_image_pos(self):
        return int(self.px - self.image_w / 2.0), int(self.py - self.image_h / 2.0)


    def collision_point_gen(self, mask, x = 10):
        pkt = mask.overlap(self.mask, self.get_image_pos())
        while pkt and x:
            yield pkt
            x -= 1
            pkt = mask.overlap(self.mask, self.get_image_pos())


    def collide_at(self, px, py):
        a = math.atan2(py, px)
        fx, fy = math.cos(a), math.sin(a)
        self.px -= fx
        self.py -= fy
        self.vx -= fx
        self.vy -= fy
        self.vx *= abs(fx) - 0.1
        self.vy *= abs(fy) - 0.1
        return math.hypot(self.vx, self.vy)

    def collide_bullets(self, bullets):
        px, py = self.get_image_pos()
        for b in bullets:
            cp = (int(b.px - px), int(b.py - py))
            try:
                if self.mask.get_at(cp):
                    b.delete()
                    yield b
            except IndexError:
                pass

    def collide_TO(self, TO):
        spx, spy = TO.get_image_pos()
        px, py = self.get_image_pos()
        pkt = self.mask.overlap(TO.mask, (spx - px, spy - py))
        if pkt:
            pxx, pyy = pkt[0] - self.image_w / 2, pkt[1] - self.image_h / 2
            vw = math.hypot(self.vx - TO.vx, self.vy - TO.vy)
            self.collide_at(pxx, pyy)
            self.crash((pxx, pyy), vw)
            pxx, pyy = pxx + px - spx, pyy + py - spy
            #print pkt, pxx, pyy
            TO.collide_at(pxx, pyy)
            self.crash((pxx, pyy), vw)
            return vw

    def boom(self, cp, b):
        pass

    def crash(self, cp, v):
        pass

    def my_detach(self, typ, dx, dy, dvx, dvy, *args, **kwargs):
        if typ is None:
            typ = type(self)
        p, pa = math.hypot(dx, dy), math.atan2(dy, dx) - self.angle
        v, va = math.hypot(dvx, dvy), math.atan2(dvy, dvx) - self.angle
        dx, dy = p * math.cos(pa), p * math.sin(pa)
        dvx, dvy = v * math.cos(va), v * math.sin(va)
        return typ(self.px + dx, self.py + dy, self.vx + dvx, self.vy + dvy, *args, **kwargs)

    def place_at(self, px, py, vx = 0, vy = 0, angle = 0):
        self.px, self.py = px, py
        self.vx, self.vy = vx, vy
        self.angle = angle
        self.make_image()

    def draw(self, bufor):
        bufor.blit(self.image, self.get_image_pos())



