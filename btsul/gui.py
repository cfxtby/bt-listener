# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import QThread
import multiprocessing
from PyQt4 import QtGui
from PyQt4.Qt import *
import time
import my_ac,socket,threading
import state

from PyQt4.QtGui import QTableWidgetItem

class fresh(QThread):
    update_date = pyqtSignal(QString)
    def setPip(self,pip):
        self.pip=pip
    def run(self):
        while True:
            """
            self.pip.send("get")
            print "send"
            print "get",self.pip.recv()
            print 'send2'
            print "get",self.pip.recv()
            print 'send3'
            print "get",self.pip.recv()
            """
            self.update_date.emit("go")
            time.sleep(1)


class DataAnalyse(QtGui.QMainWindow):
    blackList = []

    def __init__(self):

        super(DataAnalyse, self).__init__()
        self.initToolbar()
        self.initGrid()
        self.setGeometry(300, 300, 800, 300)
        self.setWindowTitle(u'黑人流量分析工具')
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.grid.horizontalHeader().setResizeMode(QHeaderView.Stretch)

    def initToolbar(self):
        inputAction = QtGui.QAction(QtGui.QIcon('add.png'), 'New', self)
        startAction = QtGui.QAction(QtGui.QIcon('begin.png'), 'New', self)
        stopAction = QtGui.QAction(QtGui.QIcon('end.png'), 'New', self)
        inputAction.setShortcut('Ctrl+N')
        startAction.setShortcut('Ctrl+E')
        stopAction.setShortcut('Delete')
        inputAction.triggered.connect(self.inputAction_def)
        startAction.triggered.connect(self.startAction_def)
        stopAction.triggered.connect(self.stopAction_def)
        self.tb_new = self.addToolBar('New')
        self.tb_edit = self.addToolBar('Edit')
        self.tb_del = self.addToolBar('Del')
        self.tb_new.addAction(inputAction)
        self.tb_edit.addAction(startAction)
        self.tb_del.addAction(stopAction)


    def initGrid(self):
        self.grid = QtGui.QTableWidget()

        self.setCentralWidget(self.grid)
        self.grid.setColumnCount(5)
        self.grid.setRowCount(0)
        column_width = [150, 150, 150, 150,150]
        for column in range(5):
            self.grid.setColumnWidth(column, column_width[column])
        headerlabels = [u'源IP', u'源端口',u'目的地址', u'目的端口', u'状态']
        self.grid.setHorizontalHeaderLabels(headerlabels)
        self.grid.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.grid.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def setDD(self,dd):
        self.dd=dd

    def refresh(self,data):
        i=0
        tcp="[((1,2),(1,2))]"
        dic_tcp=eval(tcp)
        for data in state.dic_tcp:
            if i>=self.grid.rowCount():
                self.grid.insertRow(i)
            ((sip,sport),(dip,dport))=data
            newItem = QTableWidgetItem(str(sip))
            newItem.setTextAlignment(0x004)
            self.grid.setItem(i,0,newItem)
            newItem = QTableWidgetItem(str(sport))
            newItem.setTextAlignment(0x004)
            self.grid.setItem(i, 1, newItem)
            newItem = QTableWidgetItem(str(dip))
            newItem.setTextAlignment(0x004)
            self.grid.setItem(i, 2, newItem)
            newItem = QTableWidgetItem(str(dport))
            newItem.setTextAlignment(0x004)
            self.grid.setItem(i, 3, newItem)
            newItem = QTableWidgetItem(u"检测中")
            newItem.setTextAlignment(0x004)
            self.grid.setItem(i, 4, newItem)
            i+=1
        dic_tcp=eval(tcp)
        for data in state.ls_pro:
            if i >= self.grid.rowCount():
                self.grid.insertRow(i)
            (sip,sport)=data[0]
            newItem = QTableWidgetItem(str(sip))
            newItem.setTextAlignment(0x004)
            self.grid.setItem(i,0,newItem)
            newItem = QTableWidgetItem(str(sport))
            newItem.setTextAlignment(0x004)
            self.grid.setItem(i, 1, newItem)
            newItem = QTableWidgetItem(u"等待禁止")
            newItem.setTextAlignment(0x004)
            self.grid.setItem(i, 4, newItem)
            i+=1
        dic_tcp=eval(tcp)
        for data in state.ls_pro:
            if i >= self.grid.rowCount():
                self.grid.insertRow(i)
            (sip, sport) = data[0]

            newItem = QTableWidgetItem(str(sip))
            newItem.setTextAlignment(0x004)
            self.grid.setItem(i,0,newItem)
            newItem = QTableWidgetItem(str(sport))
            newItem.setTextAlignment(0x004)
            self.grid.setItem(i, 1, newItem)
            newItem = QTableWidgetItem(u"已禁止")
            newItem.setTextAlignment(0x004)
            self.grid.setItem(i, 4, newItem)
            i+=1

        if i < self.grid.rowCount():
            n=self.grid.rowCount()
            for j in range(i,n):
                self.grid.removeRow(i)


    def inputAction_def(self):
        text, ok = QtGui.QInputDialog.getText(self, u'输入特征值',
                                              u'在这里输入特征值：')

        if ok:  #在这里修改点击OK要执行的动作
            my_ac.ac.addMode(text)

    def startAction_def(self):
        #self.pip.send("start")
        if not self.dd.is_alive():
            self.dd.start()
    def stopAction_def(self):
        #self.pip.send("stop")
        pass

class dealDa(threading.Thread):
    def run(self):
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect(("127.0.0.1", state.port))
        tmp=0
        le=0
        tmd=""
        ls=[state.dic_tcp,state.ls_pro,state.ls_rem]
        num=0
        while True:
            data=c.recv(1024)
            print "recv",data
            i=0
            while i<len(data):
                if tmp==0:
                    le=ord(data[i])
                    tmp+=1
                    i+=1
                elif tmp==1:
                    le=le*256+ord(data[i])
                    tmp=2
                    i+=1
                    if le==0:
                        tmp=0
                else:
                    if le<=len(data)-i:
                        tmd=tmd+data[i:i+le]
                        print "test",tmd
                        if num==0:
                            state.dic_tcp=eval(tmd)
                        elif num==1:
                            state.ls_pro=eval(tmd)
                        else:
                            state.ls_rem=eval(tmd)
                        num+=1
                        num=num%3
                        tmd=""
                        i=i+le
                    else:
                        tmd=tmd+data[i:]
                        le=le-len(data)+i
                        i=len(data)
                    tmp=0

class gui():
    def run(self):
        dd=dealDa()
        app = QtGui.QApplication(sys.argv)
        b = fresh()
        da = DataAnalyse()
        da.setDD(dd)

        b.update_date.connect(da.refresh)

        b.start()
        da.show()

        print "opne"
        sys.exit(app.exec_())
