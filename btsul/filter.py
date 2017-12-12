#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
0::Bt but no request
1::client requested
2::server requested
"""
import state

def dealEnd(tcp,dic,ac):
    addr=tcp.addr
    if addr in dic:
        print "end :", addr
        del dic[addr]
        ac.remove(addr)
        state.isChanged = True

def dealMid(tcp,dic,ac):

    addr=tcp.addr
    isHit={}

    if addr not in dic:
        if tcp.client.count_new>0:
            hash_info=isBt(tcp.client.data)
            data=tcp.client.data
            tcpl=tcp.client.count_new-68
            kind=1
        elif tcp.server.count_new>0:
            hash_info=isBt(tcp.server.data)
            data=tcp.server.data
            tcpl = tcp.server.count_new-68
            kind=2
        else:
            hash_info=None
        if hash_info==None:
            return isHit
        else:
            dic[addr]=[0,[0,0,0],[0,0,0],hash_info]
            state.isChanged = True
            ac.add(addr)
            isHit=ac.search(addr,hash_info)
            isRequest(data[68:],dic[addr],tcpl,kind)
            print addr, "hand shaked", kind

    elif dic[addr][0]==0:
        if tcp.client.count_new>0:
            data=tcp.client.data
            if isBt(tcp.client.data):
                print addr, "hand shaked", 1
                bool = isRequest(data[68:], dic[addr], tcp.client.count_new-68, 1)
                if bool:
                    dic[addr][0] = 1
                return isHit
            bool = isRequest(data,dic[addr],tcp.client.count_new,1)
            if bool:
                #print addr, "requested",1
                dic[addr][0]=1
        else:
            data=tcp.server.data
            if isBt(tcp.server.data):
                print addr, "hand shaked", 2
                bool = isRequest(data[68:], dic[addr], tcp.server.count_new-68, 2)
                if bool:
                    dic[addr][0] = 2
                return isHit
            bool=isRequest(data,dic[addr],tcp.server.count_new,2)
            if bool:
                dic[addr][0]=2
                #print addr, "requested", 2
    elif dic[addr][0]==1:
        if tcp.client.count_new > 0 :
            if not isRequest(tcp.client.data,dic[addr],tcp.client.count_new,1):
                dic[addr][0]=3
        elif tcp.server.count_new>0:
            last_state, last_end, new_state, new_bgn=isPiece(tcp.server.data,dic[addr],tcp.server.count_new,1)
            if last_state:
                #print "piece",0,last_end,1
                isHit=ac.search(addr,tcp.server.data[0:last_end])
            if new_state==1:
                #print "piece",new_bgn,tcp.server.count_new,1
                isHit = ac.search(addr, tcp.server.data[new_bgn:])
    elif dic[addr][0]==2:
        if tcp.server.count_new > 0 :
            if not isRequest(tcp.server.data,dic[addr],tcp.server.count_new,2):
                dic[addr][0]=3
        elif tcp.client.count_new>0:
            last_state, last_end, new_state, new_bgn=isPiece(tcp.client.data,dic[addr],tcp.client.count_new,1)
            if last_state:
                #print "piece",0,last_end,1
                isHit=ac.search(addr,tcp.client.data[0:last_end])
            if new_state==1:
                #print "piece",new_bgn,tcp.client.count_new,1
                isHit = ac.search(addr, tcp.client.data[new_bgn:])
    if len(isHit)>0:
        ac.addMode(dic[addr][3])
        return True
    else:
        return False

def isBt(str):
    if ord(str[0])!=19:
        return None
    if str[1:20]=="BitTorrent protocol":
        #print "get handshake"
        return str[28:48]

def isPiece(str,ls,leng,kind):
    ans = False
    last_state=ls[kind][2]
    last_end=leng
    new_bgn=-1
    new_state=-1

    if leng == 0:
        return ans
    state = ls[kind]
    state1 = state[0]%256
    numk = 0
    if state1 == 0:
        bgn = 0
        numk=4
        strlen = 0
    elif state1 < 4:
        bgn = 0
        numk = state1
        strlen = state[1]
    elif state1 == 4:
        bgn = 0
        numk = 0
        strlen = state[1]
    elif state1 == 5:
        numk = state[1] + 4
        bgn = state[1]
        strlen = 0
    while True:
        if bgn >= leng:
            state[0] = 5
            state[1] = bgn - leng
            if new_state==-1:
                ls[kind][2] = last_state
            else:
                ls[kind][2] = new_state
            return last_state,last_end,new_state,new_bgn
        for i in range(bgn, numk):
            if i == leng:
                state[0] = numk - 1
                state[1] = strlen
                return ans
            strlen *= 256
            strlen += ord(str[i])
        if numk == leng:
            state[0] = 5
            state[1] = strlen
            return ans
        #print "flag:",ord(str[numk]),"len:",strlen
        if numk - 4 <= 0:
            last_state = 0
        if ord(str[numk]) == 7:
            last_end=numk-4
            ans=True
            new_state=1
            new_bgn=numk+9

        else:
            new_state=0
            #return ans
        bgn=numk+strlen
        numk=bgn+4
        strlen=0

def isRequest(str,ls,leng,kind):
    ans = False
    if leng == 0:
        return ans
    state = ls[kind]
    state1 = state[0]%256
    numk = 0
    if state1 == 0:
        bgn = 0
        numk=4
        strlen = 0
    elif state1 < 4:
        bgn = 0
        numk = state1
        strlen = state[1]
    elif state1 == 4:
        bgn = 0
        numk = 0
        strlen = state[1]
    elif state1 == 5:
        numk = state[1] + 4
        bgn = state[1]
        strlen = 0
    while True:
        if bgn >= leng:
            state[0] = 5
            state[1] = bgn - leng
            return ans
        for i in range(bgn, numk):
            if i == leng:
                state[0] = numk - 1
                state[1] = strlen
                return ans
            strlen *= 256
            strlen += ord(str[i])
        if numk == leng:
            state[0] = 5
            state[1] = strlen
            return ans
        #print "flag:",ord(str[numk]),"len:",strlen
        if ord(str[numk]) == 6:
            ans=True
            #return ans
        bgn=numk+strlen
        numk=bgn+4
        strlen=0


