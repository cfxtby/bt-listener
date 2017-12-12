#!/usr/bin/python
# -*- coding: utf-8 -*-
from AC import *
import state

class my_ac(object):

    def __init__(self):
        if state.lock.acquire(1):
            self.sch = AC()
            self.sch.load()
            self.sch.initial()
            self.dic={}
            state.lock.release()
        #the sip,sport,dip,dport used as key and the state as answer

    # add one connection
    def add(self,fourS):
        self.dic[fourS]=0

    # add one fourth tuple
    def search(self,fourS,str):
        dic={}
        if state.lock.acquire(1):
            dic,self.dic[fourS]=self.sch.find(str,self.dic[fourS])
            state.lock.release()
        return dic
    def remove(self,addr):
        if addr in self.dic:
            del self.dic[addr]

    def addMode(self,str):
        self.sch.append(str)
        print self.sch.modes
        self.sch.dump()
        sch=AC()
        sch.load()
        sch.initial()
        state.lock.acquire(1)
        self.sch=sch
        state.lock.release()

    def close(self):
        self.sch.dump()
        self.sch=None
ac = my_ac()
if __name__=="__main__":

    ac.addMode("he")
    ac.addMode("she")
    ac.addMode("her")
    ac.addMode("hers")
    s="h"
    ac.add(s)
    print ac.search(s,"he and she is my friends,also her and hers ")