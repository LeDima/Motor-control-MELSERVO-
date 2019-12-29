# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 09:53:37 2019

@author: LeDima
"""

import sys
import json
import glob
from time import gmtime, strftime, sleep, time
import serial
import serial.tools.list_ports


def serial_ports():
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
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result



def openPort():
    try:
        s = serial.Serial("/dev/ttyUSB0", 57600,parity=serial.PARITY_EVEN, timeout=0.05)  #57600
        print('Serial port',"COM7",'connected.')
                
    except serial.SerialException:
        print('Error opening the port ',"COM7")
        
    return s
    


def writereadCOM(s, motor="0",comand="12",dataNo="00", dataIN="" ):
    
    
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
    print(data)
    # data=data[3:-3]
    # print(data)
    # if data==b'':
        # data=b'FFFFFFFF'

    try:
        bres="{:032b}".format(int((data[3:-3]).decode('utf-8'),16))
        data=data[1:-2]
        # print(format(sum(ss for ss in data),'02X')[-2:])
        # print(bres)
        lres = len(bres)
        bres = ' '.join([bres[i:(i + 4)] for i in range(0, lres, 4)])
        # print(bres)
    except:
        # bres="11111111111111111111111111111111"
        print(data)
        print("Error decode")
   
    # print("----------")

if __name__ == "__main__":
    
    # print(serial.tools.list_ports.comports())
    # print(serial.tools.list_ports -v)
    
    # print([port for port in serial.tools.list_ports.comports() if port[2] != 'n/a'])
    print(serial_ports())
    
   
    ser=openPort()
    
    # writereadCOM(ser,"0","12","00","")#Reading of input device statuses
    # writereadCOM(ser,"0","82","00","1EA5")#Alarm reset
    # writereadCOM(ser,"0","05","0D","")
    # writereadCOM(ser,"0","12","40","")# External input pin status read
    # writereadCOM("0","12","60","")
    # writereadCOM(ser,"0","12","80","")
    # writereadCOM(ser,"0","90","10","1EA5") #Enables input/analog input/pulse train inputs. EMG, LSP and LSN is ON 
    # writereadCOM(ser,"0","90","00","1EA5") #Disabled input/analog input/pulse train inputs. EMG, LSP and LSN is ON 
    # writereadCOM(ser,"0","8B","00","0000")
    # writereadCOM(ser,"0","8B","00","0002")
    # writereadCOM(ser,"0","8B","00","0001")
    # writereadCOM(ser,"0","A0","11","00000300")
    # writereadCOM(ser,"0","A0","11","00000255")
    # writereadCOM(ser,"0","A0","10","0010")
    # writereadCOM(ser,"0","0","10","0100")
    # writereadCOM(ser,"0","A0","10","00000255")
    # writereadCOM(ser,"0","A0","13","00100000")
    # writereadCOM(ser,"0","05","09","")
    
    # writereadCOM(ser,"0","12","40","")
    # writereadCOM(ser,"0","92","00","00000807")
    # writereadCOM(ser,"0","92","00","00010807")#Input devices ON/OFF (test operation) SON,LSP,LSN,EMG,Forward rotation start (ST1)
    # writereadCOM(ser,"0","92","60","00010807")#Input devices ON/OFF  SON,LSP,LSN,EMG,Forward rotation start (ST1)
    # writereadCOM(ser,"0","92","60","00011007")#Input devices ON/OFF  SON,LSP,LSN,EMG,Reverse rotation start (ST2)
    # writereadCOM(ser,"0","92","60","00010007")#Input devices ON/OFF  SON,LSP,LSN,EMG
    # writereadCOM(ser,"0","92","60","00000000")#Input devices ON/OFF  SON,LSP,LSN,EMG
    # writereadCOM(ser,"0","92","60","00001000")#Input devices ON/OFF  SON,LSP,LSN,EMG,Reverse rotation start (ST2)
    # writereadCOM(ser,"0","92","60","00000007")
    # writereadCOM(ser,"0","92","00","00000000")
    # writereadCOM(ser,"0","92","60","00000000")
    # writereadCOM(ser,"0","92","61","")
    # print(format(10,'04X'))
    # writereadCOM(ser,"0","84","0D","3000"+format(100,'04X'))
    # writereadCOM(ser,"0","84","0D","30000F01")# Write Par.No.13 JOG Speed
    # writereadCOM(ser,"0","84","28","300003E8")# Write Par.No.40 JOG acceleration/deceleration time constant
    
   
    i=0
    
    while i<1:
        # print(strftime("%H:%M:%S +0000", gmtime()))
        # writereadCOM(ser,"0","92","00","00000807")
        # writereadCOM(ser,"0","92","00","00001007")
        writereadCOM(ser,"0","01","80","")
        writereadCOM(ser,"0","01","85","")
        writereadCOM(ser,"0","01","8F","")
        # writereadCOM(ser,"0","81","00","1EA5")
        writereadCOM(ser,"0","01","80","")
        writereadCOM(ser,"0","01","81","")
        writereadCOM(ser,"0","01","82","")
        # writereadCOM(ser,"0","01","83","")
        # writereadCOM(ser,"0","01","84","")
        
        # writereadCOM(ser,"0","01","86","")#Servo motor speed
        writereadCOM(ser,"0","01","8E","")
        writereadCOM(ser,"0","01","8F","")
        
        
        # writereadCOM(ser,"0","A0","10","00000255")
        # writereadCOM(ser,"0","A0","11","00000255")
        # writereadCOM(ser,"0","A0","10","00000200")
        sleep(0.200)
        print(time())
        # writereadCOM(ser,"0","01","81","")
        i=i+1
        
        
    
    
    ser.close()
    # writereadCOM("0","92","60","00010007")
    # writereadCOM("0","12","80","")
    
    # 00200007
    # cmd="01"
    # print(cmd)
    # data = b""
    # cmd="#"+cmd
    # print(cmd)
    # CRC = format(sum([ord(ss) for ss in cmd]),'02X')
    # print(CRC)
    # print(format(ord(CRC[0]),'02X'))
    # print(ord(CRC[1]))
    # cmd1 =  cmd.encode("iso-8859-15") + CRC.encode("iso-8859-15") + b"\r"
    # print(cmd1)
    # print(chr(1))
   

        
#    try:
#        stdout_old_target = sys.stdout
        # app = QtWidgets.QApplication(sys.argv)
        # window = ApplicationWindow()
        # window.show()
        # sys.exit(app.exec_())
#    except:
        # window.mythread.terminate()