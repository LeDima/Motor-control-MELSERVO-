# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 568)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1000, 550))
        MainWindow.setMaximumSize(QtCore.QSize(1024, 568))
        font = QtGui.QFont()
        font.setPointSize(14)
        MainWindow.setFont(font)
        MainWindow.setIconSize(QtCore.QSize(32, 32))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 741, 501))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 501))
        self.tabWidget.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.tabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Triangular)
        self.tabWidget.setIconSize(QtCore.QSize(30, 30))
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setMovable(False)
        self.tabWidget.setTabBarAutoHide(False)
        self.tabWidget.setObjectName("tabWidget")
        self.Tab_Hourglass = QtWidgets.QWidget()
        self.Tab_Hourglass.setObjectName("Tab_Hourglass")
        self.tabWidget.addTab(self.Tab_Hourglass, "")
        self.Tab_Wheel = QtWidgets.QWidget()
        self.Tab_Wheel.setObjectName("Tab_Wheel")
        self.tabWidget.addTab(self.Tab_Wheel, "")
        self.Tab_Manual = QtWidgets.QWidget()
        self.Tab_Manual.setObjectName("Tab_Manual")
        self.pushButton = QtWidgets.QPushButton(self.Tab_Manual)
        self.pushButton.setGeometry(QtCore.QRect(170, 60, 121, 31))
        self.pushButton.setObjectName("pushButton")
        self.tabWidget.addTab(self.Tab_Manual, "")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(750, 20, 251, 481))
        self.groupBox.setObjectName("groupBox")
        self.lcdNumber = QtWidgets.QLCDNumber(self.groupBox)
        self.lcdNumber.setGeometry(QtCore.QRect(30, 40, 64, 23))
        self.lcdNumber.setObjectName("lcdNumber")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(130, 50, 47, 13))
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionasda = QtWidgets.QAction(MainWindow)
        self.actionasda.setObjectName("actionasda")

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_Hourglass), _translate("MainWindow", "Hourglass"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_Wheel), _translate("MainWindow", "Wheel"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_Manual), _translate("MainWindow", "Manual"))
        self.groupBox.setTitle(_translate("MainWindow", "Current parameter MRJ"))
        self.label.setText(_translate("MainWindow", "TextLabel"))
        self.actionasda.setText(_translate("MainWindow", "asda"))

