import serial
import threading
import serial.tools.list_ports
import time

class AxisControll(threading.Thread):
    def __init__(self, device, port, baund):
        threading.Thread.__init__(self)
        self.porta = port
        self.baundRate = baund
        self.port=self.porta 
        #AH or DEC 
        self.device = device      

        self.result = self.com_ports()

        self.errorDome = False

        if self.porta in self.result:
            self.ser = serial.Serial(
            port=self.porta,
            baudrate=self.baundRate,
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

    def close_port(self):
        if self.ser:
            self.ser.close()

    def com_ports(self):
            self.list = serial.tools.list_ports.com_ports()
            self.connected = []
            for element in self.list:
                self.connected.append(element.device)

            return(self.connected)

    def progStatus(self):    
        if self.errorDome:
            return("+0 00 00.00 *0000000000000000")
        else:        
            try:  
                ack = self.write_cmd(self.device+" PROG STATUS\r")

                if len(ack) > 2:
                    return(ack)    
                else:
                    print("ProgStatus bug")
                    print(self.porta)
                    return("+0 00 00.00 *0000000000000000")
            except Exception as e:
                print(e)
                return("+0 00 00.00 *0000000000000000")

    def mover_rap(self, position):
        if not self.errorDome:           
            ret = 'ACK' in self.write_cmd(self.device+" EIXO MOVER_RAP = " + str(position) + "\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat 

    def mover_rel(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.write_cmd(self.device+" EIXO MOVER_REL = " + str(position) + "\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat                  

    def prog_error(self):
        if not self.errorDome:
            ret = 'ACK' in self.write_cmd(self.device+" PROG ERROS\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat 
                    
    def prog_parar(self):
        if not self.errorDome:
            ret = 'ACK' in self.write_cmd(self.device+" PROG PARAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def sideral_ligar(self):
        if not self.errorDome:
            ret = 'ACK' in self.write_cmd(self.device+" SIDERAL LIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def sideral_desligar(self):
        if not self.errorDome:
            ret = 'ACK' in self.write_cmd(self.device+" SIDERAL DESLIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat    
            
    def write_cmd(self, cmd):
        if not self.errorDome:
            try:
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
            except Exception as e:
                print(e)


AxisThread = threading.Thread(target = AxisControll, args=[])
AxisThread.daemon = True
AxisThread.start()