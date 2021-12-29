import serial
import threading
import serial.tools.list_ports
import time

class DomeControll():
    def __init__(self, device):
        self.porta = "COM6"
        self.port=self.porta 
        #DOME 
        self.device = device      

        self.result = self.comPorts()

        self.errorDome = False

        if self.porta in self.result:
            self.ser = serial.Serial(
            port=self.porta,
            baudrate=9600,
            timeout=1
            )
            self.ser.close()
            if self.ser.isOpen() == False:
                try: 
                    self.ser.open()
                    self.ser.flushOutput()
                    self.ser.flushInput()
                    self.errorDome = False
                except Exception as e:
                    self.errorDome = True                    
        else:
            print('Cannot connect to: ', self.porta)
            self.errorDome = True

    def closePort(self):
        if self.ser:
            self.ser.close()

    def comPorts(self):
            self.list = serial.tools.list_ports.comports()
            self.connected = []
            for element in self.list:
                self.connected.append(element.device)

            return(self.connected)

    def progStatus(self):    
        if self.errorDome:
            return("+0 00 00.00 *0000000000000000")
        else:        
            try:  
                ack = self.writeCommand(self.device+" PROG STATUS\r")

                if len(ack) > 2:
                    return(ack)    
                else:
                    print("ProgStatus bug")
                    #print(ack)
                    return("+0 00 00.00 *0000000000000000")
            except Exception as e:
                print(e)
                return("+0 00 00.00 *0000000000000000")

    def moveCup(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" DOMO MOVER = " + str(position) + "\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat        

    def openShutter(self):
        if not self.errorDome:
            bitTrap = self.progStatus()[4]
            if bitTrap == "1" :
                ret = 'ACK' in self.writeCommand(self.device+" TRAPEIRA ABRIR\r")
                if ret:
                    stat = True
                else:
                    stat = False
                return stat           

    def CloseShutter(self):
        if not self.errorDome:
            bitTrap = self.progStatus()[4]
            if bitTrap == "1" :
                ret = 'ACK' in self.writeCommand(self.device+" TRAPEIRA FECHAR\r")
                if ret:
                    stat = True
                else:
                    stat = False
                return stat

    def DomeCW(self):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" DOMO GIRAR_CW\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def DomeCCW(self):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" DOMO GIRAR_CCW\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def DomeJOG(self):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" DOMO LIGAR_JOG\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def DomeRAP(self):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" DOMO LIGAR_RAP\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def DomeFlatLampON(self):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" FLAT_WEAK LIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
            
    def DomeFlatLampOFF(self):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" FLAT_WEAK DESLIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def progErros(self):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" PROG ERROS\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat 
                    
    def prog_parar(self):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" DOMO PARAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
            
    def writeCommand(self, cmd):
        if not self.errorDome:
            self.ser.flushOutput()
            self.ser.flushInput()
            self.ser.write(cmd.encode())
            timeoutDome = time.time()
            ack = ''
            while '\r' not in ack:
                ack += self.ser.read().decode()
                if (time.time() - timeoutDome) > 1:
                    self.ser.flushInput()
                    self.ser.flushOutput()
                    return ack
            print(ack)    
            return(ack)

DomeThread = threading.Thread(target = DomeControll, args=[])
DomeThread.start()