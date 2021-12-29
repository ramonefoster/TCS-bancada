import serial
import threading
import serial.tools.list_ports
import time

class AHControll():
    def __init__(self):
        self.porta = "COM6"
        self.port=self.porta        

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
                ack = self.writeCommand("AH PROG STATUS\r")

                if len(ack) > 2:
                    return(ack)    
                else:
                    print("ProgStatus bug")
                    #print(ack)
                    return("+0 00 00.00 *0000000000000000")
            except Exception as e:
                print(e)
                return("+0 00 00.00 *0000000000000000")

    def mover_rap(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand("AH EIXO MOVER_RAP = " + str(position) + "\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat 

    def mover_rel(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand("AH EIXO MOVER_REL = " + str(position) + "\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat                  

    def progErros(self):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand("AH PROG ERROS\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat 
                    
    def prog_parar(self):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand("AH PROG PARAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def sideral_ligar(self):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand("AH SIDERAL LIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def sideral_desligar(self):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand("AH SIDERAL DESLIGAR\r")
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

AhThread = threading.Thread(target = AHControll, args=[])
AhThread.start()