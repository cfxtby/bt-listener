#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading

port = 9999
isChanged=False
#本脚本主要进行存储多线程之间的交互数据，用于保存当时的状态
localhost=""
#捕包线程所能够处理的数据为：一个要封锁的ip，端口号、tcp或者udp的列表；
ls_pro=[]

#已封锁的ip、端口号、tcp或udp
ls_rem=[]

ls_rem1=[]

#正在检测的tcp的连接的状态
dic_tcp={}

#正在检测的udp的连接的状态
dic_udp={}
lock=threading.Lock()

start=False
close=False
