#coding: utf-8;

import urllib2
import urllib
import Cookie
#import collections
from simpack.functions import SubProces     
                
class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        #code, msg, hdrs = response.code, response.msg, response.info()
        response.info()
        return response
    https_response = http_response

cookieprocessor = urllib2.HTTPCookieProcessor()
opener = urllib2.build_opener(NoRedirection, cookieprocessor)
urllib2.install_opener(opener)


class CookieHandler(object):
    def __init__(self, url = ""):
        self.c = Cookie.SimpleCookie()
        self.url = url
    
    def log_in(self, url = "", data = None, headers = None):
        if not url:
            url = self.url
        if not data:
            data = {}
        data = urllib.urlencode(data)
        rq = None
        if headers:
            rq = urllib2.Request(url, data, headers)
        else:
            rq = urllib2.Request(url, data)

        r = urllib2.urlopen(rq)
        i = r.info()
        #self.c = Cookie.SimpleCookie()
        try:
            self.c.load(i['set-cookie'])
        except:
            pass
        return r

    def get(self, url = "", data = None, headers = None, add_cookies = True):
        if not url:
            url = self.url
        if not headers:
            headers = {}
            
        rc = ""
        for x in self.c:
            rc += self.c[x].key + "=" + self.c[x].value + "; "
        headers.update({"Cookie": rc})
            
        rq = None
        if data:
            data = urllib.urlencode(data)
            rq = urllib2.Request(url, data, headers)
        else:
            rq = urllib2.Request(url, headers = headers)

        r = urllib2.urlopen(rq)
        if add_cookies:
            i = r.info()
            try:
                self.c.load(i['set-cookie'])
            except:
                pass
        return r

    def __call__(self, url = "", data = None, headers = None, add_cookies = False):
        return self.get(url, data, headers, add_cookies)
        
    

class WorkManager(object):
    def __init__(self, max_workers = 4):
        self.workers = [] # collections.deque()
        self.max_workers = max_workers
        self._work = None
        self.status = 0
        
        
    def main_loop(self):
        self.start()
        while self.status:
            self.processIO()
            
    def start(self):
        self.status = 2        
        self._work = self.get_work()
        
    def stop(self):
        self.status = 0
        while len(self.workers):
            self.workers.pop()
        
    def processIO(self):
        while len(self.workers) < self.max_workers and self.status == 2:
            try:
                self.workers.append(SubProces(self.work, 0, 0, *self._work.next()))
            except StopIteration:
                self.status = 1
        x = 0
        while x < len(self.workers):
            if not self.workers[x].running:
                r = self.workers.pop(x).result
                if r is not None:
                    self.result(*r)
            else:
                x += 1
        if self.status == 1 and len(self.workers) == 0:
            self.status = 0
            self.end()
    
    def get_work(self):
        raise StopIteration
        yield
    
    def work(self, *a):
        pass
    
    def result(self, *a):
        print a 
        
    def end(self):
        pass
    
