# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 11:38:25 2019

@author: LeDima
"""
import sys
import glob

# from sys import argv, exit, platform
from json import load, dump
from serial import SerialException, Serial, PARITY_EVEN
# from time import time
from PyQt5 import QtCore, QtGui, QtWidgets

from GUI import *



class Thread_RS422_Communication(QtCore.QThread):
    signal_main = QtCore.pyqtSignal(list)
    signal_error = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.runing = 1
        self.CreateFileConfigandDate()
        self.i=0.001
        self.j=0.001      
    def run(self):
        # print(13, self.runing)
        # self.signal_error.emit('2')
        if self.SerialName!="None" :
            # print(13, self.runing)
            self.signal_error.emit('Serial port ' + self.MainDict['SerialName'] + ' connected.')
            print('Serial port', self.MainDict['SerialName'], 'connected.')
        else:
            self.signal_error.emit('Error opening the port ' + self.MainDict['SerialName'])
            
        while self.SerialName!="None":
            
            if self.runing==1:
                # self.startTime = time()
                # print(self.write_and_read_MRJ_DIO(self.ser))
                # self.Get_MRJ_statuses()
                self.signal_main.emit([self.Get_Positin_MRJ(),self.Get_Speed_MRJ()])
                print("Current statuses: ",self.Get_MRJ_statuses())
                # print("Current position: ",self.Get_Positin_MRJ())
                # print("Servo motor speed: ",self.Get_Speed_MRJ())
                # if(self.i>=500):
                #     self.i=self.j=0.001
                #     pass
                    
                print("{0:.2f}".format(100*self.j/self.i)+"%")
                # print(self.j/self.i)
                # self.dataFloat = [float(data_to_send[i:i+7]) for i in range(56) if i%7==0]
                # data_to_send = self.write_and_read_MRJ(self.ser, self.MainDict['ICPCONAdres2'])
                # self.dataFloat += [float(data_to_send[i:i+7]) for i in range(56) if i%7==0]
                # self.dataFloat = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                # self.signal_main.emit(self.dataFloat)

#                print (self.dataFloat)
#                 print ("Elapsed time: {:.3f} sec".format(time() - self.startTime))
                self.msleep(self.MainDict['PeriodDate'])  # "Засыпаем" на PeriodDate милисекунды
                
            elif self.runing==2:
                self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"92","60","00010807",6)
                self.runing=1
            elif self.runing==3:
                self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"92","60","00011007",6)    
                self.runing=1
            elif self.runing==4:
                self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"92","60","00000000",6)    
                self.runing=1                 
            elif self.runing==5:
                # self.write_and_read_MRJ(self.ser,"0","84","0D","3000"+format(self.MainDict['MotorSpeedIN'],'04X'))
                # print("Set Speed: ",self.MainDict['MotorSpeedIN']) 
                self.Set_Speed_MRJ()
                # self.write_and_read_MRJ(self.ser,"0","92","60","00010007")    
                self.runing=1
                          
            else:
                try:
                    self.ser.close()
                except:
                    self.signal_error.emit('Error opening the port ' + str(self.MainDict['SerialName']))
                else:
                    # self.signal_error.emit('port close')
                    print("port close")
                break

    
    def CreateFileConfigandDate(self):
        
        try:
            with open('ConfigandDate.txt', 'r', encoding='utf-8') as f:
                self.MainDict = load(f)
        except (OSError, IOError):
            NewMainDict={'SerialName':'COM5'
                              , 'SerialSpeed':57600
                              , 'PeriodDate':500
                              , 'ServoAdres':'0'
                              , 'MRJ_Station_number':'0'
                              # , 'BeamDate':[[0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]
                              #             , [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]
                              #             , [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]
                              #             , [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]]
                              , 'Comment': 'SET1(1-,2-,3-,4-,5-) \nSET2(1-,2-,3-,4-,5-) \nSET3(1-,2-,3-,4-,5-) \nSET4(1-,2-,3-,4-,5-) \n'
                              , 'Precision': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
                              , 'SetValue': 1
                              , 'MotorSpeedIN':100
                              , 'CurrentPosition':0
                              , 'CurrentSpeed':0
                              }
            with open('ConfigandDate.txt', mode='w', encoding='utf-8') as f:
                    dump(NewMainDict, f, indent=2)
            with open('ConfigandDate.txt', 'r', encoding='utf-8') as f:
                self.MainDict = load(f)
        # print(f.read())
        f.close()

        try:
            self.SerialName=self.MainDict['SerialName']
            # if platform=="win32": self.SerialName='COM'+str(self.MainDict['SerialName'])
            # elif platform=="linux": self.SerialName='/dev/ttyS'+str(self.MainDict['SerialName'])
            self.ser = self.open_serial_port(self.MainDict['SerialName'])
        except:
            self.SerialName='None'
            print('System error')
            self.runing = 0

        
    def open_serial_port(self, serial_name: object) -> object:
        try:
            s = Serial(serial_name, self.MainDict['SerialSpeed'],parity=PARITY_EVEN)
            print(1500*1/self.MainDict['SerialSpeed'])
            s.timeout = 1500*1/self.MainDict['SerialSpeed'] # 500*1/self.MainDict['SerialSpeed']   #self.MainDict['SerialTimeout'];
        except SerialException:
            print('Error opening the port ',serial_name)
        return s
        
    def write_and_read_MRJ(self, s: object, motor = "0", comand = "01", dataNo = "80",dataIN = "",numberchar = 20  ) -> object:
        
        j=0
        resent=0
        str1="\x01"+motor+comand+"\x02"+dataNo+dataIN+"\x03"
        # print(str1.encode("utf-8"))
          
        CRC2=format(sum([ord(ss) for ss in str1[1:]]),'02X')[-2:]
        # print(CRC2[-2:])
        cmd2=str1.encode("iso-8859-15")+CRC2.encode("iso-8859-15")
        # print(motor+"-"+comand+"-"+dataNo+"-"+dataIN)
        # print(type(cmd2))
        while((resent==0)and(j<5)):
            j+=1
            try:
                self.i+=1
                s.flushInput()
                s.write(cmd2)
                data=s.read(numberchar)
           
                # print(data)
                # print(data[-2:].decode('utf-8'))
                # print(format(sum(ss for ss in data[1:-2]),'02X')[-2:])
            
                # print(data[-2:].decode('utf-8')==format(sum(ss for ss in data[1:-2]),'02X')[-2:])
                
                if(data[-2:].decode('utf-8')==format(sum(ss for ss in data[1:-2]),'02X')[-2:]):
                    resent=1                    
                else:                    
                    self.j+=1
                    data = None
            except:                
                self.j+=1
                data = None
        if(data==None):
            print("------")
           
            
                            
        return data
    
    # def write_and_read_MRJ_DIO(self, s: object, motor = "0", comand = "12", dataNo = "00",dataIN = "" ) -> object:
        
    #     data = self.write_and_read_MRJ(self.ser,motor,comand,dataNo,dataIN)
        
    #     try:
    #         bres="{:032b}".format(int((data[3:-3]).decode('utf-8'),16))
    #         # print(data)
    #         # print(bres)
    #         lres = len(bres)
    #         bres = ' '.join([bres[i:(i + 4)] for i in range(0, lres, 4)])
    #         # print(bres)
    #     except:
    #         # bres="11111111111111111111111111111111"
    #         print(data)
    #         print("Error decode")
    #     # print("----------")
    #     return data
    
    def Get_MRJ_statuses(self):
        try:
            data = self.write_and_read_MRJ(self.ser,"0","12","00","",14)
            hex_data="{:08X}".format(int((data[3:-3]).decode('utf-8'),16))
            # bres="{:032b}".format(int((data[3:-3]).decode('utf-8'),16))
            # print(data)
            # print(hex_data)
            # print(0x125)
            # lres = len(bres)
            # bres = ' '.join([bres[i:(i + 4)] for i in range(0, lres, 4)])
            # print(bres)
        except:
            # data = 0
            hex_data="00000000"
            # print(data)
            
            print("Error decode")
         
        
        # try:
        #     data = self.write_and_read_MRJ_DIO(self.ser)
        #     # data = -(data & 0x80000000) | (data & 0x7fffffff)
        # except:
        #     data = None
        return hex_data
    
    def Get_Positin_MRJ(self):
        try:
            data = int(self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"01","80","",18)[7:-3].decode('utf-8'),16)
            data = -(data & 0x80000000) | (data & 0x7fffffff)
        except:
            data = 0
        return data
    def Get_Speed_MRJ(self):
        try:
            data = int(self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"01","86","",18)[7:-3].decode('utf-8'),16)
            data = -(data & 0x80000000) | (data & 0x7fffffff)
        except:
            data = 0
        return data
    def Set_Speed_MRJ(self):
        try:
            self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"84","0D","3000"+format(self.MainDict['MotorSpeedIN'],'04X'),6)
            print("Set Speed: ",self.MainDict['MotorSpeedIN'])           
        except:
            pass
        #     data = None
        # return data


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        
        self.ui.ST1_ON_Button.clicked.connect(self.onST1_ON_Button)
        self.ui.ST2_ON_Button.clicked.connect(self.onST2_ON_Button)
        self.ui.ST12_OFF_Button.clicked.connect(self.onST12_OFF_Button)
        
        
        self.Thread_RS422_Communication = Thread_RS422_Communication()
        self.Thread_RS422_Communication.signal_main.connect(self.on_change, QtCore.Qt.QueuedConnection)
        self.Thread_RS422_Communication.start() 
        # self.ui.ButtonClickMe.clicked.connect(self.dispmessage)
        self.show()
        
    def closeEvent(self, event):       
#        print("kjljuohoi")
        # self.SaveDate()
        self.Thread_RS422_Communication.runing=0
        self.hide()
        self.Thread_RS422_Communication.wait(2000)
        self.Thread_RS422_Communication.terminate()
        
    def on_change(self, s):
        print(s)
        self.ui.lcdNumber.display(str(s[0]))
        # self.ui.lcdNumber.SetValue(500)
        # self.ValueDate[0].setText("Position: "+str(s[0]))
        # self.ValueDate[1].setText("Speed: "+str(s[1]))
        # if s[1]>0:
        #     self.ST1_ON_Button.setStyleSheet("background-color: #00FF00") #Green
        #     self.ST2_ON_Button.setStyleSheet("background-color: #FFFF00") #Yellow
        #     self.ST12_OFF_Button.setStyleSheet("background-color: #FFFF00") #Yellow            
        # elif s[1]<0:
        #     self.ST1_ON_Button.setStyleSheet("background-color: #FFFF00") #Yellow
        #     self.ST2_ON_Button.setStyleSheet("background-color: #00FF00") #Green
        #     self.ST12_OFF_Button.setStyleSheet("background-color: #FFFF00") #Yellow 
        # else:
        #     self.ST1_ON_Button.setStyleSheet("background-color: #FFFF00") #Yellow
        #     self.ST2_ON_Button.setStyleSheet("background-color: #FFFF00") #Yellow
        #     self.ST12_OFF_Button.setStyleSheet("background-color: #FF0000") #Red 

    # def dispmessage(self):
    #     self.ui.labelResponse.setText("Hello "+self.ui.lineEditName.text())
        
    def onST1_ON_Button(self):
        self.Thread_RS422_Communication.runing=2
        
    def onST2_ON_Button(self):
        self.Thread_RS422_Communication.runing=3
    
    def onST12_OFF_Button(self):
        self.Thread_RS422_Communication.runing=4

if __name__=="__main__":    
    
    
    app = QtWidgets.QApplication(sys.argv)
    window = ApplicationWindow()
    window.show()
    sys.exit(app.exec_())
    
    # app = QtWidgets.QApplication(argv)
    # window = ApplicationWindow()
    # w.show()
    # w.exec()
    # sys.exit(app.exec_())