import serial
import threading
import serial.tools.list_ports
import time

class TuboControll(threading.Thread):
    def __init__(self, device, port, baund):
        threading.Thread.__init__(self)
        self.porta = port
        self.baundRate = baund
        self.port=self.porta 
        #DOME 
        self.device = device      

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

    def move_foco(self, position):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" FOCO MOVER = " + str(position) + "\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat        

    def foco_up(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" FOCO AUMENTAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def foco_down(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" FOCO DIMINUIR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def foco_ref_pos(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" FOCO REFINAR+\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def foco_ref_neg(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" FOCO REFINAR-\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

                    
    def prog_parar(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" FOCO PARAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def lamp_ne_on(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" LAMP_NE LIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def lamp_ne_off(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" LAMP_NE DESLIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def lamp_he_on(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" LAMP_HE LIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def lamp_he_off(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" LAMP_HE DESLIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def esp_lamp_avanc(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" ESP_LAMP AVANCAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat

    def esp_lamp_rec(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" ESP_LAMP RECUAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def esp_lamp_off(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" ESP_LAMP DESLIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def esp_a(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" ESPELHO A\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def esp_b(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" ESPELHO B\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def esp_c(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" ESPELHO C\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def rot_ler(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" ROTATOR LER\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def rot_test(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" ROTATOR TESTAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def vent_on(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" VENTILADOR LIGAR\r")
            if ret:
                stat = True
            else:
                stat = False
            return stat
    
    def vent_off(self):
        if not self.error_device:
            ret = 'ACK' in self.write_cmd(self.device+" VENTILADOR DESLIGAR\r")
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

TuboThread = threading.Thread(target = TuboControll, args=[])
TuboThread.start()