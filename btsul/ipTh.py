#!/usr/bin/python
# -*- coding: <encoding name> -*-
import threading
import state
import iptc
import time
class ipAddTh(threading.Thread):

    def __init__(self,sig):
        threading.Thread.__init__(self)
        self.sig=sig

    def addIP(self,ipc):
        print ipc
        ((ip,port),val)=ipc

        rule = iptc.Rule()
        rule.protocol = val
        m = iptc.Match(rule, val)
        rule.src = ip
        m.sport = str(port)
        rule.add_match(m)
        rule.target = iptc.Target(rule, "DROP")
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
        chain.insert_rule(rule)
        rule = iptc.Rule()
        rule.protocol = val
        m = iptc.Match(rule, val)
        rule.dst = ip
        m.dport = str(port)
        rule.add_match(m)
        rule.target = iptc.Target(rule, "DROP")
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "OUTPUT")
        chain.insert_rule(rule)

    def run(self):
        print "add th begin:"
        while True:
            while len(state.ls_pro)>0:
                ip=state.ls_pro.pop(0)
                if ip not in state.ls_rem1:
                    try:
                        self.addIP(ip)
                        print "add rule", ip
                        state.ls_rem.append(ip + (time.time(),))
                        state.ls_rem1.append(ip)
                        state.isChanged = True
                    except:
                        print "error ip:",ip
                        state.ls_pro.append(ip)

            self.sig.clear()
            self.sig.wait()


class ipRevTh(threading.Thread):

    def revIP(self,ip):
        print "remove rule", ip
        ((ip, port), val,time)=ip
        rule = iptc.Rule()
        rule.protocol = val
        m = iptc.Match(rule, val)
        rule.src = ip
        m.sport = str(port)
        rule.add_match(m)
        rule.target = iptc.Target(rule, "DROP")
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
        chain.delete_rule(rule)
        rule = iptc.Rule()
        rule.protocol = val
        m = iptc.Match(rule, val)
        rule.dst = ip
        m.dport = str(port)
        rule.add_match(m)
        rule.target = iptc.Target(rule, "DROP")
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "OUTPUT")
        chain.delete_rule(rule)

    def rev(self):
        t = time.time()
        for ip in state.ls_rem:
            if ip[2] - 300 < t:
                self.revIP(ip)
                if ip in state.ls_rem1:
                    state.ls_rem1.remove(ip)
                state.ls_rem.remove(ip)
                state.isChanged = True
            else:
                break


    def run(self):
        print "rev th begin:"
        while True:
            t=time.time()
            while len(state.ls_rem)>0:
                ip=state.ls_rem[0]
                if ip[2]-300<t:
                    self.revIP(state.ls_rem.pop(0))
                    state.ls_rem1.pop(0)
                else:
                    break
            time.sleep(5*60)

if __name__=="__main__":
    ipAddTh(threading.Event()).addIP((("192.168.1.0",1122),'tcp'))
















