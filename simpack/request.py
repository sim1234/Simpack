#coding: utf-8;

import urllib2
import urllib
import Cookie
import HTMLParser
from cookielib import CookieJar
from _MPH import MultipartPostHandler


from simpack.functions import SubProces, try_decode  

                
class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        #code, msg, hdrs = response.code, response.msg, response.info()
        response.info()
        return response
    https_response = http_response


class CookieHandler(object):
    def __init__(self, url = ""):
        self._cookies = CookieJar()
        self.processors = (urllib2.HTTPCookieProcessor(self._cookies), NoRedirection, MultipartPostHandler)
        self.url = url
        self.clear(url)

    def clear(self, url = ""):
        self.cookies = Cookie.SimpleCookie()
        if url:
            self.url = url

    def build_cookies(self):
        rc = ""
        for x in self.cookies:
            rc += self.cookies[x].key + "=" + self.cookies[x].value + "; "
        return ("Cookie", rc)
        

    def get(self, url = "", data = None, headers = (), add_cookies = True):
        if not url:
            url = self.url
        
        opener = urllib2.build_opener(*self.processors)
        opener.addheaders.append(self.build_cookies())
        for h in headers:
            opener.addheaders.append(h)
        
        r = opener.open(url, data)
        
        if add_cookies:
            i = r.info()
            try:
                self.cookies.load(i['set-cookie'])
            except:
                pass
        return r  
    

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
        
    def get_worker(self, work, data):
        return SubProces(work, 0, 0, False, *data)
    
    
    def processIO(self):
        while len(self.workers) < self.max_workers and self.status == 2:
            try:
                worker = self.get_worker(self.work, self._work.next())
                self.workers.append(worker)
            except StopIteration:
                self.status = 1
        x = 0
        while x < len(self.workers):
            if not self.workers[x].is_running():
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
    
    
    
class HTMlTag(object):
    indent = "  "
    
    def __init__(self, name = "", kwargs = {}):
        self.sub = []
        self.name = name
        self.kwargs = kwargs
    
    def __str__(self,):
        r = "<%s" % self.name
        for k, v in self.kwargs.iteritems():
            r += ' %s="%s"' % (k, v)
        r += ">"
        if self.sub:
            r += "\n"
        for c in self.sub:
            r += self.indent + c.__str__().replace("\n", "\n" + self.indent) + "\n"
        r += "</%s>" % self.name
        return r
    
    def __repr__(self):
        #return 'HTMLTag("%s", "%s", %s)' % (self.name, self.data, self.kwargs)
        return 'HTMLTag("%s")' % self.name
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.sub[key]
        else:
            l = []
            for t in self.sub:
                if t.name == key:
                    l.append(t)
            return l
    
    def search(self, name):
        for t in self.sub:
            if t.name == name:
                yield t
            for tt in t.search(name):
                yield tt
                
    def append(self, tag):
        self.sub.append(tag)
    
    
class HTMLText(HTMlTag):
    def __init__(self, data):
        HTMlTag.__init__(self, "Text")
        self.data = data
    
    def __repr__(self):
        return 'HTMLText("%s")' % self.data
    
    def __str__(self):
        return self.data
    
    def append(self, tag):
        pass
        
    
class MyParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.stack = []
        self.top = []
    
    def handle_starttag(self, tag, attrs):
        t = HTMlTag(tag, dict(attrs))
        if len(self.stack):
            self.stack[-1].append(t)
        else:
            self.top.append(t)
        self.stack.append(t)
        #print "<%s>" % tag
        
    def handle_endtag(self, tag):
        if len(self.stack):
            lt = self.stack.pop(-1)
            if lt.name != tag: # Try to repair broken html
                if len(self.stack) and self.stack[-1].name == tag:
                    self.stack.pop(-1)
                self.stack.append(lt)
                #raise HTMLParser.HTMLParseError("Closing tag '%s' but tag '%s' is not closed" % (tag, lt.name), self.getpos())
        #print "</%s>" % tag
        
    def handle_data(self, data):
        if len(self.stack):
            t = HTMLText(data)
            self.stack[-1].append(t)




def get_forms(data):
    m = MyParser()
    m.feed(data)
    for m in m.top[0].search("form"):
        data = {}
        for i in m.search("input"):
            n = i.kwargs.get('name', None)
            v = i.kwargs.get('value', '')
            if n:
                data[n] = v
        yield m.kwargs.get('action', ''), m.kwargs.get('name', None), data



if __name__ == "__main__":
    #m = MyParser()
    #m.feed('<html a="b"><head><title>Test</title></head><body>ASDF<h1>Parse me!</h1><h1>Parse me 2!</h1><h1>Parse me 3!<h1>Parse me 4!</h1>Parse me 5!</h1></body></html>')
    #print m.top[0]
    #print m.top[0][1]["h1"]
    #print list(m.top[0].search("h1"))
    h = CookieHandler("http://thepiratebay.org/")
    for url, n, data in get_forms(try_decode(h.get().read())):
        print url, n, data


