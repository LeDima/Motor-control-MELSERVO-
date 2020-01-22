# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 11:38:25 2019

@author: LeDima
"""
import sys
import glob
import traceback

if sys.platform.startswith('linux'):
    import pigpio 
elif sys.platform.startswith('win'):
    pigpio=None

from functools import partial
# from sys import argv, exit, platform
from json import load, dump
from serial import SerialException, Serial, PARITY_EVEN
from time import time
from PyQt5 import QtCore, QtWidgets

from GUI import Ui_MainWindow




class Thread_RS422_Communication(QtCore.QThread):
    signal_main = QtCore.pyqtSignal(list)
    signal_error = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.mode="Manual_mode"
        self.SetCommand="Pass"
        # self.Vibration="OFF"
        try:
            self.PWM_Output=pigpio.pi()
        except:
            pass
        
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

            # self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","60","00000000",6)
            self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0000",6) #Test operation mode cancel
            self.msleep(10)
            self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"90","00","1EA5",6) #Disabled input/analog input/pulse train inputs. EMG, LSP and LSN is ON 
            self.msleep(10)
            self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0001",6) #Jog operation
            self.msleep(100)
            # self.Set_Speed_MRJ(self.MainDict['MotorSpeed_Manual'])
            # self.Set_Acceleration_MRJ()
            
            if self.MainDict['CurrentMode']==0:
                self.mode="Wheel_mode"
            elif self.MainDict['CurrentMode']==1:
                self.mode="Hourglass_mode"
            elif self.MainDict['CurrentMode']==2:
                self.mode="Hourglass_Wheel_mode"
            else:
                self.mode="Manual_mode"
            self.Initiation="NO"
            # self.SetCommand="Init"
            sleeptime = self.MainDict['PeriodDate']
            
            # self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"A0","11","00005255",6)#Acceleration/deceleration time constant      
        else:
            self.signal_error.emit('Error opening the port ' + self.MainDict['SerialName'])
            
        while self.SerialName!="None":            
            startTime=time()
            # print(self.mode)
            self.msleep(sleeptime)  # "Засыпаем" на PeriodDate милисекунды
            Current_Position_MRJ=self.Get_Position_MRJ()
            Current_Speed_MRJ=self.Get_Speed_MRJ()
            Current_statuses_MRJ=self.Get_MRJ_statuses()
            print(startTime,Current_Position_MRJ,Current_Speed_MRJ)
            self.signal_main.emit([Current_Position_MRJ,Current_Speed_MRJ,Current_statuses_MRJ])
            
            if self.mode=="Manual_mode":
                if self.Initiation == "NO":
                    self.Set_vibration_ON_OFF("OFF")
                    self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00010007",6)
                    if Current_Speed_MRJ ==0:
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0000",6)
                        self.msleep(10)
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0001",6)
                        self.msleep(10)
                        self.Set_Speed_MRJ(self.MainDict['MotorSpeed_Manual'])
                        self.Set_Acceleration_MRJ(self.MainDict['MotorAcceleration_Manual'])
                        self.Initiation="YES"
                else:
                    if self.SetCommand=="Pass":
                        pass
                    elif self.SetCommand=="Start_forward_rotation":
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00010807",6)
                    elif self.SetCommand=="Start_reverse_rotation":
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00011007",6)
                    elif self.SetCommand=="Stop_rotation":
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00010007",6)
                    elif self.SetCommand=="Set_Speed_MRJ":
                        self.Set_Speed_MRJ(self.MainDict['MotorSpeed_Manual'])
                    elif self.SetCommand=="Set_Acceleration_MRJ":
                        self.Set_Acceleration_MRJ(self.MainDict['MotorAcceleration_Manual'])
                    self.SetCommand="Pass"
            
            elif self.mode=="Wheel_mode":
                if self.Initiation == "NO":
                    self.Set_vibration_ON_OFF("OFF")
                    self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00010007",6)
                    if Current_Speed_MRJ ==0:
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0000",6)
                        self.msleep(10)
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0001",6)
                        self.msleep(10)
                        self.Set_Speed_MRJ(self.MainDict['MotorSpeed_Wheel'])
                        self.Set_Acceleration_MRJ(self.MainDict['MotorAcceleration_Manual'])
                        self.Initiation="YES"
                else:
                    if self.SetCommand=="Pass":
                        pass
                    elif self.SetCommand=="Start_forward_rotation":
                        self.Set_vibration_ON_OFF(self.MainDict['Vib_Wheel'],self.MainDict['VibInt_Wheel'])
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00010807",6)
                    elif self.SetCommand=="Start_reverse_rotation":
                        self.Set_vibration_ON_OFF(self.MainDict['Vib_Wheel'],self.MainDict['VibInt_Wheel'])
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00011007",6)
                    elif self.SetCommand=="Stop_rotation":
                        self.Set_vibration_ON_OFF("OFF")
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00010007",6)
                    elif self.SetCommand=="Set_Speed_MRJ":
                        self.Set_Speed_MRJ(self.MainDict['MotorSpeed_Wheel'])
                    elif self.SetCommand=="Set_Vibration":
                        statuses = self.Get_MRJ_statuses()
                        if (statuses == "00010807")or(statuses == "00011007"):
                            self.Set_vibration_ON_OFF(self.MainDict['Vib_Wheel'],self.MainDict['VibInt_Wheel'])
                    self.SetCommand="Pass"
                    
            elif self.mode=="Hourglass_mode":
                if self.Initiation == "NO":
                    self.Set_vibration_ON_OFF("OFF")
                    self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00010007",6)
                    if Current_Speed_MRJ ==0:
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0000",6)
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0002",6)
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00000001",6)
                        
                        MotorSpeed_Hourglass=self.MainDict['MotorSpeed_Hourglass']
                        MotorSpeed_Hourglass_Oscillation=self.MainDict['MotorSpeed_Hourglass_Oscillation']
                        MotorAcceleration_Hourglass=self.MainDict['MotorAcceleration_Hourglass']
                        VibInt_Hourglass=self.MainDict['VibInt_Hourglass']
                        Vib_Hourglass=self.MainDict['Vib_Hourglass']
                        ZeroPosition_Hourglass=self.MainDict['ZeroPosition_Hourglass']
                        HoldTime_Hourglass=self.MainDict['HoldTime_Hourglass']
                        Angle_Hourglass=self.MainDict['Angle_Hourglass']
                        NM=self.MainDict['NM']
                        NL=self.MainDict['NL']
                        Backlash=self.MainDict['Backlash']
                        
                        self.Set_Speed_MRJ(MotorSpeed_Hourglass)
                        self.Set_Acceleration_MRJ(MotorAcceleration_Hourglass)
                        
                        # print(Current_Position_MRJ)
                        # print(Current_Position_MRJ-ZeroPosition_Hourglass)
                        Current_to_HalfCircle_Position=ZeroPosition_Hourglass+self.MainDict['NM']/(2*self.MainDict['NL'])-Current_Position_MRJ
                        if Current_to_HalfCircle_Position<0:
                            Current_to_HalfCircle_Position =format(((abs(int(Current_to_HalfCircle_Position*131072)) ^ 0xFFFFFFFF) + 1) & 0xFFFFFFFF,'08X')
                        else:
                            Current_to_HalfCircle_Position=format(int(Current_to_HalfCircle_Position*131072),'08X')
                        print("Current_to_HalfCircle_Position =",Current_to_HalfCircle_Position)
                        # self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"A0","13",value,6)
                        # self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"A0","13",value,6)
                        # self.Set_Speed_MRJ(self.MainDict['MotorSpeed_Wheel'])
                        # self.Set_Acceleration_MRJ(self.MainDict['MotorAcceleration_Manual'])
                        Current_to_Zero_Position=ZeroPosition_Hourglass-Current_Position_MRJ
                        if Current_to_Zero_Position<0:
                            Current_to_Zero_Position =format(((abs(int(Current_to_Zero_Position*131072)) ^ 0xFFFFFFFF) + 1) & 0xFFFFFFFF,'08X')
                        else:
                            Current_to_Zero_Position=format(int(Current_to_Zero_Position*131072),'08X')
                        print("Current_to_Zero_Position =",Current_to_Zero_Position)
                        self.Initiation="YES"
                        self.SetCommand=="Pass"
                        iteration=0
                        iteration2=0
                else:
                    if self.SetCommand=="Pass":
                        # print("pass")
                        iteration=0
                        iteration2=0
                        # startTime_Hourglass=startTime
                        pass
                    # elif self.SetCommand=="Init":
                    #     self.Set_vibration_ON_OFF("OFF")
                    #     self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00000000",6)
                    #     self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0000",6)
                    #     self.msleep(10)
                    #     self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0002",6)
                    #     self.msleep(10)
                    #     MotorSpeed_Hourglass=self.MainDict['MotorSpeed_Hourglass']
                    #     MotorSpeed_Hourglass_Oscillation=self.MainDict['MotorSpeed_Hourglass_Oscillation']
                    #     MotorAcceleration_Hourglass=self.MainDict['MotorAcceleration_Hourglass']
                    #     VibInt_Hourglass=self.MainDict['VibInt_Hourglass']
                    #     Vib_Hourglass=self.MainDict['Vib_Hourglass']
                    #     ZeroPosition_Hourglass=self.MainDict['ZeroPosition_Hourglass']
                    #     HoldTime_Hourglass=self.MainDict['HoldTime_Hourglass']
                    #     Angle_Hourglass=self.MainDict['Angle_Hourglass']
                    #     self.Set_Acceleration_MRJ(Angle_Hourglass)
                    
                    elif self.SetCommand=="Start_Hourglass_rotation":
                        if Current_Speed_MRJ ==0:
                            if(iteration==0):
                                print(1)
                                # self.Set_vibration_ON_OFF("OFF")
                                self.Set_Speed_MRJ(MotorSpeed_Hourglass)
                                print("Current_to_HalfCircle_Position =",self.Move_Current_Position(ZeroPosition_Hourglass+NM/(2*NL)-Current_Position_MRJ+Angle_Hourglass*NM/(NL*360)))
                                self.msleep(100)
                                iteration=1
                                iteration2=0
                            elif(iteration==1):
                                print(2)
                                startTime_Hourglass=time()
                                self.Set_Speed_MRJ(MotorSpeed_Hourglass_Oscillation)
                                iteration=2
                                print(startTime_Hourglass)
                            elif(iteration==2):
                                print(3)
                                if(time()<startTime_Hourglass+HoldTime_Hourglass):
                                    if(iteration2==0):
                                        # self.Set_vibration_ON_OFF(self.MainDict['Vib_Hourglass'],self.MainDict['VibInt_Hourglass'])
                                        print("4",self.Move_Current_Position(-2*Angle_Hourglass*NM/(NL*360)-Backlash))
                                        self.msleep(200)
                                        iteration2=1
                                    elif(iteration2==1):
                                        print("5",self.Move_Current_Position(2*Angle_Hourglass*NM/(NL*360)+Backlash))
                                        self.msleep(200)
                                        iteration2=0
                                else:
                                    print(6)
                                    # self.Set_vibration_ON_OFF("OFF")
                                    self.Set_Speed_MRJ(MotorSpeed_Hourglass)
                                    print("Current_to_Zero_Position =",self.Move_Current_Position(ZeroPosition_Hourglass-Current_Position_MRJ-Angle_Hourglass*NM/(NL*360)-Backlash))
                                    self.msleep(100)
                                    iteration2=0
                                    iteration=3
                            elif(iteration==3):
                                print(7)
                                startTime_Hourglass=time()
                                iteration=4
                                self.Set_Speed_MRJ(MotorSpeed_Hourglass_Oscillation)
                                print(startTime_Hourglass)
                            elif(iteration==4):
                                print(8)
                                if(time()<startTime_Hourglass+HoldTime_Hourglass):
                                    if(iteration2==0):
                                        # self.Set_vibration_ON_OFF(self.MainDict['Vib_Hourglass'],self.MainDict['VibInt_Hourglass'])
                                        print("9",self.Move_Current_Position(+2*Angle_Hourglass*NM/(NL*360)+Backlash))
                                        self.msleep(200)
                                        iteration2=1
                                    elif(iteration2==1):
                                        print("10",self.Move_Current_Position(-2*Angle_Hourglass*NM/(NL*360)-Backlash))
                                        self.msleep(200)
                                        iteration2=0
                                else:
                                    print(11)
                                    # self.Set_vibration_ON_OFF("OFF")
                                    iteration2=0
                                    iteration=0
                                

                        else:
                            # print("Wait")
                            pass 
                            

                    elif self.SetCommand=="GoToZeroPositio_Hourglass_rotation":
                        if Current_Speed_MRJ ==0:
                            self.Set_vibration_ON_OFF("OFF")
                            self.Set_Speed_MRJ(MotorSpeed_Hourglass)
                            print("Current_to_Zero_Position =",self.Move_Current_Position(ZeroPosition_Hourglass-Current_Position_MRJ))
                            iteration2=0
                            iteration=0
                            self.SetCommand="Pass"
                        else: print("Wait")

                    # self.SetCommand="Pass"
                    
                    
                        
            elif self.mode=="Hourglass_Wheel_mode":
                if self.Initiation == "NO":
                    self.Set_vibration_ON_OFF("OFF")
                    self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00010007",6)
                    if Current_Speed_MRJ ==0:
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0000",6)
                        self.msleep(10)
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0002",6)
                        self.msleep(10)
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00000000",6)
                        # self.Set_Speed_MRJ(self.MainDict['MotorSpeed_Wheel'])
                        # self.Set_Acceleration_MRJ(self.MainDict['MotorAcceleration_Manual'])
                        self.Initiation="YES"
                else:
                    if self.SetCommand=="Pass":
                        pass
                    # elif self.SetCommand=="Init":
                    #     self.Set_vibration_ON_OFF("OFF")
                    #     self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00000000",6)
                    #     self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0000",6)
                    #     self.msleep(10)
                    #     self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0002",6)
                    #     self.msleep(10)
                    #     self.Set_Speed_MRJ(self.MainDict['MotorSpeed_Wheel'])
                    #     self.Set_Acceleration_MRJ(self.MainDict['MotorAcceleration_Manual'])
                    elif self.SetCommand=="Start_forward_rotation":
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00010807",6)
                    elif self.SetCommand=="Start_reverse_rotation":
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00011007",6)
                    elif self.SetCommand=="Stop_rotation":
                        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00010007",6)
                    elif self.SetCommand=="Set_Speed_MRJ":
                        self.Set_Speed_MRJ(self.MainDict['MotorSpeed_Wheel'])
                    self.SetCommand="Pass"
                    
                    
                    pass


            else:
                try:
                    print(10)
                    startTime=time()
                    self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"A0","11","000003E8",6)#Acceleration/deceleration time constant
                    self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00010007",6) 
                    self.msleep(350)
                    self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00010007",6)
                    self.msleep(350)
                    self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00010007",6)
                    self.msleep(350)
                    # self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"A0","12","1EA5",6) #Clear the test operation acceleration/deceleration time constant.
                    self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"8B","00","0000",6) #Test operation mode cancel
                    self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"90","10","1EA5",6) #Enables input/analog input/pulse train inputs. EMG, LSP and LSN is ON 
                    print(20)
                    self.ser.close()
                    
                    print ("Elapsed time: {:.3f} sec".format(time() - startTime))
                except:
                    self.signal_error.emit('Error opening the port ' + str(self.MainDict['SerialName']))
                else:
                    print("port close")
                    break
            # print ("Elapsed time: {:.3f} sec".format(time() - startTime))
        print("Thread exit")
    
    def CreateFileConfigandDate(self):
        
        try:
            with open('ConfigandDate.txt', 'r', encoding='utf-8') as f:
                self.MainDict = load(f)
        except (OSError, IOError):
            NewMainDict={'SerialName':'COM5'
                         , 'SerialSpeed':57600
                         , 'PeriodDate':50
                         , 'CurrentMode': 0
                         , 'MRJ_Station_number':'0'
                         , 'MRJ_type':'J2S-xCL'
                         , 'NL':1
                         , 'NM':50
                         , 'Backlash':0.20
                         
                         , 'MotorSpeed_Wheel':100
                         , 'VibInt_Wheel':20
                         , 'Vib_Wheel':'OFF'
                         
                         , 'MotorSpeed_Hourglass':100
                         , 'MotorSpeed_Hourglass_Oscillation':10
                         , 'MotorAcceleration_Hourglass':500
                         , 'VibInt_Hourglass':20
                         , 'Vib_Hourglass':'OFF'
                         , 'ZeroPosition_Hourglass':0.0
                         , 'HoldTime_Hourglass':10
                         , 'Angle_Hourglass':1.5
                         
                         , 'MotorSpeed_Manual':100
                         , 'MotorAcceleration_Manual':1000

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
            self.mode = 0
    
    def open_serial_port(self, serial_name: object) -> object:
        try:
            s = Serial(serial_name, self.MainDict['SerialSpeed'],parity=PARITY_EVEN)
            print(1500*1/self.MainDict['SerialSpeed'])
            s.timeout = 1500*1/self.MainDict['SerialSpeed'] # 500*1/self.MainDict['SerialSpeed']   #self.MainDict['SerialTimeout'];
            s.writeTimeout = 1500*1/self.MainDict['SerialSpeed']
        except SerialException:
            print('Error opening the port ',serial_name)
        return s
        
    def write_and_read_MRJ(self, s: object, motor = "0", comand = "01", dataNo = "80",dataIN = "",numberchar = 20  ) -> object:
        j=0
        str1="\x01"+motor+comand+"\x02"+dataNo+dataIN+"\x03"
        CRC2=format(sum([ord(ss) for ss in str1[1:]]),'02X')[-2:]
        cmd2=str1.encode("iso-8859-15")+CRC2.encode("iso-8859-15")
        while j<5:
            j+=1
            try:
                self.i+=1
                s.flushInput()
                # print("flushInput",end=" ")
                s.write(cmd2)
                # print("write",end=" ")
                data=s.read(numberchar)
                # print("read",end=" ")
                       
                if(data[-2:].decode('utf-8')==format(sum(ss for ss in data[1:-2]),'02X')[-2:]):
                    break
                else:                    
                    self.j+=1
                    data = None
            except:
                print("Except write_and_read_MRJ")
                self.j+=1
                data = None
                break
        if(data==None):
            pass
            print("------")
                           
        return data
    def Move_Current_Position(self,distanse=0.0):        
        value=self.Float_to_HEX_Position(distanse)
        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"A0","13",value,6)
        self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"92","00","00000001",6)
        return value
        
        
    
    def Float_to_HEX_Position(self,value=0.0):
        if value<0:
            value = format(((abs(int(value*131072)) ^ 0xFFFFFFFF) + 1) & 0xFFFFFFFF,'08X')
        else:
            value = format(int(value*131072),'08X')
        return value
        
     
    def Get_MRJ_statuses(self):
        try:
            data = self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"12","00","",14)
            hex_data="{:08X}".format(int((data[3:-3]).decode('utf-8'),16))
        except:
            hex_data="00000000"    
            print("Except Get_MRJ_statuses")
        return hex_data
    
    def Get_Position_MRJ(self):
        try:
            data = int(self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"01",self.ABS_counter_cmd,"",18)[7:-3].decode('utf-8'),16)
            data = -(data & 0x80000000) | (data & 0x7fffffff)
            data2= int(self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"01",self.One_revolution_position,"",18)[7:-3].decode('utf-8'),16)
            data=round(data+data2/131072,2)
        except:
            print("Except Get_Position_MRJ")
            data = 0
        return data
    
    def Get_Speed_MRJ(self):
        try:
            data = int(self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"01",self.Servo_motor_speed,"",18)[7:-3].decode('utf-8'),16)
            data = -(data & 0x80000000) | (data & 0x7fffffff)
        except:
            print("Except Get_Speed_MRJ")
            data = 0
        return data
    
    def Set_Acceleration_MRJ(self,Acceleration=1000):#Write the acceleration/deceleration time constant [ms] in hexadecimal
        try:
            self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"A0","11","0000"+format(Acceleration,'04X'),6)
            print("Set Acceleration: ",Acceleration)           
        except:
            print("Except Set_Acceleration_MRJ")
            pass
    
    def Set_Speed_MRJ(self,speed=0):
        try:
            self.write_and_read_MRJ(self.ser,self.MainDict['MRJ_Station_number'],"A0","10",format(speed,'04X'),6)
            print("Set Speed: ",speed)           
        except:
            print("Except Set_Speed_MRJ")
            pass
    
    def Set_vibration_ON_OFF(self,vibration_ON_OFF="OFF",vibration_intensity=0):
        try:
            if vibration_ON_OFF=="ON":
                self.PWM_Output.hardware_PWM(12,30000,10000*vibration_intensity)
            if vibration_ON_OFF=="OFF":
                self.PWM_Output.hardware_PWM(12,0,0)
        except:
            print("Except PWM")


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        serialname = self.serial_ports()
        print(1)
        self.ui.tabWidget.currentChanged.connect(self.onTabwiget)
        
        self.ui.ST1_ON_Button.clicked.connect(self.onST1_ON_Button)
        self.ui.ST2_ON_Button.clicked.connect(self.onST2_ON_Button)
        self.ui.ST12_OFF_Button.clicked.connect(self.onST12_OFF_Button)
        
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
        
        self.ui.ST1_ON_Button_Wheel.clicked.connect(self.onST1_ON_Button)
        self.ui.ST2_ON_Button_Wheel.clicked.connect(self.onST2_ON_Button)
        self.ui.ST12_OFF_Button_Wheel.clicked.connect(self.onST12_OFF_Button)
        
        self.ui.button_Speed_Wheel_m1.clicked.connect(partial(self.onSpeed_Wheel_Button,-1))
        self.ui.button_Speed_Wheel_m10.clicked.connect(partial(self.onSpeed_Wheel_Button,-10))
        self.ui.button_Speed_Wheel_m100.clicked.connect(partial(self.onSpeed_Wheel_Button,-100))
        self.ui.button_Speed_Wheel_p1.clicked.connect(partial(self.onSpeed_Wheel_Button,1))
        self.ui.button_Speed_Wheel_p10.clicked.connect(partial(self.onSpeed_Wheel_Button,10))
        self.ui.button_Speed_Wheel_p100.clicked.connect(partial(self.onSpeed_Wheel_Button,100))
        
        self.ui.button_VibInt_Wheel_m1.clicked.connect(partial(self.onVibInt_Wheel_Button,-1))
        self.ui.button_VibInt_Wheel_m10.clicked.connect(partial(self.onVibInt_Wheel_Button,-10))
        self.ui.button_VibInt_Wheel_p1.clicked.connect(partial(self.onVibInt_Wheel_Button,1))
        self.ui.button_VibInt_Wheel_p10.clicked.connect(partial(self.onVibInt_Wheel_Button,10))
        self.ui.comboBox_Vib_Wheel.currentIndexChanged.connect(partial(self.onVibInt_Wheel_Button,0))
        
        self.ui.button_Speed_Hourglass_m100.clicked.connect(partial(self.onSpeed_Hourglass_Button,-100))
        self.ui.button_Speed_Hourglass_p100.clicked.connect(partial(self.onSpeed_Hourglass_Button,100))
        
        self.ui.button_Speed_Oscillation_Hourglass_m5.clicked.connect(partial(self.onSpeed_Hourglass_Oscillation_Button,-5))
        self.ui.button_Speed_Oscillation_Hourglass_p5.clicked.connect(partial(self.onSpeed_Hourglass_Oscillation_Button,5))
        
        self.ui.button_Acceleration_Hourglass_m10.clicked.connect(partial(self.onAcceleration_Hourglass_Button,-10))
        self.ui.button_Acceleration_Hourglass_m100.clicked.connect(partial(self.onAcceleration_Hourglass_Button,-100))
        self.ui.button_Acceleration_Hourglass_p10.clicked.connect(partial(self.onAcceleration_Hourglass_Button,10))
        self.ui.button_Acceleration_Hourglass_p100.clicked.connect(partial(self.onAcceleration_Hourglass_Button,100))
        
        self.ui.button_VibInt_Hourglass_m1.clicked.connect(partial(self.onVibInt_Hourglass_Button,-1))
        self.ui.button_VibInt_Hourglass_m10.clicked.connect(partial(self.onVibInt_Hourglass_Button,-10))
        self.ui.button_VibInt_Hourglass_p1.clicked.connect(partial(self.onVibInt_Hourglass_Button,1))
        self.ui.button_VibInt_Hourglass_p10.clicked.connect(partial(self.onVibInt_Hourglass_Button,10))
        self.ui.comboBox_Vib_Hourglass.currentIndexChanged.connect(partial(self.onVibInt_Hourglass_Button,0))
        
        self.ui.button_SetZeroPosition_Hourglass.clicked.connect(self.onSetZeroPosition_Hourglass)
        self.ui.button_GoToZeroPosition_Hourglass.clicked.connect(self.onGoToZeroPosition_Hourglass_Button)
        
        self.ui.button_HoldTime_Hourglass_m10.clicked.connect(partial(self.onHoldTime_Hourglass_Button,-10))
        self.ui.button_HoldTime_Hourglass_p10.clicked.connect(partial(self.onHoldTime_Hourglass_Button,10))
        
        self.ui.button_Angle_Hourglass_m05.clicked.connect(partial(self.onAngle_Hourglass_Button,-0.5))
        self.ui.button_Angle_Hourglass_p05.clicked.connect(partial(self.onAngle_Hourglass_Button,0.5))
        
        self.ui.button_Start_Hourglass.clicked.connect(self.onStart_Hourglass_Button)
        
        self.ui.button_Backlash_m01.clicked.connect(partial(self.onBacklash_Button,-0.1))
        self.ui.button_Backlash_m001.clicked.connect(partial(self.onBacklash_Button,-0.01))
        self.ui.button_Backlash_p01.clicked.connect(partial(self.onBacklash_Button,0.1))
        self.ui.button_Backlash_p001.clicked.connect(partial(self.onBacklash_Button,0.01))
        
        self.ui.pushButton_Save_Settings.clicked.connect(partial(self.SaveDate,1))

        
        # self.ui.tabWidget.setStyleSheet("background-color:rgb(174, 255, 255);")
        print(2)
        
        try:
            self.Thread_RS422_Communication = Thread_RS422_Communication()
            self.Thread_RS422_Communication.signal_main.connect(self.on_change, QtCore.Qt.QueuedConnection)
            self.Thread_RS422_Communication.start() 
            print(3)
            self.ui.tabWidget.setCurrentIndex(self.Thread_RS422_Communication.MainDict['CurrentMode'])
            
            self.ui.comboBoxSerialName.addItems([self.Thread_RS422_Communication.SerialName]+serialname)
            
            index = self.ui.comboBoxSerialSpeed.findText(str(self.Thread_RS422_Communication.MainDict['SerialSpeed']),QtCore.Qt.MatchFixedString)
            self.ui.comboBoxSerialSpeed.setCurrentIndex(index)
            
            index = self.ui.comboBoxPeriodDate.findText(str(self.Thread_RS422_Communication.MainDict['PeriodDate']),QtCore.Qt.MatchFixedString)
            self.ui.comboBoxPeriodDate.setCurrentIndex(index)
            
            index = self.ui.comboBoxMRJ_type.findText(str(self.Thread_RS422_Communication.MainDict['MRJ_type']),QtCore.Qt.MatchFixedString)
            self.ui.comboBoxMRJ_type.setCurrentIndex(index)
            
            index = self.ui.comboBoxStation_number.findText(str(self.Thread_RS422_Communication.MainDict['MRJ_Station_number']),QtCore.Qt.MatchFixedString)
            self.ui.comboBoxStation_number.setCurrentIndex(index)
            
            NL=self.Thread_RS422_Communication.MainDict['NL']
            index = self.ui.comboBox_NL.findText(str(NL),QtCore.Qt.MatchFixedString)
            self.ui.comboBox_NL.setCurrentIndex(index)
            NM=self.Thread_RS422_Communication.MainDict['NM']
            index = self.ui.comboBox_NM.findText(str(NM),QtCore.Qt.MatchFixedString)
            self.ui.comboBox_NM.setCurrentIndex(index)
            
            self.ui.lineEdit_Backlash_IN.setText("{:.2f}".format(self.Thread_RS422_Communication.MainDict['Backlash']))
            
            self.ui.lineEdit_Speed_IN.setText(str(self.Thread_RS422_Communication.MainDict['MotorSpeed_Manual']))
            
            self.ui.lineEdit_Acceleration_IN.setText(str(self.Thread_RS422_Communication.MainDict['MotorAcceleration_Manual']))
            
            self.ui.button_Speed_Wheel_p1.setText( "+{:.3f}".format(NL/NM))
            self.ui.button_Speed_Wheel_p10.setText( "+{:.2f}".format(10*NL/NM))
            self.ui.button_Speed_Wheel_p100.setText( "+{:.1f}".format(100*NL/NM))
            self.ui.button_Speed_Wheel_m1.setText( "{:.3f}".format(-NL/NM))
            self.ui.button_Speed_Wheel_m10.setText( "{:.2f}".format(-10*NL/NM))
            self.ui.button_Speed_Wheel_m100.setText( "{:.1f}".format(-100*NL/NM))
            self.ui.lineEdit_Speed_Wheel_IN.setText("{:.2f}".format(self.Thread_RS422_Communication.MainDict['MotorSpeed_Wheel']*NL/NM))
            index = self.ui.comboBox_Vib_Wheel.findText(str(self.Thread_RS422_Communication.MainDict['Vib_Wheel']),QtCore.Qt.MatchFixedString)
            self.ui.comboBox_Vib_Wheel.setCurrentIndex(index)
            self.ui.lineEdit_VibInt_Wheel.setText(str(self.Thread_RS422_Communication.MainDict['VibInt_Wheel']))
            
            self.ui.button_Speed_Hourglass_p100.setText( "+{:.1f}".format(100*NL/NM))
            self.ui.button_Speed_Hourglass_m100.setText( "{:.1f}".format(-100*NL/NM))
            self.ui.lineEdit_Speed_Hourglass_IN.setText("{:.1f}".format(self.Thread_RS422_Communication.MainDict['MotorSpeed_Hourglass']*NL/NM))
            self.ui.button_Speed_Oscillation_Hourglass_p5.setText( "+{:.2f}".format(5*NL/NM))
            self.ui.button_Speed_Oscillation_Hourglass_m5.setText( "{:.2f}".format(-5*NL/NM))
            self.ui.lineEdit_Speed_Oscillation_Hourglass_IN.setText("{:.2f}".format(self.Thread_RS422_Communication.MainDict['MotorSpeed_Hourglass_Oscillation']*NL/NM))
            self.ui.lineEdit_Acceleration_Hourglass_IN.setText(str(self.Thread_RS422_Communication.MainDict['MotorAcceleration_Hourglass']))
            index = self.ui.comboBox_Vib_Hourglass.findText(str(self.Thread_RS422_Communication.MainDict['Vib_Hourglass']),QtCore.Qt.MatchFixedString)
            self.ui.comboBox_Vib_Hourglass.setCurrentIndex(index)
            self.ui.lineEdit_VibInt_Hourglass.setText(str(self.Thread_RS422_Communication.MainDict['VibInt_Hourglass']))
            self.ui.lineEdit_HoldTime_Hourglass.setText(str(self.Thread_RS422_Communication.MainDict['HoldTime_Hourglass']))
            self.ui.lineEdit_Angle_Hourglass.setText("{:.1f}°".format(self.Thread_RS422_Communication.MainDict['Angle_Hourglass']))

            # print(self.Thread_RS422_Communication.MainDict['Angle_Hourglass']*NL*360/NM)
            
            
            
            print(4)
            # self.ui.spinBox_NL.setValue(NL)
            # self.ui.spinBox_NM.setValue(NM)
            # self.ui.spinBox_NL.valueChanged.connect(self.onNL_NM_change)
            # self.ui.spinBox_NM.valueChanged.connect(self.onNL_NM_change)
        except:
            print("Except init Thread")
            self.Thread_RS422_Communication.mode=0
            
        
       
        # self.ui.spinBoxSpeed_IN_10X.setValue(int(self.Thread_RS422_Communication.MainDict['MotorSpeed_Manual']/100)*100)
        # digits = list(map(int, str(MotorSpeed_Manual)))
        # print(digits)
        
        # self.ui.Acceleration_IN_Slider.setSliderPosition(self.Thread_RS422_Communication.MainDict['MotorAcceleration_Manual'])
        
        
        # self.ui.ButtonClickMe.clicked.connect(self.dispmessage)
        # self.show()
        
    def on_change(self, s):
        # print('--',end ="")
        # self.ui.lcdPosition.display("{:.2f}".format(s[0]))
        self.ui.lineEdit_Position.setText("{:.2f}".format(s[0]))
        # self.ui.lcdSpeed.display(str(s[1]))
        self.ui.lineEdit_Speed.setText(str(s[1]))
        # print(s)
        
        if((s[2]=="00010807")or(s[1]>0)):
            self.ui.lineEdit_Statuses.setText("Rotation >")
            self.ui.lineEdit_Statuses.setStyleSheet("QLineEdit { background-color: green;border: 2px solid green;border-radius: 15px;}")
        elif((s[2]=="00011007")or(s[1]<0)):
            self.ui.lineEdit_Statuses.setText("Rotation <")
            self.ui.lineEdit_Statuses.setStyleSheet("QLineEdit { background-color: green;border: 2px solid green;border-radius: 15px;}")
        elif(s[2]=="00010007"or(s[2]=="00010006")):
            self.ui.lineEdit_Statuses.setText("STOP")
            self.ui.lineEdit_Statuses.setStyleSheet("QLineEdit { background-color: yellow;border: 2px solid  rgb(0, 173, 0);border-radius: 15px;}")
            # self.ui.MainWindow.setStyleSheet("QLineEdit#lineEdit_Statuses {background-color: yellow }")
        else:
            self.ui.lineEdit_Statuses.setText("ERROR")
            self.ui.lineEdit_Statuses.setStyleSheet("QLineEdit { background-color: red;border: 2px solid green;border-radius: 15px;}")
            
    def onTabwiget(self):
        index=self.ui.tabWidget.currentIndex()
        if index==0:
            self.Thread_RS422_Communication.mode="Wheel_mode"
        elif index==1:
            self.Thread_RS422_Communication.mode="Hourglass_mode"
        elif index==2:
            self.Thread_RS422_Communication.mode="Hourglass_Wheel_mode"
        else:
            self.Thread_RS422_Communication.mode="Manual_mode"
        self.Thread_RS422_Communication.Initiation="NO"
            
        print(index)
        pass
        
    def onBacklash_Button(self,value=0.0):
        value = self.Thread_RS422_Communication.MainDict['Backlash']+value
        if value<=0:
           value=0.0
        elif value>=2.0:
            value=2.0
        self.ui.lineEdit_Backlash_IN.setText("{:.2f}".format(value))
        self.Thread_RS422_Communication.MainDict['Backlash']=round(value,2)
        print(value)
        
    def onNL_NM_change(self):
        print("xcxzcx")
        self.Thread_RS422_Communication.MainDict['NM']=self.ui.spinBox_NM.value()
        self.Thread_RS422_Communication.MainDict['NL']=self.ui.spinBox_NL.value()        
        
    def onST1_ON_Button(self):
        self.Thread_RS422_Communication.SetCommand="Start_forward_rotation"
        
    def onST2_ON_Button(self):
        self.Thread_RS422_Communication.SetCommand="Start_reverse_rotation"
    
    def onST12_OFF_Button(self):
        self.Thread_RS422_Communication.SetCommand="Stop_rotation"
        
    def onSpeed_Button(self,value=0):
        value = self.Thread_RS422_Communication.MainDict['MotorSpeed_Manual']+value
        if value<=0:
           value=0
        elif value>=3000:
            value=3000
        self.ui.lineEdit_Speed_IN.setText(str(value))
        self.Thread_RS422_Communication.MainDict['MotorSpeed_Manual']=int(value)
        self.Thread_RS422_Communication.SetCommand="Set_Speed_MRJ"
        print(value)
        
    def onAcceleration_Button(self,value=0):
        value = self.Thread_RS422_Communication.MainDict['MotorAcceleration_Manual']+value
        if value<=500:
           value=500
        elif value>=20000:
            value=20000
        self.ui.lineEdit_Acceleration_IN.setText(str(value))
        self.Thread_RS422_Communication.MainDict['MotorAcceleration_Manual']=int(value)
        self.Thread_RS422_Communication.SetCommand="Set_Acceleration_MRJ"
        print(value)
        
    def onSpeed_Wheel_Button(self,value=0):
        NL=self.Thread_RS422_Communication.MainDict['NL']
        NM=self.Thread_RS422_Communication.MainDict['NM']
        value = self.Thread_RS422_Communication.MainDict['MotorSpeed_Wheel']+value
        if value<=0:
           value=0
        elif value>=3000:
            value=3000
        self.ui.lineEdit_Speed_Wheel_IN.setText("{:.2f}".format(value*NL/NM))
        self.Thread_RS422_Communication.MainDict['MotorSpeed_Wheel']=value
        self.Thread_RS422_Communication.SetCommand="Set_Speed_MRJ"
        print(value)
        
    def onVibInt_Wheel_Button(self,value=0):
        value = self.Thread_RS422_Communication.MainDict['VibInt_Wheel']+value
        if value<=0:
           value=0
        elif value>=80:
            value=80
        self.ui.lineEdit_VibInt_Wheel.setText(str(value))
        self.Thread_RS422_Communication.MainDict['VibInt_Wheel']=value
        print(self.ui.comboBox_Vib_Wheel.currentText())
        self.Thread_RS422_Communication.MainDict['Vib_Wheel']=self.ui.comboBox_Vib_Wheel.currentText()
        self.Thread_RS422_Communication.SetCommand="Set_Vibration"
        print(value)
        
    def onSpeed_Hourglass_Button(self,value=0):
        NL=self.Thread_RS422_Communication.MainDict['NL']
        NM=self.Thread_RS422_Communication.MainDict['NM']
        value = self.Thread_RS422_Communication.MainDict['MotorSpeed_Hourglass']+value
        if value<=0:
           value=0
        elif value>=1500:
            value=1500
        self.ui.lineEdit_Speed_Hourglass_IN.setText("{:.1f}".format(value*NL/NM))
        self.Thread_RS422_Communication.MainDict['MotorSpeed_Hourglass']=value
        # self.Thread_RS422_Communication.SetCommand="Set_Speed_MRJ"
        print(value)
        
    def onSpeed_Hourglass_Oscillation_Button(self,value=0):
        NL=self.Thread_RS422_Communication.MainDict['NL']
        NM=self.Thread_RS422_Communication.MainDict['NM']
        value = self.Thread_RS422_Communication.MainDict['MotorSpeed_Hourglass_Oscillation']+value
        if value<=0:
           value=0
        elif value>=300:
            value=300
        self.ui.lineEdit_Speed_Oscillation_Hourglass_IN.setText("{:.2f}".format(value*NL/NM))
        self.Thread_RS422_Communication.MainDict['MotorSpeed_Hourglass_Oscillation']=value
        # self.Thread_RS422_Communication.SetCommand="Set_Speed_MRJ"
        print(value)
        
    def onAcceleration_Hourglass_Button(self,value=0):
        value = self.Thread_RS422_Communication.MainDict['MotorAcceleration_Hourglass']+value
        if value<=200:
           value=200
        elif value>=2000:
            value=2000
        self.ui.lineEdit_Acceleration_Hourglass_IN.setText(str(value))
        self.Thread_RS422_Communication.MainDict['MotorAcceleration_Hourglass']=int(value)
        self.Thread_RS422_Communication.SetCommand="Set_Acceleration_MRJ"
        print(value)
        
    def onVibInt_Hourglass_Button(self,value=0):
        value = self.Thread_RS422_Communication.MainDict['VibInt_Hourglass']+value
        if value<=0:
           value=0
        elif value>=80:
            value=80
        self.ui.lineEdit_VibInt_Hourglass.setText(str(value))
        self.Thread_RS422_Communication.MainDict['VibInt_Hourglass']=value
        print(self.ui.comboBox_Vib_Hourglass.currentText())
        self.Thread_RS422_Communication.MainDict['Vib_Hourglass']=self.ui.comboBox_Vib_Hourglass.currentText()
        # self.Thread_RS422_Communication.SetCommand="Set_Vibration"
        print(value)
        
    def onSetZeroPosition_Hourglass(self):
        print(self.ui.lineEdit_Position.text())
        self.Thread_RS422_Communication.MainDict['ZeroPosition_Hourglass']=float(self.ui.lineEdit_Position.text())
        
    def onGoToZeroPosition_Hourglass_Button(self):
        self.Thread_RS422_Communication.SetCommand="GoToZeroPositio_Hourglass_rotation"
        pass
        
    def onAngle_Hourglass_Button(self,value=0.0):
        value = self.Thread_RS422_Communication.MainDict['Angle_Hourglass']+value
        if value<=0:
           value=0.0
        elif value>=20:
            value=20.0
        self.ui.lineEdit_Angle_Hourglass.setText("{:.1f}°".format(value))
        self.Thread_RS422_Communication.MainDict['Angle_Hourglass']=value
        print(value)
        
    def onHoldTime_Hourglass_Button(self,value=0):
        value = self.Thread_RS422_Communication.MainDict['HoldTime_Hourglass']+value
        if value<=10:
           value=10
        elif value>=600:
            value=600
        self.ui.lineEdit_HoldTime_Hourglass.setText(str(value))
        self.Thread_RS422_Communication.MainDict['HoldTime_Hourglass']=value
        print(value)
    def onStart_Hourglass_Button(self):
        self.Thread_RS422_Communication.SetCommand="Start_Hourglass_rotation"
        pass

        
        
    def SaveDate(self,value=0):
        
        if value==1:
            self.Thread_RS422_Communication.MainDict['SerialName'] = self.ui.comboBoxSerialName.currentText()
            
        self.Thread_RS422_Communication.MainDict['NL'] = int(self.ui.comboBox_NL.currentText())
        self.Thread_RS422_Communication.MainDict['NM'] = int(self.ui.comboBox_NM.currentText())
        self.Thread_RS422_Communication.MainDict['SerialSpeed'] = int(self.ui.comboBoxSerialSpeed.currentText())
        self.Thread_RS422_Communication.MainDict['PeriodDate'] = int(self.ui.comboBoxPeriodDate.currentText())
        self.Thread_RS422_Communication.MainDict['MRJ_type']=self.ui.comboBoxMRJ_type.currentText()        
        self.Thread_RS422_Communication.MainDict['MRJ_Station_number']=self.ui.comboBoxStation_number.currentText()
        self.Thread_RS422_Communication.MainDict['CurrentMode']=self.ui.tabWidget.currentIndex()
        
        with open('ConfigandDate.txt', mode='w', encoding='utf-8') as f:
            dump(self.Thread_RS422_Communication.MainDict, f, indent=2)
        f.close()  
    
    
    def closeEvent(self, event):
        # print(event)
        self.Thread_RS422_Communication.mode=0
        self.SaveDate()
        self.hide()
        self.Thread_RS422_Communication.wait(3000)
        # self.Thread_RS422_Communication.terminate()
        # sys.exit(0)
        event.accept()
        # self.exit(1)
        # return 1
        
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
                s = Serial(port,timeout=2,write_timeout=2)
                print(port,end=" ")
                s.close()
                print("close")
                result.append(port)
            except (OSError, SerialException):
                # traceback.print_exc()
                print("Except serial_ports scan")
        print("--")
        return result

if __name__=="__main__":
    # app = QtWidgets.QApplication(sys.argv)
    # window = ApplicationWindow()
    # window.show()
    # print(0)
    # # sys.exit()
    # sys.exit(app.exec_())
    # print(-1)
    
    try:
        # app = QtWidgets.QApplication.instance()
        app = QtWidgets.QApplication(sys.argv)
        # app.aboutToQuit.connect(app.deleteLater)
        window = ApplicationWindow()
        window.show()
        # print(0)
        # sys.exit()
        app.exec_()
        # app.exit(app.exec_())
        # print(-1)
    except:
        traceback.print_exc()
        print("Except window")

    
    try:
        window.Thread_RS422_Communication.mode=0
        print(1)
        window.Thread_RS422_Communication.wait(3000)
        print(2)
        # print("---",window.Thread_RS422_Communication.ser.is_open,"---")
        # print(type(window.Thread_RS422_Communicationser.ser))
        if window.Thread_RS422_Communication.ser.is_open:
            try:
                print(3)
                window.Thread_RS422_Communication.ser.close()
                print(4)
            except:
                traceback.print_exc()
                print(5)
                window.Thread_RS422_Communication.ser.__del__()
                print(6)
    except:
        traceback.print_exc()
        print("Except Thread_RS422_Communication")
        window.Thread_RS422_Communication.terminate()
        # print(4)
    # window.Thread_RS422_Communication.terminate()
    # print(window.Thread_RS422_Communication)
