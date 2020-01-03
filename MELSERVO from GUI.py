# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 11:38:25 2019

@author: LeDima
"""
import sys
import glob

from functools import partial
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
        if self.SerialName!="None" :
            self.signal_error.emit('Serial port ' + self.MainDict['SerialName'] + ' connected.')
            print('Serial port', self.MainDict['SerialName'], 'connected.')
            if self.MainDict['MRJ_type']=='J2S-xCL':
                self.ABS_counter_cmd="8F"
                self.One_revolution_position="8E"
                self.Servo_motor_speed="86"
            else:
                self.ABS_counter_cmd="8C"
                self.One_revolution_position="8B"
                self.Servo_motor_speed="81"
                
                
                
            # self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"92","60","00000000",6)  
            self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"90","00","1EA5",6) #Disabled input/analog input/pulse train inputs. EMG, LSP and LSN is ON 
            self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"8B","00","0001",6) #Jog operation
            self.msleep(100)
            self.Set_Speed_MRJ()
            self.Set_Acceleration_MRJ()             
            # self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"A0","11","00005255",6)#Acceleration/deceleration time constant      
        else:
            self.signal_error.emit('Error opening the port ' + self.MainDict['SerialName'])
            
        while self.SerialName!="None":            
            if self.runing==1:
                # self.startTime = time()
                # print(self.write_and_read_MRJ_DIO(self.ser))
                # self.Get_MRJ_statuses()
                self.signal_main.emit([self.Get_Positin_MRJ(),self.Get_Speed_MRJ()])
                # print("Current statuses: ",self.Get_MRJ_statuses())
                # print("Current position: ",self.Get_Positin_MRJ())
                # print("Servo motor speed: ",self.Get_Speed_MRJ())
                # if(self.i>=500):
                #     self.i=self.j=0.001
                #     pass
                    
                # print("{0:.2f}".format(100*self.j/self.i)+"%")
                # print(self.j/self.i)
                # self.dataFloat = [float(data_to_send[i:i+7]) for i in range(56) if i%7==0]
                # data_to_send = self.write_and_read_MRJ(self.ser, self.MainDict['ICPCONAdres2'])
                # self.dataFloat += [float(data_to_send[i:i+7]) for i in range(56) if i%7==0]
                # self.dataFloat = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                # self.signal_main.emit(self.dataFloat)

#                print (self.dataFloat)
#                 print ("Elapsed time: {:.3f} sec".format(time() - self.startTime))
                self.msleep(self.MainDict['PeriodDate'])  # "Засыпаем" на PeriodDate милисекунды
            # elif self.runing==2:
            #     writereadCOM(ser,"0","90","00","1EA5") #Disabled input/analog input/pulse train inputs. EMG, LSP and LSN is ON 
            #     writereadCOM(ser,"0","8B","00","0001") 
            
            elif self.runing==3:
                self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"92","00","00010807",6)
                self.runing=1
            elif self.runing==4:
                self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"92","00","00011007",6)    
                self.runing=1
            elif self.runing==5:
                self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"92","00","00010007",6)    
                self.runing=1                 
            elif self.runing==6:
                # self.write_and_read_MRJ(self.ser,"0","84","0D","3000"+format(self.MainDict['MotorSpeedIN'],'04X'))
                # print("Set Speed: ",self.MainDict['MotorSpeedIN']) 
                self.Set_Speed_MRJ()
                # self.write_and_read_MRJ(self.ser,"0","92","60","00010007")    
                self.runing=1     
            elif self.runing==7:
                self.Set_Acceleration_MRJ()  
                self.runing=1                
            else:
                try:
                    self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"A0","11","000003E8",6)#Acceleration/deceleration time constant
                    self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"92","00","00010007",6) 
                    self.msleep(1500)
                    self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"A0","12","1EA5",6) #Clear the test operation acceleration/deceleration time constant.
                    self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"8B","00","0000",6) #Test operation mode cancel
                    self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"90","10","1EA5",6) #Enables input/analog input/pulse train inputs. EMG, LSP and LSN is ON 
                    self.ser.close()
                except:
                    self.signal_error.emit('Error opening the port ' + str(self.MainDict['SerialName']))
                else:
                    print("port close")
                break

    
    def CreateFileConfigandDate(self):
        
        try:
            with open('ConfigandDate.txt', 'r', encoding='utf-8') as f:
                self.MainDict = load(f)
        except (OSError, IOError):
            NewMainDict={'SerialName':'COM5'
                              , 'SerialSpeed':57600
                              , 'PeriodDate':200
                              , 'ServoAdres':'0'
                              , 'MRJ_Station_number':'0'
                              , 'Comment': 'SET1(1-,2-,3-,4-,5-) \nSET2(1-,2-,3-,4-,5-) \nSET3(1-,2-,3-,4-,5-) \nSET4(1-,2-,3-,4-,5-) \n'
                              , 'MRJ_type':'J2S-xCL'
                              , 'CurrentTabIndex': 1
                              , 'MotorSpeedIN':100
                              , 'MotorAccelerationIN':1000
                              , 'CurrentPosition':0
                              , 'CurrentSpeed':0
                              }
            with open('ConfigandDate.txt', mode='w', encoding='utf-8') as f:
                    dump(NewMainDict, f, indent=2)
            with open('ConfigandDate.txt', 'r', encoding='utf-8') as f:
                self.MainDict = load(f)
        f.close()

        try:
            self.SerialName=self.MainDict['SerialName']
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
          
        CRC2=format(sum([ord(ss) for ss in str1[1:]]),'02X')[-2:]

        cmd2=str1.encode("iso-8859-15")+CRC2.encode("iso-8859-15")

        while((resent==0)and(j<5)):
            j+=1
            try:
                self.i+=1
                s.flushInput()
                s.write(cmd2)
                data=s.read(numberchar)
                       
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
     
    def Get_MRJ_statuses(self):
        try:
            data = self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"12","00","",14)
            hex_data="{:08X}".format(int((data[3:-3]).decode('utf-8'),16))
        except:
            hex_data="00000000"    
            print("Error decode")

        return hex_data
    
    def Get_Positin_MRJ(self):
        try:
            data = int(self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"01",self.ABS_counter_cmd,"",18)[7:-3].decode('utf-8'),16)
            data = -(data & 0x80000000) | (data & 0x7fffffff)
            data2= int(self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"01",self.One_revolution_position,"",18)[7:-3].decode('utf-8'),16)
            data=round(data+data2/131072,2)
        except:
            data = 0
        return data
    def Get_Speed_MRJ(self):
        try:
            data = int(self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"01",self.Servo_motor_speed,"",18)[7:-3].decode('utf-8'),16)
            data = -(data & 0x80000000) | (data & 0x7fffffff)
        except:
            data = 0
        return data
    def Set_Acceleration_MRJ(self):#Write the acceleration/deceleration time constant [ms] in hexadecimal
        try:
            self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"A0","11","0000"+format(self.MainDict['MotorAccelerationIN'],'04X'),6)
            print("Set Acceleration: ",self.MainDict['MotorAccelerationIN'])           
        except:
            pass
    def Set_Speed_MRJ(self):
        try:
            # print("sgsdf")
            self.write_and_read_MRJ(self.ser,self.MainDict['ServoAdres'],"A0","10",format(self.MainDict['MotorSpeedIN'],'04X'),6)
            print("Set Speed: ",self.MainDict['MotorSpeedIN'])           
        except:
            pass


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.ST1_ON_Button.clicked.connect(self.onST1_ON_Button)
        self.ui.ST2_ON_Button.clicked.connect(self.onST2_ON_Button)
        self.ui.ST12_OFF_Button.clicked.connect(self.onST12_OFF_Button)
        self.ui.pushButton_Save_Settings.clicked.connect(partial(self.SaveDate,1))
        self.ui.button_Speed_m1.clicked.connect(partial(self.onSpeed_Button,-1))
        self.ui.button_Speed_m10.clicked.connect(partial(self.onSpeed_Button,-10))
        self.ui.button_Speed_m100.clicked.connect(partial(self.onSpeed_Button,-100))
        self.ui.button_Speed_p1.clicked.connect(partial(self.onSpeed_Button,1))
        self.ui.button_Speed_p10.clicked.connect(partial(self.onSpeed_Button,10))
        self.ui.button_Speed_p100.clicked.connect(partial(self.onSpeed_Button,100))
        self.ui.button_Acceleration_m10.clicked.connect(partial(self.onAcceleration_Button,-10))
        self.ui.button_Acceleration_m100.clicked.connect(partial(self.onAcceleration_Button,-100))
        self.ui.button_Acceleration_m1000.clicked.connect(partial(self.onAcceleration_Button,-1000))
        self.ui.button_Acceleration_p10.clicked.connect(partial(self.onAcceleration_Button,10))
        self.ui.button_Acceleration_p100.clicked.connect(partial(self.onAcceleration_Button,100))
        self.ui.button_Acceleration_p1000.clicked.connect(partial(self.onAcceleration_Button,1000))

        
        self.Thread_RS422_Communication = Thread_RS422_Communication()
        self.Thread_RS422_Communication.signal_main.connect(self.on_change, QtCore.Qt.QueuedConnection)
        self.Thread_RS422_Communication.start() 
        
        self.ui.tabWidget.setCurrentIndex(self.Thread_RS422_Communication.MainDict['CurrentTabIndex'])
        
        # self.ui.comboBoxSerialSpeed.addItems(['9600', '19200', '38400', '57600'])
        index = self.ui.comboBoxSerialSpeed.findText(str(self.Thread_RS422_Communication.MainDict['SerialSpeed']),QtCore.Qt.MatchFixedString)
        self.ui.comboBoxSerialSpeed.setCurrentIndex(index)
        
        self.ui.comboBoxSerialName.addItems([self.Thread_RS422_Communication.SerialName]+self.serial_ports())
        
        index = self.ui.comboBoxPeriodDate.findText(str(self.Thread_RS422_Communication.MainDict['PeriodDate']),QtCore.Qt.MatchFixedString)
        self.ui.comboBoxPeriodDate.setCurrentIndex(index)
        
        MotorSpeedIN=self.Thread_RS422_Communication.MainDict['MotorSpeedIN']
        self.ui.lineEdit_Speed_IN.setText(str(MotorSpeedIN))
        
        MotorAccelerationIN=self.Thread_RS422_Communication.MainDict['MotorAccelerationIN'] 
        self.ui.lineEdit_Acceleration_IN.setText(str(MotorAccelerationIN))
        
        
       
        # self.ui.spinBoxSpeed_IN_10X.setValue(int(self.Thread_RS422_Communication.MainDict['MotorSpeedIN']/100)*100)
        # digits = list(map(int, str(MotorSpeedIN)))
        # print(digits)
        
        # self.ui.Acceleration_IN_Slider.setSliderPosition(self.Thread_RS422_Communication.MainDict['MotorAccelerationIN'])
        
        
        # self.ui.ButtonClickMe.clicked.connect(self.dispmessage)
        self.show()
        
    def SaveDate(self,value=0):
        if value==1:
            self.Thread_RS422_Communication.MainDict['SerialName'] = self.ui.comboBoxSerialName.currentText()
        self.Thread_RS422_Communication.MainDict['CurrentTabIndex']=self.ui.tabWidget.currentIndex()
        self.Thread_RS422_Communication.MainDict['SerialSpeed'] = int(self.ui.comboBoxSerialSpeed.currentText())
        self.Thread_RS422_Communication.MainDict['PeriodDate'] = int(self.ui.comboBoxPeriodDate.currentText())
        with open('ConfigandDate.txt', mode='w', encoding='utf-8') as f:
            dump(self.Thread_RS422_Communication.MainDict, f, indent=2)
        f.close()  
    
    
    def closeEvent(self, event):
#        print("kjljuohoi")
        self.Thread_RS422_Communication.runing=0
        self.SaveDate()
        self.hide()
        self.Thread_RS422_Communication.wait(3000)
        self.Thread_RS422_Communication.terminate()
        
    def on_change(self, s):
        print(s)
        self.ui.lcdPosition.display("{:.2f}".format(s[0]))
        self.ui.lcdSpeed.display(str(s[1]))
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
        self.Thread_RS422_Communication.runing=3
        
    def onST2_ON_Button(self):
        self.Thread_RS422_Communication.runing=4
    
    def onST12_OFF_Button(self):
        self.Thread_RS422_Communication.runing=5
        
    
    def onSpeed_Button(self,value=0):
        # print(self.sender().myDate)
        value = self.Thread_RS422_Communication.MainDict['MotorSpeedIN']+value
        if value<=0:
           value=0
        elif value>=3000:
            value=3000
        self.ui.lineEdit_Speed_IN.setText(str(value))
        self.Thread_RS422_Communication.MainDict['MotorSpeedIN']=int(value)
        self.Thread_RS422_Communication.runing=6
        
        # print(value)

    def onAcceleration_Button(self,value=0):
        value = self.Thread_RS422_Communication.MainDict['MotorAccelerationIN']+value
        if value<=500:
           value=500
        elif value>=20000:
            value=20000
        self.ui.lineEdit_Acceleration_IN.setText(str(value))
        self.Thread_RS422_Communication.MainDict['MotorAccelerationIN']=int(value)
        self.Thread_RS422_Communication.runing=7       
        
        print(value)    
        
    
    # def onAcceleration_IN_Slider(self):
    #     self.Thread_RS422_Communication.runing=7
    #     self.Thread_RS422_Communication.MainDict['MotorAccelerationIN']=self.ui.Acceleration_IN_Slider.value()
    #     print(self.ui.Acceleration_IN_Slider.value())
        
    def serial_ports(self):
        """ Lists serial port names
    
            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(20)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
    
        result = []
        for port in ports:
            try:
                s = Serial(port)
                s.close()
                result.append(port)
            except (OSError, SerialException):
                pass
        return result

if __name__=="__main__":    
    
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = ApplicationWindow()
        window.show()
        sys.exit(app.exec_())
    except:
        # print("Exept")
        window.Thread_RS422_Communication.terminate()
    
    # app = QtWidgets.QApplication(argv)
    # window = ApplicationWindow()
    # w.show()
    # w.exec()
    # sys.exit(app.exec_())