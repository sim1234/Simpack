# coding: utf-8


import os
import pygame
import StringIO
import zipfile
from simpack.functions import load_config, make_config


CONFIG = {
          "top" : "",
          "archive" : "data.zip",
          "datas": {}
          }


class NormalProvider(object):
    def __init__(self, config):
        self.configure(config['top'], config['datas'])

    def configure(self, top, datas):
        self.top = top # os.path.abspath(top)
        self.datas = datas

    def join(self, *src):
        return os.path.join(self.top, *src)

    def get_name(self, folder, *names):
        return self.join(self.datas[folder], *names)

    def open(self, folder, *names):
        return self.raw_open(self.get_name(folder, *names))

    def raw_open(self, path, mode="rb"):
        return open(path, mode)

    def get_content(self, folder, *names):
        return self.open(folder, *names).read()

    def list_datas(self, folder, *names):
        n = self.get_name(folder, *names)
        for p in os.listdir(n):
            p = os.path.join(n,p)
            if os.path.isfile(p):
                yield p

    def list_datas_as_files(self, folder, *names):
        for n in self.list_datas(folder, *names):
            yield n, self.raw_open(n)

    def load_image(self, folder, *names):
        n = self.get_name(folder, *names)
        return pygame.image.load(self.raw_open(n), n)

    def load_config(self, folder, *names):
        return load_config(self.get_content(folder, *names))
    
    def load_local(self, mode = "rb", default = "", *names):
        n = self.join(*names)
        try:
            return open(n, mode)
        except IOError:
            f = open(n, "wb")
            f.write(default)
            f.close()
            return open(n, mode)
            


class FrozenProvider(NormalProvider):
    def __init__(self, config):
        self.configure(config['archive'], config['datas'])

    def configure(self, archive, datas):
        self.archive = zipfile.ZipFile(archive)
        self.datas = datas
        self.top = ""

    def join(self, *src):
        return NormalProvider.join(self, *src).replace("\\", "/")

    def raw_open(self, path, mode="rb"):
        return StringIO.StringIO(self.archive.open(path).read())

    def get_content(self, folder, *names): # Tylko w celach optymalizacyjnych
        return self.archive.open(self.get_name(folder, *names)).read()

    def list_datas(self, folder, *names):
        path = self.get_name(folder, *names)
        for p in self.archive.namelist():
            if p.startswith(path) and not p.endswith("/"):
                yield p




#provider = NormalProvider(PYSHEEPS_CONFIG)
#if hasattr(sys, "frozen"):
#    provider = FrozenProvider(PYSHEEPS_CONFIG)



def compress_datas(config = None, dist_dir="dist"):
    if config is None:
        config = CONFIG
    if not os.path.exists(dist_dir):
        os.mkdir(dist_dir)
    a = os.path.join(dist_dir, config["archive"])
    print "Compressing datas to", a
    z = zipfile.ZipFile(a, "w")
    def func(arg, dirname, fnames):
        for f in fnames:
            p = os.path.join(arg, dirname, f)
            print "   Compressing", p
            z.write(p, p)

    for p in config["datas"].values():
        os.path.walk(p, func, "")

    print "Archive complete!"







