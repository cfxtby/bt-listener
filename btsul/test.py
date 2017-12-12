#! /usr/bin/env python2
#-*- coding:utf-8 -*-
# pynids Example
# $Id: Example,v 1.3 2005/01/27 04:53:45 mjp Exp $

import nids
import filter
import threading
import state

class runPcap(threading.Thread):

    def __init__(self,signal):
        self.signal=signal
    
    end_states = (nids.NIDS_CLOSE, nids.NIDS_TIMEOUT, nids.NIDS_RESET)
    def getTheIPPORT(self,addr):
        (src,dst)=addr
        if src[0]==state.localhost:
            return src
        else:
            return dst

    def handleTcpStream(self,tcp):
        if tcp.nids_state == nids.NIDS_JUST_EST:
            # new to us, but do we care?
            tcp.client.collect = 1
            tcp.server.collect = 1
        elif tcp.nids_state == nids.NIDS_DATA:
            b=filter.dealMid(tcp,state.dic_tcp,state.ac)
            if b:
                state.ls_pro.append(self.getTheIPPORT(tcp.addr))
        elif tcp.nids_state in self.end_states:
            filter.dealEnd(tcp,state.dic_tcp,state.ac)

    def main(self):
        #nids.param("scan_num_hosts", 0)
        nids.param("filename", "test1.pcap")
        nids.chksum_ctl([('0.0.0.0/0', False)]) # disable checksumming
        #nids.register_udp()
        nids.init()

        nids.register_tcp(self.handleTcpStream)
        # Loop forever (network device), or until EOF (pcap file)
        # Note that an exception in the callback will break the loop!
        try:
            nids.run()
        except nids.error, e:
            print "nids/pcap error:", e
        except Exception, e:
            print "misc. exception (runtime error in user callback?):", e

    def run(self):
        self.main()

#    if __name__ == '__main__':
 #       main()
