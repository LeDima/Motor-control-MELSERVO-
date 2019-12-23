# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 11:38:25 2019

@author: LeDima
"""
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

from GUI import *

class MyForm(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # self.ui.ButtonClickMe.clicked.connect(self.dispmessage)
        self.show()

    # def dispmessage(self):
    #     self.ui.labelResponse.setText("Hello "+self.ui.lineEditName.text())

if __name__=="__main__":    
    app = QtWidgets.QApplication(sys.argv)
    w = MyForm()
    w.show()
    sys.exit(app.exec_())