#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *

from Plot import *

import PyQt4
from PyQt4 import QtCore, QtGui, QtSvg

app = None

#app = QtGui.QApplication(sys.argv)

class CPlottingWindow(QtGui.QMainWindow):

    
    app = None
    
    #FigList = []
    
    #==========================================
    def __init__(self):
    #==========================================
#         global app
#         if app == None: #one time only
#             print "new QApp instantiated"
#             app = QtGui.QApplication(sys.argv)
        super(CPlottingWindow, self).__init__()
        
                                              
        # CHANGE HERE ----------------------------
        WindowSize = (1920, 800)
        TextEditWidth = 400
        self.FigList = []
        #-----------------------------------------
    

        
        self.CentralWidget = QtGui.QWidget()
        self.HLayout = QtGui.QHBoxLayout()
        self.VLayout = QtGui.QVBoxLayout()
        self.TextEdit = QtGui.QPlainTextEdit()
        self.TextEdit.setReadOnly(True)
        self.TextEdit.setFixedWidth(TextEditWidth)
        
        self.HLayout.addWidget(self.TextEdit)
        self.HLayout.addLayout(self.VLayout)
        
        self.CentralWidget.setLayout(self.HLayout)
        self.setCentralWidget(self.CentralWidget)
        self.resize(WindowSize[0], WindowSize[1])
        
    #==========================================
    def __del__(self):
    #==========================================
        #print "Destructor called"
        for Fig in self.FigList:
            plt.figure(Fig.number)
            plt.clf
            #plt.close()
            #Fig.clf
            #del Fig
            #print "Fig cleared"
         
        #Needed? Maybe, FIXME   
        #plt.close()
    
        #FIXME: does not exist
        #super(CPlottingWindow, self).__del__()
        
    #==========================================
    def appendText(self, Text):
    #==========================================
        self.TextEdit.appendPlainText(Text)
        
    #==========================================
    def appendFig(self, Fig):
    #==========================================
        self.FigList.append(Fig)
        Canvas = FigureCanvas(Fig)
        self.VLayout.addWidget(Canvas)
        
    #==========================================
    def screenshot(self, FN):
    #==========================================
        p = QtGui.QPixmap.grabWidget(self)
        p.save(FN)
        #print "Screenshot taken"
        
    #==========================================
    def showGUI(self):
    #==========================================
        self.show()
        #global app
        test = QtCore.QCoreApplication.instance() 
        test.exec_()

#==========================================
def show_DictTreeWidget(Dict):
#==========================================
    
#     Dict = {
#         'foo':'bar',
#         'bar': ['f', 'o', 'o'],
#         'foobar':0,
#     }
    
    def data_to_tree(parent, data):
        if isinstance(data, dict):
            parent.setFirstColumnSpanned(True)
            for key,value in data.items():
                child = QtGui.QTreeWidgetItem(parent)
                child.setText(0, key)
                data_to_tree(child, value)
        elif isinstance(data, list):
            parent.setFirstColumnSpanned(True)
            for index,value in enumerate(data):
                child = QtGui.QTreeWidgetItem(parent)
                child.setText(0, str(index))
                data_to_tree(child, value)
        else:
            pass
            widget = QtGui.QLineEdit(parent.treeWidget())
            widget.setText(str(data))
            parent.treeWidget().setItemWidget(parent, 1, widget)
    
    app = QtGui.QApplication(sys.argv)
    
    wid = QtGui.QTreeWidget()
    wid.setColumnCount(2)
    wid.show()

    data_to_tree(wid.invisibleRootItem(), Dict)
    
    app.exec_()

