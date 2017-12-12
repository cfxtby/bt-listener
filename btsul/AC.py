#!/usr/bin/python
# -*- coding: <encoding name> -*-
import mode
class AC(object):
    def __init__(self):
        self.modes = []
        self.next = []
        self.base = []
        self.chk = []
        self.tofather = []
        self.fail = []
        self.state = 0
        self.dic1 = {}
    def load(self,filename="modes.txt"):
        try:
            self.modes=mode.readM(filename)
            self.modes.sort()
        except:
            self.modes=[]
            print "no file!!"

    def dump(self,filename="modes.txt"):
        mode.writeM(self.modes)

    def append(self,str):
        self.modes.append(str)
        self.modes.sort()

    def my_init(self):
        cnt_end=0
        j=0
        num=len(self.modes)
        f_state = [0] *num
        t_father = 1
        while cnt_end<num:
            father=0
            son = []
            dic={}
            nxt_state=0
            for i in range(0,num):
                if j==len(self.modes[i]):
                    mls=[]
                    mls.append(self.modes[i])
                    self.dic1[f_state[i]]=mls
                    cnt_end+=1
                    continue
                elif j>len(self.modes[i]):
                    continue
                elif len(son)==0:
                    nxt_state=t_father
                    father=f_state[i]
                    f_state[i]=t_father
                    t_father+=1
                    son.append(self.modes[i][j])
                    dic[father]=son
                elif son[-1] != self.modes[i][j] and father==f_state[i]:
                    son.append(self.modes[i][j])
                    f_state[i]=t_father
                    t_father+=1
                elif father!=f_state[i]:
                    son=[]
                    father = f_state[i]
                    f_state[i]=t_father
                    t_father+=1
                    son.append(self.modes[i][j])
                    dic[father] = son
                else:
                    f_state[i]=t_father-1
            j+=1
            self.get_tree(dic,nxt_state)

    def get_tree(self,dic,state=None):
        for key in dic:
            ls=dic[key]
            if len(self.next) == 0:
                self.next = [0] * 256
            for i in range(0, len(self.next)):
                flag = False
                if self.next[i] == 0:
                    flag=True
                    for node in ls:
                        if ord(node) - ord(ls[0])+i>=len(self.next):
                            self.next.extend([0]*256)
                        if self.next[ord(node) - ord(ls[0])+i] != 0:
                            flag = False
                            break

                if flag:
                    for node in ls:
                        self.next[ord(node) - ord(ls[0])+i]=state
                        self.chk.append(key)
                        self.tofather.append(node)
                        state+=1
                    self.base.append(i-ord(ls[0]))
                    break

    def nxtstate(self,state,c):
        if state>=len(self.base) or self.base[state]+ord(c)>=len(self.next) or self.base[state]+ord(c)<0:
            return 0
        n=self.next[self.base[state]+ord(c)]
        if self.chk[n-1]==state:
            return n
        else:
            return 0


    def goto(self,state,c):
        f=state
        t=0
        if f==0:
            return self.nxtstate(state,c)
        while t==0 and f!=0:
            t = self.nxtstate(f, c)
            f=self.fail[f]

        return t


    def fail1(self,state):
        if state==0:
            return 0
        elif self.chk[state-1]==0:
            return 0
        return self.nxtstate(self.fail[self.chk[state-1]],self.tofather[state-1])

    def getfail(self):
        self.fail=[0]*(len(self.chk)+1)
        for i in range(0,len(self.fail)):
            self.fail[i]=self.fail1(i)

    def initial(self):
        self.my_init()
        self.getfail()
        for i in range(1,len(self.fail)):
            nx=i
            while nx!=0:
                t=self.fail[nx]
                if t in self.dic1:
                    if i in self.dic1:
                        self.dic1[i].extend(self.dic1[t])
                    else:
                        self.dic1[i]=[].extend(self.dic1[t])
                nx=t


    def find(self,str,state=0):
        nx=state
        dic={}
        for i in range(0,len(str)):
            nx=self.goto(nx,str[i])
            if nx in self.dic1:
                dic[i]=self.dic1[nx]
        return dic,nx

if __name__=="__main__":
    #ls=["\x6a\x76\x2b\x45\xea"]
    ls=["he","she","her","hers"]
    ls.sort()
    a=AC()
    a.modes=ls
    a.initial()
    print a.find("hello,my name is Hello,I am he is she her here and hers name is he she ")

