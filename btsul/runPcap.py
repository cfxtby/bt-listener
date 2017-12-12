#! /usr/bin/env python2
# -*- coding:utf-8 -*-
# pynids Example
# $Id: Example,v 1.3 2005/01/27 04:53:45 mjp Exp $

import nids
import filter


import threading,ipTh
from my_ac import *
import socket

class runPcap(threading.Thread):
    def __init__(self, signal):
        threading.Thread.__init__(self)
        self.signal = signal
        self.cnt=0

    def initial(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('',state.port))
        self.s.listen(5)
        self.sock, addr = self.s.accept()
        print addr

    end_states = (nids.NIDS_CLOSE, nids.NIDS_TIMEOUT, nids.NIDS_RESET)

    def getTheIPPORT(self, addr):
        (src, dst) = addr
        if src[0] == state.localhost:
            return dst
        else:
            return src

    """
        def handleUtp(self,addrs, payload, pkt):
            self.cnt+=1
            if self.cnt==9425:
                print self.cnt
            if dealUDP(addrs,payload,ac):
                state.ls_pro.append((self.getTheIPPORT(addrs),1))
            #以上为将传入的udp加入到了utp流中
            #下一步是要将utp流中的数据进行取出进行处理
    """

    def handleTcpStream(self, tcp):
        state.isChanged = False
        #print "tcp:", tcp.addr
        if tcp.nids_state == nids.NIDS_JUST_EST:
            # new to us, but do we care?
            tcp.client.collect = 1
            tcp.server.collect = 1
        elif tcp.nids_state == nids.NIDS_DATA:
            b = filter.dealMid(tcp, state.dic_tcp, ac)
            if b:
                state.ls_pro.append((self.getTheIPPORT(tcp.addr),'tcp'))
                state.isChanged=True
                self.signal.set()
                print "hit:",tcp.addr,"hash info:",state.dic_tcp[tcp.addr][3]
        elif tcp.nids_state in self.end_states:
            filter.dealEnd(tcp, state.dic_tcp, ac)


        rev=ipTh.ipRevTh()
        rev.rev()
        if state.isChanged:
            self.send()

    def send(self):
        ls=[]
        for k in state.dic_tcp:
            ls.append(k)
        s = str(ls)
        n = len(s)
        s = chr(n % 256) + s
        s = chr(n / 256) + s
        self.sock.send(s)

        s = str(state.ls_pro)
        n = len(s)
        s = chr(n % 256) + s
        s = chr(n / 256) + s
        self.sock.send(s)

        s = str(state.ls_rem)
        n = len(s)
        s = chr(n % 256) + s
        s = chr(n / 256) + s
        self.sock.send(s)

    def main(self):
        #nids.param("filename", "bittorrent.pcap")
        nids.chksum_ctl([('0.0.0.0/0', False)])  # disable checksumming
        # nids.register_udp()
        nids.init()
        nids.register_tcp(self.handleTcpStream)
        #nids.register_udp(self.handleUtp)

        # Loop forever (network device), or until EOF (pcap file)
        # Note that an exception in the callback will break the loop!

        nids.run()

    def run(self):
        self.main()

if __name__ == '__main__':
    runPcap(threading.Event()).main()
