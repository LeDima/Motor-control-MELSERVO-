#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 09:18:09 2018

@author: LeDima
"""
import sys
from sys import argv, exit, platform
from json import load, dump
from serial import SerialException, Serial, PARITY_EVEN
# from time import time
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.Qt import QPixmap



# sys._excepthook = sys.excepthook

class MyThread(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(list)
    mysignalerror = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.runing = 1
        self.CreateFileConfigandDate()
    def run(self):
        if self.runing == 1:
            self.mysignalerror.emit('Serial port ' + str(self.MainDict['SerialNumber']) + ' connected.')
            print('Serial port', str(self.MainDict['SerialNumber']), 'connected.')
        while 1:
            if self.runing==1:
                # self.startTime = time()
                data_to_send = self.write_and_read_MRJ(self.ser)
                # self.dataFloat = [float(data_to_send[i:i+7]) for i in range(56) if i%7==0]
                # data_to_send = self.write_and_read_MRJ(self.ser, self.MainDict['ICPCONAdres2'])
                # self.dataFloat += [float(data_to_send[i:i+7]) for i in range(56) if i%7==0]
                self.dataFloat = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                self.mysignal.emit(self.dataFloat)

#                print (self.dataFloat)
#                 print ("Elapsed time: {:.3f} sec".format(time() - self.startTime))
                self.msleep(self.MainDict['PeriodDate'])  # "Засыпаем" на PeriodDate милисекунды
            elif self.runing==2:
                 self.write_and_read_MRJ(self.ser,"0","90","00","1EA5")    
                 self.write_and_read_MRJ(self.ser,"0","8B","00","0001")
                 self.write_and_read_MRJ(self.ser,"0","A0","11","00000300")
                 self.write_and_read_MRJ(self.ser,"0","A0","10","0100")
                 self.write_and_read_MRJ(self.ser,"0","92","00","00000807")
                 self.runing=1
                
            else:
                try:
                    self.ser.close()
                except:
                    self.mysignalerror.emit('Error opening the port ' + str(self.MainDict['SerialNumber']))
                else:
                    self.mysignalerror.emit('port close')
                    print("port close")
                break

    
    def CreateFileConfigandDate(self):
        
        try:
            with open('ConfigandDate.txt', 'r', encoding='utf-8') as f:
                self.MainDict = load(f)
        except (OSError, IOError):
            NewMainDict={'SerialNumber':1
                              , 'SerialSpeed':9600
                              , 'PeriodDate':500
                              , 'ServoAdres':'0'
                              , 'ICPCONAdres1':'01'
                              , 'ICPCONAdres2':'02'
                              , 'BeamDate':[[0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]
                                          , [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]
                                          , [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]
                                          , [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]]
                              , 'Comment': 'SET1(1-,2-,3-,4-,5-) \nSET2(1-,2-,3-,4-,5-) \nSET3(1-,2-,3-,4-,5-) \nSET4(1-,2-,3-,4-,5-) \n'
                              , 'Precision': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
                              , 'SetValue': 1
                             }
            with open('ConfigandDate.txt', mode='w', encoding='utf-8') as f:
                    dump(NewMainDict, f, indent=2)
            with open('ConfigandDate.txt', 'r', encoding='utf-8') as f:
                self.MainDict = load(f)
        # print(f.read())
        f.close()

        try:
            if platform=="win32": serialnumber='COM'+str(self.MainDict['SerialNumber'])
            elif platform=="linux": serialnumber='/dev/ttyS'+str(self.MainDict['SerialNumber']-1)
            self.ser = self.open_serial_port(serialnumber)
        except:
            self.mysignalerror.emit('System error')
            print('System error')
            self.runing = 0

        
    def open_serial_port(self, serial_name: object) -> object:
        try:
            s = Serial(serial_name, self.MainDict['SerialSpeed'],parity=PARITY_EVEN)
            print(1000/self.MainDict['SerialSpeed'])
            s.timeout = 1000/self.MainDict['SerialSpeed']   #self.MainDict['SerialTimeout'];
        except SerialException:
            print('Error opening the port ',serial_name)
            self.mysignalerror.emit('Error opening the port '+serial_name)
        return s
        
    def write_and_read_MRJ(self, s: object, motor = "0", comand = "01", dataNo = "80",dataIN = "" ) -> object:
        
        str1="\x01"+motor+comand+"\x02"+dataNo+dataIN+"\x03"
        # print(str1.encode("utf-8"))
          
        CRC2=format(sum([ord(ss) for ss in str1[1:]]),'02X')[-2:]
        # print(CRC2[-2:])
        cmd2=str1.encode("iso-8859-15")+CRC2.encode("iso-8859-15")
        print(motor+"-"+comand+"-"+dataNo+"-"+dataIN)
        # print(type(cmd2))
       
        s.write(cmd2)
        data=s.read(25)
        s.flushInput()
                            
        return data
    
    def write_and_read_MRJ_DIO(self, s: object, motor = "0", comand = "12", dataNo = "00",dataIN = "" ) -> object:
        
        data = self.write_and_read_MRJ(self.ser,motor,comand,dataNo,dataIN)
        
        print(data)
        data=data[3:-3]
        # print(data)
        if data==b'':
            data=b'FFFFFFFF'
    
        bres="{:032b}".format(int(data.decode('utf-8'),16))
                 
        print(bres)
        lres = len(bres)
        bres = ' '.join([bres[i:(i + 4)] for i in range(0, lres, 4)])
        print(bres)
        print("----------")
    


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
      
        self.setWindowTitle("PyQtScanViver")
        self.setGeometry(50, 100, 0, 0)

        self.main_widget = QtWidgets.QWidget(self)
        self.main_widget.setStyleSheet("background-color:#0080FF")
        #self.main_widget.se
        
        VBoxMain = QtWidgets.QVBoxLayout(self.main_widget)

        
        self.ButtonGET = [QtWidgets.QPushButton("GET1"),
                          QtWidgets.QPushButton("GET2"),
                          QtWidgets.QPushButton("GET3"),
                          QtWidgets.QPushButton("GET4")]

        self.ButtonSET = [QtWidgets.QPushButton("SET1"),
                          QtWidgets.QPushButton("SET2"),
                          QtWidgets.QPushButton("SET3"),
                          QtWidgets.QPushButton("SET4")]
                
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        
        j=1
        for i in self.ButtonGET:
            i.setSizePolicy(sizePolicy)
            i.ButtonNumber = j
            i.setStyleSheet("font: bold 18px; background-color: white") #min-hight: 10em;
            i.clicked.connect(self.onGetClick)
#            i.resize(200,100)
#            print(i.ButtonNumber)
            j=j+1

        j = 1
        for i in self.ButtonSET:
            # i.setSizePolicy(sizePolicy)
            i.setMaximumSize(60,30)
            i.ButtonNumber = j
            i.setStyleSheet("font: bold 18px; background-color: white")  # min-hight: 10em;
            i.clicked.connect(self.onSetClick)
            #            i.resize(200,100)
            #            print(i.ButtonNumber)
            j = j + 1
        
       
               
        self.ValueDate = [QtWidgets.QLineEdit(),QtWidgets.QLineEdit(),
                          QtWidgets.QLineEdit(),QtWidgets.QLineEdit(),
                          QtWidgets.QLineEdit(),QtWidgets.QLineEdit(),
                          QtWidgets.QLineEdit(),QtWidgets.QLineEdit(),
                          QtWidgets.QLineEdit(),QtWidgets.QLineEdit()]
                      
        for i in self.ValueDate:
            i.setReadOnly(1)
            i.setText("dY=+5.555")
            i.setFixedWidth(95)
   
        VBoxTextLeftTop = QtWidgets.QVBoxLayout()
        VBoxTextLeftTop.setContentsMargins(1, 1, 1, 1)
        VBoxTextLeftTop.setSpacing(1)
        VBoxTextLeftTop.addWidget(self.ValueDate[0])
        VBoxTextLeftTop.addWidget(self.ValueDate[1])
        
               
        VBoxTextLeftBottom = QtWidgets.QVBoxLayout()
        VBoxTextLeftBottom.setContentsMargins(1, 1, 1, 1)
        VBoxTextLeftBottom.setSpacing(1)
        VBoxTextLeftBottom.addWidget(self.ValueDate[2])
        VBoxTextLeftBottom.addWidget(self.ValueDate[3])
        
        boxLeftTop = QtWidgets.QGroupBox("GUN1 Diff")
        boxLeftTop.setStyleSheet("font:bold 15px")
        boxLeftTop.setLayout(VBoxTextLeftTop)
        
        boxLeftBottom = QtWidgets.QGroupBox("GUN2 Diff")
        boxLeftBottom.setStyleSheet("font:bold 15px")
        boxLeftBottom.setLayout(VBoxTextLeftBottom)
        
        VBoxLeft = QtWidgets.QVBoxLayout()
        VBoxLeft.addWidget(boxLeftTop,stretch=1,alignment=QtCore.Qt.AlignTop)
        VBoxLeft.addWidget(boxLeftBottom,stretch=1,alignment=QtCore.Qt.AlignBottom)
                
        VBoxTextRightTop = QtWidgets.QVBoxLayout()
        VBoxTextRightTop.setContentsMargins(1, 1, 1, 1)
        VBoxTextRightTop.setSpacing(1)
        VBoxTextRightTop.addWidget(self.ValueDate[4])
        VBoxTextRightTop.addWidget(self.ValueDate[5])
        
        VBoxTextRightCenter = QtWidgets.QVBoxLayout()
        VBoxTextRightCenter.setContentsMargins(1, 1, 1, 1)
        VBoxTextRightCenter.setSpacing(1)
        VBoxTextRightCenter.addWidget(self.ValueDate[8])
        VBoxTextRightCenter.addWidget(self.ValueDate[9])
        
        VBoxTextRightBottom = QtWidgets.QVBoxLayout()
        VBoxTextRightBottom.setContentsMargins(1, 1, 1, 1)
        VBoxTextRightBottom.setSpacing(1)
        VBoxTextRightBottom.addWidget(self.ValueDate[6])
        VBoxTextRightBottom.addWidget(self.ValueDate[7])
        
        boxRightTop = QtWidgets.QGroupBox("GUN3 Diff") # Объект rруппы
        boxRightTop.setStyleSheet("font:bold 15px")
        boxRightTop.setLayout(VBoxTextRightTop)
        
        boxRightCente = QtWidgets.QGroupBox("GUN5 Diff") # Объект rруппы
        boxRightCente.setStyleSheet("font:bold 14px")
        boxRightCente.setLayout(VBoxTextRightCenter)
        
        boxRightBottom = QtWidgets.QGroupBox("GUN4 Diff") # Объект rруппы
        boxRightBottom.setStyleSheet("font:bold 15px")
        boxRightBottom.setLayout(VBoxTextRightBottom)
        
        VBoxRight = QtWidgets.QVBoxLayout()
        VBoxRight.addWidget(boxRightTop,stretch=1,alignment=QtCore.Qt.AlignTop)
        VBoxRight.addWidget(boxRightCente)
        VBoxRight.addStretch(1)
        VBoxRight.addWidget(boxRightBottom,stretch=1,alignment=QtCore.Qt.AlignBottom)
        
        pixmap = QPixmap("Schem.bmp")
        label = QtWidgets.QLabel()
        label.setPixmap(pixmap)      
        
        HBoxText = QtWidgets.QHBoxLayout()
        HBoxText.addLayout(VBoxLeft)
        HBoxText.addWidget(label)
        HBoxText.addLayout(VBoxRight)

        VBoxButton = QtWidgets.QVBoxLayout()

        for i in self.ButtonGET:
            VBoxButton.addWidget(i)
                
        HBoxWidget = QtWidgets.QHBoxLayout()
        HBoxWidget.addLayout(HBoxText)
        HBoxWidget.addLayout(VBoxButton,stretch=1)
        
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setRowCount(11)
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setStyleSheet("background-color: white;font: 15px; gridline-color: #000000")

        for i in range(5):
            self.tableWidget.setSpan(2*i+1,0,2,1)

            font = QtGui.QFont()
            font.setPointSize(14)
            font.setBold(True)
            font.setWeight(75)
            item = QtWidgets.QTableWidgetItem(str(i+1))
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFont(font)
            self.tableWidget.setItem(2*i+1,0,item)

            item = QtWidgets.QTableWidgetItem("X")
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFont(font)
            self.tableWidget.setItem(2*i+1,1,item)

            item = QtWidgets.QTableWidgetItem("Y")
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFont(font)
            self.tableWidget.setItem(2*i+2,1,item)

        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        item = QtWidgets.QTableWidgetItem("GUN")
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        item.setFont(font)
        self.tableWidget.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem("X, Y")
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        item.setFont(font)
        self.tableWidget.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem("Present value")
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        item.setFont(font)
        self.tableWidget.setItem(0, 2, item)

        for i in range(4):
            self.tableWidget.setCellWidget(0, 3+i, self.ButtonSET[i])

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)

        if platform == "win32": width = 479
        elif platform == "linux": width = 527
        self.tableWidget.setMinimumSize(width, 332)
        self.tableWidget.setMaximumSize(width, 332)

        self.TextComment = QtWidgets.QPlainTextEdit()
        self.TextComment.setStyleSheet("background-color: white; font: 14px;")

        self.Commentlabel = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setPointSize(27)
        self.Commentlabel.setFont(font)
        self.Commentlabel.setText("Comment")

        self.CommentButton = QtWidgets.QPushButton("Save \n Comment")
        self.CommentButton.setStyleSheet("font: bold 22px; background-color: white")
        self.CommentButton.setSizePolicy(sizePolicy)

        self.CommentButton.clicked.connect(self.onSaveComentClick)
        
        self.DisableINButton = QtWidgets.QPushButton("Disable IN")
        self.DisableINButton.setStyleSheet("font: bold 22px; background-color: white")
        self.DisableINButton.setSizePolicy(sizePolicy)

        self.DisableINButton.clicked.connect(self.onDisableINClick)

        VBoxComment=QtWidgets.QVBoxLayout()
        VBoxComment.setContentsMargins(5, 5, 5, 5)
        # VBoxComment.setSpacing(10)
        VBoxComment.addWidget(self.DisableINButton)
        VBoxComment.addWidget(self.CommentButton)
        VBoxComment.addWidget(self.TextComment)

        boxComment = QtWidgets.QGroupBox("Comment")  # Объект rруппы
        boxComment.setStyleSheet("font:bold 15px")
        boxComment.setLayout(VBoxComment)

        HBoxWidgetTable = QtWidgets.QHBoxLayout()
        HBoxWidgetTable.addWidget(self.tableWidget)
        HBoxWidgetTable.addWidget(boxComment)

        self.TextError = QtWidgets.QPlainTextEdit()
        self.TextError.setReadOnly(1)
        self.TextError.setStyleSheet("background-color: white")

        self.SettingsButton = QtWidgets.QPushButton("Settings")
        self.SettingsButton.setStyleSheet("font: bold 22px; background-color: white")
        self.SettingsButton.setSizePolicy(sizePolicy)



        HBoxErrorSettings=QtWidgets.QHBoxLayout()
        HBoxErrorSettings.addWidget(self.TextError)
        HBoxErrorSettings.addWidget(self.SettingsButton)


        VBoxMain.addLayout(HBoxWidget)
        VBoxMain.addLayout(HBoxWidgetTable)
        VBoxMain.addLayout(HBoxErrorSettings)
        # VBoxMain.addWidget(self.TextError, stretch=0)

        self.mythread = MyThread()
        self.mythread.start() 

        self.mythread.mysignal.connect(self.on_change, QtCore.Qt.QueuedConnection)
        self.mythread.mysignalerror.connect(self.on_error, QtCore.Qt.QueuedConnection)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        
        self.SetValuePre=self.mythread.MainDict['SetValue']
        self.ButtonGET[self.SetValuePre-1].setStyleSheet("font: bold 18px; background-color:#00FF01")
        self.ButtonSET[self.SetValuePre - 1].setStyleSheet("font: bold 18px; background-color:#00FF01")
            
        for i in range(1,11):
            for j in range(4):
                self.tableWidget.setItem(i,j+3,QtWidgets.QTableWidgetItem(format(self.mythread.MainDict['BeamDate'][j][i-1], '+.03f')))
#                print(self.mythread.MainDict['SetValue'],j)
                if int(self.mythread.MainDict['SetValue'])-1==j:
                    self.tableWidget.item(i,j+3).setBackground(QtGui.QColor(0,255,0))
                else:
                    pass

        self.TextComment.insertPlainText(self.mythread.MainDict['Comment'])

        self.tableWidget.resizeColumnsToContents()

        self.SettingsButton.clicked.connect(self.showSettingsDialog)

        self.show()

    def on_change(self, s):
#        with Profiler() as p:
        self.PresentValue=s
        for i in range(10):
            DiffValues = s[i]-self.mythread.MainDict['BeamDate'][self.mythread.MainDict['SetValue']-1][i]
            if DiffValues<-self.mythread.MainDict['Precision'][i]:
                self.ValueDate[i].setStyleSheet("background-color: #00FF00") #Green
            elif DiffValues>+self.mythread.MainDict['Precision'][i]:
                self.ValueDate[i].setStyleSheet("background-color: #FF0000") #Red
            else:
                self.ValueDate[i].setStyleSheet("background-color: #FFFF00")  #Yellow

            if i%2==0:
                self.ValueDate[i].setText("dX="+format(DiffValues, '+.03f'))
            else:
                self.ValueDate[i].setText("dY="+format(DiffValues, '+.03f'))
                
            self.tableWidget.setItem(i+1,2,QtWidgets.QTableWidgetItem(format(s[i], '+.03f')))

    def on_error(self, s):
        self.TextError.appendPlainText(s)

    def onGetClick(self):
        #self.mythread.runing=2
        #self.mythread.wait(1000)
       # print(self.mythread.MainDict['BeamDate'])
       #  reply = QtWidgets.QMessageBox.question(self, 'Read new value',
       #      "Do you want read SET" + str(self.sender().ButtonNumber) + " value?", QtWidgets.QMessageBox.Yes |
       #      QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)
       #
       #  if reply == QtWidgets.QMessageBox.Yes:
            self.SetValueNow=self.sender().ButtonNumber
            self.mythread.MainDict['SetValue']=self.SetValueNow
            
            self.ButtonGET[self.SetValueNow-1].setStyleSheet("font: bold 18px; background-color:#00FF01")
            self.ButtonSET[self.SetValueNow - 1].setStyleSheet("font: bold 18px; background-color:#00FF01")
            self.ButtonGET[self.SetValuePre-1].setStyleSheet("font: bold 18px; background-color:white")
            self.ButtonSET[self.SetValuePre - 1].setStyleSheet("font: bold 18px; background-color:white")
            for i in range(10):
            
                for j in range(4):
                    self.tableWidget.setItem(i+1,j+3,QtWidgets.QTableWidgetItem(format(self.mythread.MainDict['BeamDate'][j][i], '+.03f')))
#                print(self.mythread.MainDict['SetValue'],j)
                    if int(self.mythread.MainDict['SetValue'])-1==j:
                        self.tableWidget.item(i+1,j+3).setBackground(QtGui.QColor(0,255,0))
                    else:
                        pass
            
            
            self.SetValuePre=self.SetValueNow
            self.SaveDate()
        #     pass
        # else:
        #     pass

    def onSetClick(self):
        number = self.sender().ButtonNumber
        reply = QtWidgets.QMessageBox.question(self, 'Save new position', "Do you want save new value in SET "+
                                               str(number)+  " ?",
                                               QtWidgets.QMessageBox.Yes |
                                               QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)
        if reply == QtWidgets.QMessageBox.Yes:
            for i in range(10):
                self.mythread.MainDict['BeamDate'][number-1][i]=self.PresentValue[i]
            self.SaveDate()

            for i in range(1, 11):
                for j in range(4):
                    self.tableWidget.setItem(i, j + 3, QtWidgets.QTableWidgetItem(
                        format(self.mythread.MainDict['BeamDate'][j][i - 1], '+.03f')))
                    if int(self.mythread.MainDict['SetValue']) - 1 == j:
                        self.tableWidget.item(i, j + 3).setBackground(QtGui.QColor(0, 255, 0))
        else:
            pass
        
        
    def onDisableINClick(self):
        
        self.mythread.runing=2
        
        # self.mythread.write_and_read_MRJ(self.mythread.ser,"0","90","00","1EA5")    
        # self.mythread.write_and_read_MRJ(self.mythread.ser,"0","8B","00","0001")
        # self.mythread.write_and_read_MRJ(self.mythread.ser,"0","A0","11","00000300")
        # self.mythread.write_and_read_MRJ(self.mythread.ser,"0","A0","10","0100")
        # self.mythread.write_and_read_MRJ(self.mythread.ser,"0","92","00","00000807")
        
        # reply = QtWidgets.QMessageBox.question(self, 'Save comment', "Do you want save comment?", QtWidgets.QMessageBox.Yes |
        #                                        QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)
        # if reply == QtWidgets.QMessageBox.Yes:
        #     self.mythread.MainDict['Comment']=self.TextComment.toPlainText()
        #     # self.TextComment.
        #     self.TextComment.setPlainText(self.mythread.MainDict['Comment'])
        #     self.SaveDate()
        # else:
        pass

    def onSaveComentClick(self):
        reply = QtWidgets.QMessageBox.question(self, 'Save comment', "Do you want save comment?", QtWidgets.QMessageBox.Yes |
                                               QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)
        if reply == QtWidgets.QMessageBox.Yes:
            self.mythread.MainDict['Comment']=self.TextComment.toPlainText()
            # self.TextComment.
            self.TextComment.setPlainText(self.mythread.MainDict['Comment'])
            self.SaveDate()
        else:
            pass

    def SaveDate(self):
        with open('ConfigandDate.txt', mode='w', encoding='utf-8') as f:
            dump(self.mythread.MainDict, f, indent=2)
        f.close()  
        
    def closeEvent(self, event):       
#        print("kjljuohoi")
        self.mythread.runing=0
        self.hide()
        self.mythread.wait(4000)
        self.mythread.terminate()


    def showSettingsDialog(self):
        ui=Settings_Dialog()

        ui.exec_()
        ui.show()



class Settings_Dialog(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)

        self.setWindowTitle("Settings")

        form = QtWidgets.QFormLayout()
        self.comboComNumber = QtWidgets.QComboBox()
        self.comboComNumber.addItems(["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9"])
        index = self.comboComNumber.findText("COM"+str(window.mythread.MainDict['SerialNumber']), QtCore.Qt.MatchFixedString)
        self.comboComNumber.setCurrentIndex(index)

        # self.comboComNumber.setEditable(False)

        self.comboComSpeed = QtWidgets.QComboBox()
        self.comboComSpeed.addItems(['9600', '19200', '38400', '57600', '115200'])
        index = self.comboComSpeed.findText(str(window.mythread.MainDict['SerialSpeed']),QtCore.Qt.MatchFixedString)
        self.comboComSpeed.setCurrentIndex(index)

        self.SpinPeriodDate = QtWidgets.QSpinBox()
        self.SpinPeriodDate.setRange(200,2000)
        self.SpinPeriodDate.setSingleStep(10)
        self.SpinPeriodDate.setValue(window.mythread.MainDict['PeriodDate'])

        self.TextDCONAdress1 = QtWidgets.QLineEdit()
        self.TextDCONAdress1.setText(str(window.mythread.MainDict['ICPCONAdres1']))
        self.TextDCONAdress2 = QtWidgets.QLineEdit()
        self.TextDCONAdress2.setText(str(window.mythread.MainDict['ICPCONAdres2']))

        self.SpinPrecision = QtWidgets.QDoubleSpinBox()
        self.SpinPrecision.setRange(0.01, 2)
        self.SpinPrecision.setSingleStep(0.01)
        self.SpinPrecision.setValue(window.mythread.MainDict['Precision'][0])

        self.ButtonSaveSettings = QtWidgets.QPushButton("Save settings")
        self.ButtonOut = QtWidgets.QPushButton("Exit")
        HBoxButton = QtWidgets.QHBoxLayout()
        HBoxButton.addWidget(self.ButtonSaveSettings)
        HBoxButton.addWidget(self.ButtonOut)

        self.ButtonOut.clicked.connect(self.Out)
        self.ButtonSaveSettings.clicked.connect(self.SaveSettings)

        # self.TextPresigionGun1 = QLineEdit()

        form.addRow("COM port Number", self.comboComNumber)
        form.addRow("COM port Speed", self.comboComSpeed)
        form.addRow("Period poll, ms(200,...,2000)", self.SpinPeriodDate)
        form.addRow("DCON Adres 1, (00,01,...,FF)", self.TextDCONAdress1)
        form.addRow("DCON Adres 2, (00,01,...,FF)", self.TextDCONAdress2)
        form.addRow("Precision, V(0.02,...,2)", self.SpinPrecision)
        form.addRow(HBoxButton)

        self.setLayout(form)

    def Out(self):
        # print("sdas")
        self.close()

    def SaveSettings(self):
        window.mythread.MainDict['SerialNumber'] = self.comboComNumber.currentIndex()+1
        window.mythread.MainDict['SerialSpeed'] = int(self.comboComSpeed.currentText())
        window.mythread.MainDict['ICPCONAdres1'] = self.TextDCONAdress1.displayText()
        window.mythread.MainDict['ICPCONAdres2'] = self.TextDCONAdress2.displayText()
        window.mythread.MainDict['PeriodDate'] = self.SpinPeriodDate.value() # TextDCONAdress2.displayText()
        window.mythread.MainDict['Precision'][0] = self.SpinPrecision.value()
        for i in range(10):
            window.mythread.MainDict['Precision'][i] = round(self.SpinPrecision.value(),2)
        window.SaveDate()

        pass
    
def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


if __name__ == "__main__":
    sys._excepthook = sys.excepthook
    sys.excepthook = my_exception_hook

    try:
        app = QtWidgets.QApplication(argv)
        window = ApplicationWindow()
        window.show()
        exit(app.exec_())
    except:
        # print("Exept")
        window.mythread.terminate()
        
