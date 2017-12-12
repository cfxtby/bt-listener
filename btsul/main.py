#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket,fcntl,struct
from runPcap import *
from ipTh import *
import gui,multiprocessing
import socket
""""
四个线程。
一，进行捕包处理；
二，对于进行防火墙配置，等待线程一通知，每次通知就对于ip进行封锁；
三，对于已经封锁的ip进行解封，每五分钟执行一次，因此每个ip封锁时间是5-10分钟；
四，界面展示；
"""

class rev1(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def setPip(self,pip):
        self.pip = pip
    def setSig(self,pip):
        self.sig = pip

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1',9998))
        s.listen(5)
        sock, addr = s.accept()
        print addr
        while True:
            self.sig.clear()
            get = sock.recv()
            print "socket:", get
            if get=="open":
                state.start=True
            elif get=="stop":
                state.start=False
            elif get=="close":
                state.close=True
            else:
                print str(state.dic_tcp)
                sock.send(str(state.dic_tcp))
                sock.send(str(state.ls_pro))
                sock.send(str(state.ls_rem))
        """
        while True:
            print "wait"
            get=self.pip.recv()
            print type(get)
            if get=="open":
                state.start=True
            elif get=="stop":
                state.start=False
            elif get=="close":
                state.close=True
            else:
                print str(state.dic_tcp)
                self.pip.send(str(state.dic_tcp))
                self.pip.send(str(state.ls_pro))
                self.pip.send(str(state.ls_rem))
"""


def get_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])


def func1(pp):
    g=gui.gui(pip=pp)
    g.run()

def func2(pp):

    rev=rev1()
    rev.setPip(pp)
    rev.setPriority(threading.Thread.MAX_PRIORITY);
    rev.start()


    state.localhost = get_ip("enp2s0")
    sig = threading.Event()
    rejTh = ipAddTh(sig)
    rejTh.setPriority(threading.Thread.NORM_PRIORITY);
    rejTh.start()

    revTh = ipRevTh()
    revTh.setPriority(threading.Thread.NORM_PRIORITY);
    revTh.start()

    runTh = runPcap(sig)
    runTh.setPriority(threading.Thread.MIN_PRIORITY);
    print "runpcap"
    runTh.start()



def begin():
    pp = multiprocessing.Pipe(duplex=True)
    p1 = multiprocessing.Process(target=func1, args=(pp[0],))
    #p2 = multiprocessing.Process(target=func2, args=(pp[1],))
    p1.start()
    p1.join()
    func2(pp[1])

    #p2.start()

    #p2.join()


if __name__=="__main__":
    begin()


    """
    state.localhost=get_ip("enp2s0")

    sig = threading.Event()

    g=gui.gui()
    g.start()

    rejTh=ipAddTh(sig)
    rejTh.start()

    revTh=ipRevTh()
    revTh.start()
    runTh=runPcap(sig)
    print "runpcap"
    runTh.run()"""