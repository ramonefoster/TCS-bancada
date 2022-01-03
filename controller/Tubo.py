import serial
import threading
import serial.tools.list_ports
import time

class TuboControll(threading.Thread):
    def __init__(self, device):
        threading.Thread.__init__(self)
        self.porta = "COM5"
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

    def moveFoco(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" FOCO MOVER = " + str(position) + "\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat        

    def focoUp(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" FOCO AUMENTAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def focodOWN(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" FOCO DIMINUIR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def focoRefPos(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" FOCO REFINAR+\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def focoRefNeg(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" FOCO REFINAR-\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

                    
    def prog_parar(self):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" FOCO PARAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def lampNEON(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" LAMP_NE LIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def lampNEOFF(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" LAMP_NE DESLIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def lampHEON(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" LAMP_HE LIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def lampHEOFF(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" LAMP_HE DESLIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def esp_lamp_avanc(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" ESP_LAMP AVANCAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def esp_lamp_rec(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" ESP_LAMP RECUAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def esp_lamp_off(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" ESP_LAMP DESLIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def espA(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" ESPELHO A\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def espB(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" ESPELHO B\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def espC(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" ESPELHO C\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def rot_ler(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" ROTATOR LER\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def rot_test(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" ROTATOR TESTAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def vent_on(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" VENTILADOR LIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def vent_off(self, position):
        if not self.errorDome:
            ret = 'ACK' in self.writeCommand(self.device+" VENTILADOR DESLIGAR\r")
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

TuboThread = threading.Thread(target = TuboControll, args=[])
TuboThread.start()