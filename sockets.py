# coding: utf-8


import socket
import time
import bz2
import errno
#import select
#import cPickle as pickle
import collections
from simpack.functions import fill_to
from simpack.request import WorkManager



def localhost():
    return ""
    #return socket.gethostbyname(socket.gethostname())


def try_blocking(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except socket.error as e:
        if e.errno == errno.EWOULDBLOCK: # NON-blocking
            return
        raise


class Message(object):
    _typ_len = 10
    def make_typ(self, typ):
        return fill_to(typ, Message._typ_len, "-")
    
    def __init__(self, typ, msg, compressed = None):
        self.typ = self.make_typ(typ)
        self.msg = msg
        self._compressed = bool(compressed)
        if compressed is None and len(msg) > 500:
            self._compressed = True
    
    @staticmethod
    def from_str(msg):
        e = Message._typ_len + 1
        c = msg[0] == "1"
        t = msg[1:e]
        m = msg[e:]
        if c:
            m = bz2.decompress(m)
        return Message(t, m, c)
    
    def is_type(self, typ):
        return self.typ == self.make_typ(typ)
    
    def __str__(self):
        m, c = self.msg, "0"
        if self._compressed:
            m, c = bz2.compress(m), "1"
        return "%s%s%s" % (c, self.make_typ(self.typ), m)

class BaseProtocol(object):
    #pattern = re.compile(r"(\d+);(.*)")
    
    def __init__(self, client):
        self.client = client

    def _get_packet(self):
        try:
            l, d = self.client.data_in.split(";", 1)
            l = int(l)
            if l <= len(d):
                self.client.data_in = d[l:]
                return d[:l]
        except Exception as e:
            pass
        
    def send(self, msg, *args, **kwargs):
        msg = str(msg)
        self.client.data_out += "%d;%s" % (len(msg), msg)
        
    def recive(self):
        msg = self._get_packet()
        while msg is not None:
            msg = self.make_message(msg)
            if msg is not None:
                yield msg
            msg = self._get_packet()
        
    def make_message(self, msg):
        return str(msg)



class Protocol(BaseProtocol):
    msg = Message
    
    def send(self, typ, msg, compressed = None):
        msg = self.msg(typ, msg, compressed)
        BaseProtocol.send(self, msg)
        
        
    def make_message(self, msg):
        msg = BaseProtocol.make_message(self, msg)
        try:
            return self.msg.from_str(msg)
        except IndexError: 
            pass
        print "Bad message: '%s'." % msg

"""
class ExtendedProtocol(Protocol):
    reserved = ("_P1", "_P2")
    
    def __init__(self, client):
        Protocol.__init__(self, client)
        self.ping_ = 0
    
    def make_message(self, msg):
        msg = Protocol.make_message(self, msg)
        if msg.is_type(self.reserved[0]):
            self.send(self.reserved[1], msg.msg, False)
        elif msg.is_type(self.reserved[1]):
            self.ping_ = time.time() - float(msg.msg)
            # print "Ping: %f ms" % (self.ping_ * 1000)
        else:
            return msg
    
    def ping(self):
        self.send(self.reserved[0], time.time(), False)
        return self.ping_
        
"""

class LanSearch(WorkManager):
    def __init__(self, *ports):
        WorkManager.__init__(self, 250)
        self.ports = ports
        
    def start(self):
        l = socket.gethostbyname_ex(socket.getfqdn())[2]
        self.lans = map(lambda x: x.rsplit(".", 1)[0] + ".%d", l)
        WorkManager.start(self)
        
    def get_work(self):
        for p in self.ports:
            yield  "127.0.0.1", p
        for l in self.lans:
            for x in xrange(256):
                for p in self.ports:
                    yield l % x, p
        
    def result(self, host, port):
        print "%s:%d" % (host, port)
        
    def work(self, host, port):
        try:
            sock = socket.create_connection((host, port), 4)
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            return  host, port
        except socket.error:
            pass
            #print "%s:%d" % (host, port), "nah"
        
        

    

        

class Client(object):
    
    def __init__(self, sock = None, protocol = Protocol, timeout = 10):
        self.max_data_recv = 2**12
        
        self.running, self.host, self.port = False, None, None
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
            self.running = True
            self.host, self.port = self.sock.getpeername()
        self.sock.setblocking(False)
        self.fileno = self.sock.fileno
        
        self.data_in = ""
        self.data_out = ""
        self.messages = collections.deque()
        
        self.protocol = protocol(self)
        
        self.timeout = timeout
        self.lastmsg = time.clock()
        
        #if broken is None:
        #    def b(sock, exc):
        #        print "Socket error: '%s'" % exc
        #        sock.close()
        #    broken = b
        #self.broken = broken
            
        
    def connect(self, host, port):
        self.host, self.port = host, port
        try:
            if self.running:
                raise Exception("Socket already connected")
            #self.sock.connect((host, port))
            self.sock = socket.create_connection((host, port), self.timeout)
            self.running = True
            print "Connected to " + str(host) + ":" + str(port) + "."
            self.sock.setblocking(False)
            #return 0
        except socket.error as e:
            print "Couldn't connect to " + str(host) + ":" + str(port)+ ".", e
            self.close()
            raise
            #return 1
        
        
    def send(self, *args, **kwargs):
        self.protocol.send(*args, **kwargs)
    
    
    def get_messages(self):
        while len(self.messages):
            #yield self.messages.pop(0)
            yield self.messages.popleft()
            

    def processIO(self):
        if not self.running:
            # raise Exception("Socket not connected")
            return
        #try:
        try_blocking(self._recv)
        try_blocking(self._send)
        #except socket.error as e:
        #    self.broken(self, e)
        if self.lastmsg + self.timeout < time.clock():
            raise socket.error("Socket Timeout")
        
        for msg in self.protocol.recive():
            self.messages.append(msg)
        
    def _send(self):
        e = self.sock.send(self.data_out)
        if e:
            #print "> `%s`" % self.data_out[:e]
            self.data_out = self.data_out[e:]
        
        
    def _recv(self):
        r = self.sock.recv(self.max_data_recv)
        if r:
            #print "< `%s`" % r
            self.data_in += r  
            self.lastmsg = time.clock()
        else:
            raise socket.error("Connection closed by remote host")


    def close(self):
        self.running = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        try:
            self.sock.close()
        except socket.error:
            pass
        print "Socket on %s:%s closed" % (self.host, self.port)
        


         
    
class Server(object): 
    def __init__(self, port, protocol = Protocol, *args, **kwargs): 
        self._host = ""
        self._port = int(port)
        self._server = None
        self._clients = []
        self._running = False               
        self._protocol = protocol
               
        self.init(*args, **kwargs) # user init
 
    
    def init(self):
        pass
    
    def new_client(self, client):
        pass
    
    def broken_client(self, client, exc):
        pass
    
    def message(self, msg, client):
        pass
    
    def tick(self):
        pass
    
    def send_all(self, *args, **kwargs):
        for s in self._clients:
            s.send(*args, **kwargs)
 
    def stop(self):
        self._running = False
 
 
    def _open_socket(self):
        try:
            if self._running:
                raise Exception("Server already running")
            self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server.bind((self._host, self._port)) 
            self._server.listen(5)
            self._server.setblocking(False)
            self._running = True
            print "Server started on:"
            for a in ["127.0.0.1"] + socket.gethostbyname_ex(socket.getfqdn())[2]:
                print str(a) + ":" + str(self._port)
        except socket.error as e:
            if self._server: 
                self._server.close()
            print "Couldn't open socket.", e
            self._running = False
            raise
        
    def _broken_client(self, client, exc):
        try:
            self._clients.pop(self._clients.index(client))
        except ValueError:
            pass
        client.close()
        print "Client %s disconnected due to error: '%s'." % (client.host, exc)
        self.broken_client(client, exc)
 
    
    def _main_loop(self):
        try:
            sock, adr = self._server.accept() # Accept connection
            c = Client(sock, self._protocol)
            self._clients.append(c)
            print "%s:%s connected." % (adr[0], adr[1])
            self.new_client(c) # Handle new clients
        except socket.error as e:
            if e.errno != errno.EWOULDBLOCK:
                pass
                #raise
        
        self.tick() # User loop  
        
        for s in self._clients:
            try:
                s.processIO() # Handle clients I/O
                for m in s.get_messages():
                    self.message(m, s) # Handle messages 
            except socket.error as e:
                self._broken_client(s, e) # Handle broken clients
                    
 
 
    def main_loop(self): 
        self._open_socket()
        while self._running:
            self._main_loop()

        #self._server.shutdown(socket.SHUT_RDWR)
        self._server.close()
        for c in self._clients:
            c.close()

        print "Server exited."
    
    
        
 
 



        
        
