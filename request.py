#coding: utf-8;

import urllib2
import urllib
import Cookie
import time
#import random
import threading
#from .functions import between

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
        
    
        
