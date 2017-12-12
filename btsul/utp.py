#! /usr/bin/env python2
#-*- coding:utf-8 -*-

from my_ac import *
from filter import *

class peer(object):
    def __init__(self):
        self.cid = 0
        self.times = 0
        self.count_new = 0
        self.data = ""
        self.ack = -1
        self.seq = -1
        self.ls = []  # node is [seq,ack,data]

    def rst(self):
        self.count_new = 0
        self.data = ""

    def insert(self,ls,isutp):
        if isutp<2:
            self.ls.append(ls)
            return True
        if len(self.ls)==0:
            self.ls.append(ls)
        #print len(self.ls)
        if len(ls)>0 and ls[0]<=self.ls[0][0]:
            self.ls.insert(0,ls)
        for i in range(0,len(self.ls)):
            if ls[0]>self.ls[i][0] and (i+1==len(self.ls) or ls[0]==self.ls[i+1][0]):
                self.ls.insert(i+1,ls)
                break
        if self.seq<0:
            self.seq=self.ls[0][0]-1
            self.ack = self.ls[0][1]

        if len(self.ls)>20:
            print self.seq,self.ack
            for i in self.ls:
                print i[0],i[1]
            return False
        return True

    def getData(self):
        ret=[]
        while len(self.ls)>0:
            if self.seq==self.ls[0][0]:
                if len(self.ls[0][2])>0:
                    ret.append(self.ls[0][2])
                self.ack = self.ls[0][1]
                self.ls.pop(0)
            elif self.seq+1==self.ls[0][0]:
                if len(self.ls[0][2])>0:
                    ret.append(self.ls[0][2])
                self.seq+=1
                self.seq=self.ls[0][0]
                self.ack = self.ls[0][1]
                self.ls.pop(0)
            else:
                break
        return ret


class utp(object):
    #decide is utp stream,0 means sinit,1 means ver and type is right,2 means cid is right
    def __init__(self):
        self.isUtp = 0
        self.cid = 0
        self.client = peer()
        self.server = peer()
        self.notUtp=False

    def insert(self,udppkt,inOrder):

        typevar = ord(udppkt[0])

        if len(udppkt)<20:
            return False

        if (typevar >> 4) > 4 :
            return False
        if typevar % 16 != 1:
            return False

        extension=ord(udppkt[1])
        if extension>0:
            return False

        cid = (ord(udppkt[2]) << 8) + ord(udppkt[3])
        if self.isUtp==0:
            self.isUtp+=1
            self.cid=cid
            self.client.cid=cid
        elif self.isUtp==1:
            if inOrder:
                if self.cid==cid:
                    self.isUtp+=1
                else:
                    self.notUtp=True
                    return False
            else:
                if self.cid==cid+1 or self.cid==cid-1:
                    self.server.cid=cid
                else:
                    self.notUtp = True
                    return False

        ack=(ord(udppkt[18])<<8)+ord(udppkt[19])
        seq=(ord(udppkt[16])<<8)+ord(udppkt[17])
        if len(udppkt)<20:
            return False
        elif len(udppkt)==20:
            return True
        data=udppkt[20:]
        if inOrder:
            bool=self.client.insert((seq,ack,data),self.isUtp)
        else:
            bool=self.server.insert((seq, ack, data),self.isUtp)
        if not bool:
            print "lose the packet"
            self.notUtp=True
        return True

udp_dic={}
def dealUDP(addrs, payload,ac):
    ((sip, sport), (dip, dport)) = addrs
    kind=0
    maddrs = addrs
    if addrs in udp_dic:
        pkt = udp_dic[addrs]
        kind=1
        pkt.insert(payload, True)
    elif ((dip, dport), (sip, sport)) in udp_dic:
        maddrs=((dip, dport), (sip, sport))
        pkt = udp_dic[((dip, dport), (sip, sport))]
        kind = 2
        pkt.insert(payload, not True)
    else:
        pkt = utp()
        print "new", addrs
        if pkt.insert(payload, True):
            udp_dic[addrs] = pkt
        else:
            return

    if pkt.notUtp:
        print "del",addrs
        del udp_dic[maddrs]
        return

    datas=pkt.client.getData()
    for data in datas:
        getAns=dealData(data,maddrs,kind)
        if getAns and 'useful' in getAns:
            print "del", addrs
            del udp_dic[maddrs]
            return False
        elif getAns:
            return True
    datas = pkt.server.getData()
    for data in datas:
        getAns=dealData(data,maddrs,kind)
        if getAns and 'useful' in getAns:
            print "del", addrs
            del udp_dic[maddrs]
            return False
        elif getAns:
            return True
    return False



def dealData(data,addrs,kind):
    isHit={}
    if not addrs in state.dic_udp:
        hash_info=isBt(data)
        if hash_info==None:
            isHit["useful"]=False
            return isHit
        else:
            state.dic_udp[addrs]=[0,[0,0,0],[0,0,0]]
            data=data[68:]
            state.dic_udp[addrs].append(hash_info)
            ac.add(addrs)
            isHit = ac.search(addrs, hash_info)

    if len(data)==0:
        return None
    ls=state.dic_udp[addrs]
    if ls[0]==0:
        hash_info=isBt(data)
        if hash_info:
            print "hand !!"
            if hash_info==ls[3]:
                data=data[68:]

            else:
                ls[3]=hash_info
        else:
            if isRequest(data,ls,len(data),kind):
                ls[0]=1
                print "request"
    elif ls[0]==1:
        last_state, last_end, new_state, new_bgn = isPiece(data, ls, len(data), kind)
        if last_state:
            print "piece", 0, last_end, kind
            isHit = ac.search(addrs, data[0:last_end])
        if new_state == 1:
            print "piece", new_bgn, len(data), kind
            isHit = ac.search(addrs, data[new_bgn:])
        if len(isHit):
            ac.addMode(ls[3])
            ls[0]=2
            return True
        else:
            return False
    elif ls[0]==2:
        return False
