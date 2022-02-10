import serial
import threading
import serial.tools.list_ports
import time

class DomeControll(threading.Thread):
    def __init__(self, device, port, baund):
        threading.Thread.__init__(self)
        self.porta = port
        self.baundRate = baund
        self.port=self.porta 
        #DOME 
        self.device = device      
        print(device)

        self.result = self.com_ports()

        self.error_device = False

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
                    self.error_device = False
                except Exception as e:
                    self.error_device = True                    
        else:
            print('Cannot connect to: ', self.porta)
            self.error_device = True

    def close_port(self):
        if self.ser:
            self.ser.close()

    def com_ports(self):
            self.list = serial.tools.list_ports.com_ports()
            self.connected = []
            for element in self.list:
                self.connected.append(element.device)

            return(self.connected)

    def prog_status(self): 
        if self.error_device:
            return("+0 00 00.00 *0000000000000000")
        else:        
            try:  
                ack = self.write_cmd(self.device+" PROG STATUS\r")

                if len(ack) > 2:
                    return(ack)    
                else:
                    print("prog_status bug")
                    #print(ack)
                    return("+0 00 00.00 *0000000000000000")
            except Exception as e:
                print(e)
                return("+0 00 00.00 *0000000000000000")

    def move_cup(self, position):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" DOMO MOVER = " + str(position) + "\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat        

    def open_shutter(self):
        if not self.error_device:
            bitTrap = self.prog_status()[4]
            if bitTrap == "1" :
                ret = 'ACK' in self.write_cmd(self.device+" TRAPEIRA ABRIR\r")
                if ret:
                    stat = True
                else:
                    stat = False
                return stat           

    def close_shutter(self):
        if not self.error_device:
            bitTrap = self.prog_status()[4]
            if bitTrap == "1" :
                ret = 'ACK' in self.write_cmd(self.device+" TRAPEIRA FECHAR\r")
                if ret:
                    stat = True
                else:
                    stat = False
                return stat

    def dome_cw(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" DOMO GIRAR_CW\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def dome_ccw(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" DOMO GIRAR_CCW\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def dome_jog(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" DOMO LIGAR_JOG\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def dome_rap(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" DOMO LIGAR_RAP\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def dome_flat_ligar(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" FLAT_WEAK LIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
            
    def dome_flat_desligar(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" FLAT_WEAK DESLIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def prog_error(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" PROG ERROS\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat 
                    
    def prog_parar(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" DOMO PARAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
            
    def write_cmd(self, cmd):
        if not self.error_device:
            try:
                self.ser.flushOutput()
                self.ser.flushInput()
                self.ser.write(cmd.encode())
                timeout_device = time.time()
                ack = ''
                while '\r' not in ack:
                    ack += self.ser.read().decode()
                    if (time.time() - timeout_device) > 1:
                        self.ser.flushInput()
                        self.ser.flushOutput()
                        return ack
                print(ack)    
                return(ack)
            except Exception as e:
                print(e)
                return('NAK')

DomeThread = threading.Thread(target = DomeControll, args=[])
DomeThread.start()