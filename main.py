"""
TCS-bancada is a software that emulates the TCSPD for testing in OPD's eletronic laboratory
"""
import sys
import os
import datetime
import ephem
import serial.tools.list_ports

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer,  pyqtSlot, QSettings, QThreadPool
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMessageBox
import controller.MoveAxis as AxisDevice
import controller.Dome as Dome
import controller.Tubo as Tubo

main_window_file = "main.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(main_window_file)

settings_ui_file = 'settings.ui'
formSettings, baseSettings = uic.loadUiType(settings_ui_file)

class SettingsWindow(baseSettings, formSettings):
    """Settings window for configuration of files and com ports"""
    def __init__(self):
        super(baseSettings, self).__init__()
        self.setupUi(self)

        list_baund_rates = ['2400', '4800', '9600', '115200']
        self.boxBaund.clear()
        self.boxBaund.addItems(list_baund_rates)

        list_com_portsorts = self.ports()
        self.boxPort.clear()
        self.boxPort.addItems(list_com_portsorts)

        self.get_settings_values()

        #load settings
        self.txtLogPath.setText(self.setting_variables.value("log"))
        self.txtBSCpath.setText(self.setting_variables.value("bsc"))
        if (self.setting_variables.value("comport"))>0:
            self.boxPort.setCurrentIndex(int(self.setting_variables.value("comport")))
        else:
            self.boxPort.setCurrentIndex(0)

        if self.setting_variables.value("baund")>0:
            self.boxBaund.setCurrentIndex(int(self.setting_variables.value("baund")))
        else:
            self.boxBaund.setCurrentIndex(0)

        #butons
        self.btnsave_settings.clicked.connect(self.save_settings)
        self.btnCancelSettings.clicked.connect(self.cancel_btn)

    def get_settings_values(self):
        """get saved settings"""
        self.setting_variables = QSettings('my app', 'variables')

    def save_settings(self):
        """save port and file settings"""
        self.setting_variables.setValue("comport", self.boxPort.currentIndex())
        self.setting_variables.setValue("baund", self.boxBaund.currentIndex())
        self.setting_variables.setValue("bsc", self.txtBSCpath.text())
        self.setting_variables.setValue("log", self.txtLogPath.text())

    def cancel_btn(self):
        """cancels and do not save any change"""
        #load settings
        self.txtLogPath.setText(self.setting_variables.value("log"))
        self.txtBSCpath.setText(self.setting_variables.value("bsc"))
        if (self.setting_variables.value("comport"))>0:
            self.boxPort.setCurrentIndex(int(self.setting_variables.value("comport")))
        else:
            self.boxPort.setCurrentIndex(0)

        if self.setting_variables.value("baund")>0:
            self.boxBaund.setCurrentIndex(int(self.setting_variables.value("baund")))
        else:
            self.boxBaund.setCurrentIndex(0)
        self.close()

    def ports(self):
        """list forts availables"""
        list_com_ports = serial.tools.list_ports.comports()
        connected = []
        for element in list_com_ports:
            connected.append(element.device)

        return connected

    def close_event(self, event):
        """closes setting window"""
        event.accept()

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    """main window"""
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.settings_window = SettingsWindow()
        self.thread_manager = QThreadPool()

        global statbuf
        statbuf = None
        self.device = None
        self.opd_device = None

        #clear prog erros
        self.actionLimpar.triggered.connect(self.clear_error_bit)
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionDisconnect.triggered.connect(self.disconnect_device)

        #connect devices
        self.btnStartAH.clicked.connect(self.connect_ah)
        self.btnStartDEC.clicked.connect(self.connect_dec)
        self.btnStartDome.clicked.connect(self.connect_dome)
        self.btnStartTubo.clicked.connect(self.connect_tubo)

        #AH buttons
        self.btnPoint.clicked.connect(self.point)
        self.btnTracking.clicked.connect(self.tracking)
        self.btnStop.clicked.connect(self.stop)
        self.btnMoveRel.clicked.connect(self.mover_rel)

        #DEC buttons
        self.btnPoint_2.clicked.connect(self.point)
        self.btnStop_2.clicked.connect(self.stop)
        self.btnMoveRel_2.clicked.connect(self.mover_rel)

        #Dome Buttons
        self.btndome_cw.clicked.connect(self.dome_cw)
        self.btndome_ccw.clicked.connect(self.dome_ccw)
        self.btndome_stop.clicked.connect(self.dome_stop)
        self.btndome_rap.clicked.connect(self.dome_rap)
        self.btndome_jog.clicked.connect(self.dome_jog)
        self.btnDomeGo.clicked.connect(self.dome_move)
        self.btnShutter.clicked.connect(self.dome_shutter)
        self.btnLampON.clicked.connect(self.dome_flat_ligar)
        self.btnLampOff.clicked.connect(self.dome_flat_desligar)

        #Tubo buttons
        self.btnEspA.clicked.connect(self.espelho_a)
        self.btnEspB.clicked.connect(self.espelho_b)
        self.btnEspC.clicked.connect(self.espelho_c)
        self.btnRotLer.clicked.connect(self.rotator_ler)
        self.btnRotTest.clicked.connect(self.rotator_testar)
        self.btnFanON.clicked.connect(self.fan_on)
        self.btnFanOFF.clicked.connect(self.fan_off)
        self.btnFocoUp.clicked.connect(self.foco_up)
        self.btnFocoDown.clicked.connect(self.foco_down)
        self.btnRefUp.clicked.connect(self.ref_up)
        self.btnRefDown.clicked.connect(self.ref_down)
        self.btnNEON.clicked.connect(self.ne_on)
        self.btnNEOFF.clicked.connect(self.ne_off)
        self.btnHEON.clicked.connect(self.he_on)
        self.btnHEOFF.clicked.connect(self.he_off)
        self.brnFocoMover.clicked.connect(self.he_off)

        self.timer_update = QTimer()

        #precess
        self.btnPrecess.clicked.connect(self.select_precess)
        self.btnOpenbsc_file.clicked.connect(self.load_bsc_default)
        self.btnPrecess_2.clicked.connect(self.select_precess)
        self.btnOpenbsc_file_2.clicked.connect(self.load_bsc_default)

    def open_settings(self):
        """open settings window"""
        if self.settings_window.isVisible():
            self.settings_window.hide()
        else:
            self.settings_window.show()

    #Tubo
    def espelho_a(self):
        """A mirror"""
        self.opd_device.esp_a()

    def espelho_b(self):
        """B mirror"""
        self.opd_device.esp_b()

    def espelho_c(self):
        """C mirror"""
        self.opd_device.esp_c()

    def rotator_ler(self):
        """read rotator"""
        self.opd_device.rot_ler()

    def rotator_testar(self):
        """test rotator"""
        self.opd_device.rot_test()

    def fan_on(self):
        """turn fan on"""
        self.opd_device.vent_on()

    def fan_off(self):
        """turn fan off"""
        self.opd_device.vent_off()

    def foco_up(self):
        """moves focus up"""
        self.opd_device.foco_up()

    def foco_down(self):
        """moves focus down"""
        self.opd_device.foco_down()

    def ref_up(self):
        """moves fine pos path"""
        self.opd_device.foco_ref_pos()

    def ref_down(self):
        """moves fine negative path"""
        self.opd_device.foco_ref_neg()

    def ne_on(self):
        """neon light on"""
        self.opd_device.lamp_ne_on()

    def ne_off(self):
        """neon light off"""
        self.opd_device.lamp_ne_off()

    def he_on(self):
        """helium light on"""
        self.opd_device.lamp_he_on()

    def he_off(self):
        """helium light off"""
        self.opd_device.lamp_he_off()

    def mover_foco(self):
        """moves focus"""
        if "TUBO" in self.device:
            foco_pos = self.txtFocoPos.text()
            if len(foco_pos) > 0 and foco_pos.isdigit():
                self.opd_device.move_foco(foco_pos)

    #DOME
    def dome_cw(self):
        """clockwise movement"""
        self.opd_device.dome_cw()

    def dome_ccw(self):
        """counter-clockwise movement"""
        self.opd_device.dome_ccw()

    def dome_jog(self):
        """jog movement"""
        self.opd_device.dome_jog()

    def dome_rap(self):
        """rapid movement"""
        self.opd_device.dome_rap()

    def dome_stop(self):
        """stop any movement"""
        self.opd_device.prog_parar()

    def dome_flat_ligar(self):
        """turns lamp on"""
        lamp_stat = self.opd_device.dome_flat_ligar()
        if lamp_stat:
            self.statLamp.setStyleSheet("background-color: lightgreen")
        else:
            self.statLamp.setStyleSheet("background-color: indianred")

    def dome_flat_desligar(self):
        """turns lamp off"""
        lamp_stat = self.opd_device.dome_flat_desligar()
        if lamp_stat:
            self.statLamp.setStyleSheet("background-color: indianred")
        else:
            self.statLamp.setStyleSheet("background-color: lightgreen")

    def dome_move(self):
        """moves the dome"""
        pos_dome = self.txtPointDome.text()
        if pos_dome.isdigit():
            try:
                if statbuf[25] == "0":
                    self.opd_device.move_cup(int(pos_dome))
                else:
                    print("erro")

            except Exception as exc_error:
                print("error: ", exc_error)
        else:
            msg = "Ivalid position"
            self.show_dialog(msg)

    def dome_shutter(self):
        """opens or close based on statbuf"""
        if statbuf[19] == "0":
            self.opd_device.open_shutter()
        elif statbuf[19] == "1":
            self.opd_device.close_shutter()

    def connect_ah(self):
        """connect ah"""
        self.timer_update.timeout.connect(self.update_data)
        self.start_timer()
        self.device = "AH"
        self.label_sideral.setText("Sideral")
        self.label_manual.setText("Manual")
        self.opd_device = AxisDevice.AxisControll(self.device, self.settings_window.boxPort.currentText(),
                            int(self.settings_window.boxBaund.currentText()))

    def connect_dec(self):
        """connect dec"""
        self.timer_update.timeout.connect(self.update_data)
        self.start_timer()
        self.device = "DEC"
        self.label_sideral.setText("Sideral")
        self.label_manual.setText("Manual")
        self.opd_device = AxisDevice.AxisControll(self.device, self.settings_window.boxPort.currentText(),
                            int(self.settings_window.boxBaund.currentText()))

    def connect_dome(self):
        """connect dome"""
        self.timer_update.timeout.connect(self.update_data)
        self.start_timer()
        self.device = "CUP"
        self.label_sideral.setText("Trapeira")
        self.label_manual.setText("Paravento")
        self.opd_device = Dome.DomeControll(self.device, self.settings_window.boxPort.currentText(),
                            int(self.settings_window.boxBaund.currentText()))

    def connect_tubo(self):
        """connect Tubo"""
        self.timer_update.timeout.connect(self.update_data)
        self.start_timer()
        self.device = "TUBO"
        self.opd_device = Tubo.TuboControll(self.device, self.settings_window.boxPort.currentText(),
                            int(self.settings_window.boxBaund.currentText()))

    def clear_error_bit(self):
        """prog erros"""
        self.opd_device.prog_error()

    def mover_rel(self):
        """fine movement by indexer"""
        if "AH" in self.device:
            dest_rel = self.txtIndexer.text()
            if len(dest_rel) > 2:
                self.opd_device.mover_rel(dest_rel)
        if "DEC" in self.device:
            dest_rel = self.txtIndexer_2.text()
            if len(dest_rel) > 2:
                self.opd_device.mover_rel(dest_rel)

    def stop(self):
        """stop any movement and abort slew"""
        self.opd_device.prog_parar()
        if "AH" in self.device:
            self.opd_device.sideral_desligar()

    def tracking(self):
        """turns sidereal on and off"""
        if "AH" in self.device:
            if statbuf[19] == "0":
                self.opd_device.sideral_ligar()
            elif statbuf[19] == "1":
                self.opd_device.sideral_desligar()

    def disconnect_device(self):
        """discconect devices and resets controller"""
        self.timer_update.stop()
        self.opd_device.prog_parar()
        self.opd_device.close_port()

    def select_precess(self):
        """Grabs selected txt from table"""
        if "AH" in self.device:
            name_obj = ([item.text().split("\t")[0].strip() \
                for item in self.listWidget.selectedItems()])[0]
            ra_obj = ([item.text().split("\t")[1].strip() \
                for item in self.listWidget.selectedItems()])[0]
            if self.listWidget.selectedItems():
                self.set_precess(name_obj, ra_obj)
        if "DEC" in self.device:
            name_obj = ([item.text().split("\t")[0].strip() \
                for item in self.listWidget_2.selectedItems()])[0]
            ra_obj = ([item.text().split("\t")[1].strip() \
                for item in self.listWidget_2.selectedItems()])[0]
            if self.listWidget.selectedItems():
                self.set_precess(name_obj, ra_obj)

    def set_precess(self, name_obj, ra_obj):
        """Precess object and check if its above the Horizon"""
        if "AH" in self.device:
            self.txtPointRA.setText(ra_obj)
            self.txtPointOBJ.setText(name_obj)
        if "DEC" in self.device:
            self.txtPointDEC.setText(ra_obj)
            self.txtPointOBJ_2.setText(name_obj)

    def load_bsc_default(self):
        """load default star catalog"""
        ##################################################
        bsc_file = self.settings_window.txtBSCpath.text()
        #bsc_file = "C:\\Users\\User\\Documents\\BSC_08.txt"
        ##################################################
        if bsc_file and os.path.exists(bsc_file):
            data = open(str(bsc_file), 'r')
            data_list = data.readlines()
            if "AH" in self.device:
                self.listWidget.clear()
                for each_line in data_list :
                    new_hr_string = str(each_line.split("\t")[0:2]).replace("[","").replace("]","").\
                        replace("'","").replace(",", "\t")
                    if len(each_line.strip())!=0:
                        self.listWidget.addItem(new_hr_string.strip())

            if "DEC" in self.device:
                self.listWidget_2.setSortingEnabled(True)
                self.listWidget_2.clear()
                for each_line in data_list :
                    new_hr_string = str(each_line.split("\t")[0:3:2]).replace("[","").replace("]","").\
                        replace("'","").replace(",", "\t")
                    print(new_hr_string)
                    if len(each_line.strip())!=0 :
                        self.listWidget_2.addItem(new_hr_string.strip())

    def point(self):
        """Points the telescope to a given Target"""
        if "AH" in self.device:
            ra_txt = self.txtPointRA.text()
            if len(ra_txt) > 2:
                try:
                    if statbuf[25] == "0":
                        self.opd_device.sideral_ligar()
                        self.opd_device.mover_rap(ra_txt)
                    else:
                        print("erro")

                except Exception as exc_err:
                    print("error: ", exc_err)
            else:
                msg = "Ivalid RA"
                self.show_dialog(msg)
        elif "DEC" in self.device:
            dect_txt = self.txtPointDEC.text()
            if len(dect_txt) > 2:
                try:
                    if statbuf[25] == "0":
                        self.opd_device.mover_rap(dect_txt)
                    else:
                        print("erro")

                except Exception as exc_err:
                    print("error: ", exc_err)
            else:
                msg = "Ivalid DEC inputs"
                self.show_dialog(msg)

    def update_data(self):
        """    Update coordinates every 1s    """
        if "AH" in self.device or "DEC" in self.device:
            # year = datetime.datetime.now().strftime("%Y")
            # month = datetime.datetime.now().strftime("%m")
            # day = datetime.datetime.now().strftime("%d")
            # hours = datetime.datetime.now().strftime("%H")
            # minute = datetime.datetime.now().strftime("%M")
            utc_time = str(datetime.datetime.utcnow().strftime('%H:%M:%S'))

            #ephem
            gatech = ephem.Observer()
            gatech.lon, gatech.lat = '-45.5825', '-22.534444'
            #gatech.date = year+month+day+" "+hours+minute
            if "AH" in self.device:
                self.txtCoordLST.setText(str(gatech.sidereal_time()))
                self.txtCoordUTC.setText(utc_time)
            if "DEC" in self.device:
                self.txtCoordLST_2.setText(str(gatech.sidereal_time()))
                self.txtCoordUTC_2.setText(utc_time)

        #DATA
        self.get_status()
        if statbuf:
            self.txtProgStatus.setText(statbuf)
            if "*" in statbuf:
                self.bit_status()
                if "AH" in self.device:
                    self.ah_status()
                if "DEC" in self.device:
                    self.dec_stat()
                if "CUP" in self.device:
                    self.dome_stat()
                if "TUBO" in self.device:
                    self.tubo_status()

        if statbuf and self.checkBoxLog.isChecked():
            self.create_log_file()

    @pyqtSlot()
    def get_status(self):
        """calls threading stats"""
        self.thread_manager.start(self.get_prog_status)

    @pyqtSlot()
    def get_prog_status(self):
        """get statbuf from controller"""
        global statbuf
        statbuf = self.opd_device.progStatus()

    def bit_status(self):
        """sets the labels colors for each statbit"""
        if statbuf[13] == "1":
            self.stat1.setStyleSheet("background-color: lightgreen")
        else:
            self.stat1.setStyleSheet("background-color: indianred")
        if statbuf[14] == "1":
            self.stat2.setStyleSheet("background-color: lightgreen")
        else:
            self.stat2.setStyleSheet("background-color: indianred")
        if statbuf[15] == "1":
            self.stat3.setStyleSheet("background-color: lightgreen")
        else:
            self.stat3.setStyleSheet("background-color: indianred")
        if statbuf[16] == "1":
            self.stat4.setStyleSheet("background-color: lightgreen")
        else:
            self.stat4.setStyleSheet("background-color: indianred")
        if statbuf[17] == "1":
            self.stat5.setStyleSheet("background-color: lightgreen")
        else:
            self.stat5.setStyleSheet("background-color: indianred")
        if statbuf[19] == "1":
            self.stat6.setStyleSheet("background-color: lightgreen")
        else:
            self.stat6.setStyleSheet("background-color: indianred")
        if statbuf[21] == "1":
            self.stat7.setStyleSheet("background-color: lightgreen")
        else:
            self.stat7.setStyleSheet("background-color: indianred")
        if statbuf[22] == "1":
            self.stat8.setStyleSheet("background-color: lightgreen")
        else:
            self.stat8.setStyleSheet("background-color: indianred")
        if statbuf[23] == "1":
            self.stat9.setStyleSheet("background-color: lightgreen")
        else:
            self.stat9.setStyleSheet("background-color: indianred")
        if statbuf[24] == "1":
            self.stat10.setStyleSheet("background-color: lightgreen")
        else:
            self.stat10.setStyleSheet("background-color: indianred")
        if statbuf[25] == "1":
            self.stat11.setStyleSheet("background-color: lightgreen")
        else:
            self.stat11.setStyleSheet("background-color: indianred")
        if statbuf[26] == "1":
            self.stat12.setStyleSheet("background-color: lightgreen")
        else:
            self.stat12.setStyleSheet("background-color: indianred")
        if statbuf[27] == "1":
            self.stat13.setStyleSheet("background-color: lightgreen")
        else:
            self.stat13.setStyleSheet("background-color: indianred")

    def dec_stat(self):
        """shows dec statbuf"""
        self.txtCoordDec.setText(statbuf[0:11])

    def dome_stat(self):
        """shows dome statbuf"""
        self.txtCoordDome.setText(statbuf[0:11])

    def tubo_status(self):
        """shows tubo statbuf"""
        self.txtCoordTubo.setText(statbuf[0:11])

    def ah_status(self):
        """shows ah statbuf and check sideral stat"""
        self.txtCoordRA.setText(statbuf[0:11])
        if statbuf[19] == "1":
            self.btnTracking.setText("ON")
            self.btnTracking.setStyleSheet("background-color: lightgreen")
        else:
            self.btnTracking.setText("OFF")
            self.btnTracking.setStyleSheet("background-color: indianred")

    def create_log_file(self):
        """creates a log file"""
        year = datetime.datetime.now().strftime("%Y")
        month = datetime.datetime.now().strftime("%m")
        day = datetime.datetime.now().strftime("%d")
        hours = datetime.datetime.now().strftime("%H")
        minute = datetime.datetime.now().strftime("%M")
        seconds = datetime.datetime.now().strftime("%S")
        time_log = str(hours) + ":" + str(minute) + ":" + str(seconds)
        dir_log_file = self.settings_window.txtLogPath.text()
        log_file_name = "LOG - " + str(year) + "-" + str(month) + "-" + str(day) + ".txt"
        log_path = dir_log_file + log_file_name
        if os.path.exists(log_path):
            log_file = open(dir_log_file+log_file_name,"a+")
            log_file.write(time_log + " " + self.device + " = " + statbuf + "\n")
        else:
            try:
                log_file = open(dir_log_file+log_file_name,"w+")
                log_file.write(time_log + " " + self.device + " = " + statbuf + "\n")
            except Exception as exc_err:
                self.timer_update.stop()
                self.show_dialog("Diretório nao existe")
                print(exc_err)

    #simple timer (1s)
    def start_timer(self):
        self.timer_update.stop()
        self.timer_update.start(1000)

    def show_dialog(self, msg_error):
        """Simple dialog box"""
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        msg_box.setText(msg_error)
        msg_box.setWindowTitle("Warning")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.exec()

    def close_event(self, event):
        """shows a message to the user confirming closing application"""
        close = QMessageBox()
        close.setText("Are you sure?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()

        if close == QMessageBox.Yes:
            self.disconnect_device()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()

    window.show()
    sys.exit(app.exec_())
