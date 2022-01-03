import sys, os
import time
import ephem
import datetime
import serial.tools.list_ports

from PyQt5 import QtCore, QtGui, QtWidgets, uic, QtSerialPort
from PyQt5.QtCore import QTimer, QDateTime, QObject, QThread, pyqtSignal, QUrl, pyqtSlot, Qt, QSettings
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QStyle, QWidget, QLabel, QLineEdit, QTextEdit, QGridLayout, QMessageBox
import controller.MoveAxis as AxisDevice
import controller.Dome as Dome
import controller.Tubo as Tubo

pyQTfileName = "main.ui" 
Ui_MainWindow, QtBaseClass = uic.loadUiType(pyQTfileName)

SettingsUI = 'settings.ui'
formSettings, baseSettings = uic.loadUiType(SettingsUI)

class SettingsWindow(baseSettings, formSettings):
    def __init__(self):
        super(baseSettings, self).__init__()
        self.setupUi(self)

        listBaundRates = ['2400', '4800', '9600', '115200']
        self.boxBaund.clear()
        self.boxBaund.addItems(listBaundRates) 

        listPorts = self.ports()
        self.boxPort.clear()
        self.boxPort.addItems(listPorts)

        self.getSettingsValue() 

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
        self.btnSaveSettings.clicked.connect(self.saveSettings)
        self.btnCancelSettings.clicked.connect(self.cancelBtn)

    def getSettingsValue(self):
        self.setting_variables = QSettings('my app', 'variables')
    
    def saveSettings(self):
        self.setting_variables.setValue("comport", self.boxPort.currentIndex())
        self.setting_variables.setValue("baund", self.boxBaund.currentIndex())
        self.setting_variables.setValue("bsc", self.txtBSCpath.text())
        self.setting_variables.setValue("log", self.txtLogPath.text())

    def cancelBtn(self):
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
        listP = serial.tools.list_ports.comports()
        connected = []
        for element in listP:
            connected.append(element.device)

        return(connected)
    
    def closeEvent(self, event):
        event.accept()
        

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.settingsWin = SettingsWindow()
        
        self.device = "NONE"         

        #clear prog erros
        self.actionLimpar.triggered.connect(self.clearBits)
        self.actionSettings.triggered.connect(self.openSettings)

        #connect devices
        self.btnStartAH.clicked.connect(self.connAH)
        self.btnStartDEC.clicked.connect(self.connDEC)
        self.btnStartDome.clicked.connect(self.connDome)
        self.btnStartTubo.clicked.connect(self.connTubo)

        #AH buttons
        self.btnPoint.clicked.connect(self.point)
        self.btnTracking.clicked.connect(self.tracking)
        self.btnStop.clicked.connect(self.stop) 
        self.btnMoveRel.clicked.connect(self.moverRel)

        #DEC buttons
        self.btnPoint_2.clicked.connect(self.point)
        self.btnStop_2.clicked.connect(self.stop) 
        self.btnMoveRel_2.clicked.connect(self.moverRel)

        #Dome Buttons
        self.btnDomeCW.clicked.connect(self.DomeCW)
        self.btnDomeCCW.clicked.connect(self.DomeCCW)
        self.btnDomeStop.clicked.connect(self.domeStop)
        self.btnDomeRap.clicked.connect(self.domeRAP)
        self.btnDomeJog.clicked.connect(self.DomeJOG)
        self.btnDomeGo.clicked.connect(self.domeMove)    
        self.btnShutter.clicked.connect(self.domeShutter)
        self.btnLampON.clicked.connect(self.domeFlatOn)
        self.btnLampOff.clicked.connect(self.domeFlatOff)

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

        self.timerUpdate = QTimer()

        #precess
        self.btnPrecess.clicked.connect(self.selectToPrecess)
        self.btnOpenBSCfile.clicked.connect(self.loadBSCdefault)
        self.btnPrecess_2.clicked.connect(self.selectToPrecess)
        self.btnOpenBSCfile_2.clicked.connect(self.loadBSCdefault)

    def openSettings(self, checked):
        if self.settingsWin.isVisible():
            self.settingsWin.hide()
        else:
            self.settingsWin.show()

    #Tubo
    def espelho_a(self):
        self.DeviceOPD.espA()
    
    def espelho_b(self):
        self.DeviceOPD.espB()
    
    def espelho_c(self):
        self.DeviceOPD.espC()
    
    def rotator_ler(self):
        self.DeviceOPD.rot_ler()

    def rotator_testar(self):
        self.DeviceOPD.rot_test()

    def fan_on(self):
        self.DeviceOPD.vent_on()

    def fan_off(self):
        self.DeviceOPD.vent_off()

    def foco_up(self):
        self.DeviceOPD.focoUp()

    def foco_down(self):
        self.DeviceOPD.focodOWN()

    def ref_up(self):
        self.DeviceOPD.focoRefPos()
    
    def ref_down(self):
        self.DeviceOPD.focoRefNeg()
    
    def ne_on(self):
        self.DeviceOPD.lampNEON()
    
    def ne_off(self):
        self.DeviceOPD.lampNEOFF()

    def he_on(self):
        self.DeviceOPD.lampHEON()

    def he_off(self):
        self.DeviceOPD.lampHEOFF()
    
    def mover_foco(self):
        if "TUBO" in self.device:
            foco_pos = self.txtFocoPos.text()
            if len(foco_pos) > 0 and foco_pos.isdigit():
                self.DeviceOPD.mover_rel(foco_pos)
        
    #DOME
    def DomeCW(self):
        self.DeviceOPD.DomeCW()
    
    def DomeCCW(self):
        self.DeviceOPD.DomeCCW()
    
    def DomeJOG(self):
        self.DeviceOPD.DomeJOG()
    
    def domeRAP(self):
        self.DeviceOPD.DomeRAP()
    
    def domeStop(self):
        self.DeviceOPD.prog_parar()
    
    def domeFlatOn(self):
        lampStat = self.DeviceOPD.DomeFlatLampON()
        if lampStat:
            self.statLamp.setStyleSheet("background-color: lightgreen")
        else:
            self.statLamp.setStyleSheet("background-color: indianred")
    
    def domeFlatOff(self):
        lampStat = self.DeviceOPD.DomeFlatLampOFF()
        if lampStat:
            self.statLamp.setStyleSheet("background-color: indianred")
        else:
            self.statLamp.setStyleSheet("background-color: lightgreen")
    
    def domeMove(self):
        posDome = self.txtPointDome.text()
        if posDome.isdigit():            
            try:            
                if statbuf[25] == "0":
                    self.DeviceOPD.moveCup(int(posDome))
                else:
                    print("erro")
                            
            except Exception as e:               
                print("error: ", e)                
        else:
            msg = "Ivalid position"
            self.showDialog(msg)
    
    def domeShutter(self):
        if statbuf[19] == "0":
            self.DeviceOPD.openShutter()
        elif statbuf[19] == "1":
            self.DeviceOPD.CloseShutter() 

    def connAH(self):
        self.timerUpdate.timeout.connect(self.updateData)
        self.startTimer()
        self.device = "AH"
        self.label_sideral.setText("Sideral")
        self.label_manual.setText("Manual")  
        self.DeviceOPD = AxisDevice.AxisControll(self.device, self.settingsWin.boxPort.currentText(), int(self.settingsWin.boxBaund.currentText()))
    
    def connDEC(self):
        self.timerUpdate.timeout.connect(self.updateData)
        self.startTimer()
        self.device = "DEC"
        self.label_sideral.setText("Sideral")
        self.label_manual.setText("Manual")  
        self.DeviceOPD = AxisDevice.AxisControll(self.device, self.settingsWin.boxPort.currentText(), int(self.settingsWin.boxBaund.currentText()))
    
    def connDome(self):
        self.timerUpdate.timeout.connect(self.updateData)
        self.startTimer()
        self.device = "CUP"
        self.label_sideral.setText("Trapeira")
        self.label_manual.setText("Paravento")        
        self.DeviceOPD = AxisDevice.AxisControll(self.device, self.settingsWin.boxPort.currentText(), int(self.settingsWin.boxBaund.currentText()))
    
    def connTubo(self):
        self.timerUpdate.timeout.connect(self.updateData)
        self.startTimer()
        self.device = "TUBO"
        self.DeviceOPD = AxisDevice.AxisControll(self.device, self.settingsWin.boxPort.currentText(), int(self.settingsWin.boxBaund.currentText()))

    def clearBits(self):
        self.DeviceOPD.progErros()
    
    def moverRel(self):
        if "AH" in self.device:
            destRel = self.txtIndexer.text()
            if len(destRel) > 2:
                self.DeviceOPD.mover_rel(destRel)
        if "DEC" in self.device:
            destRel = self.txtIndexer_2.text()
            if len(destRel) > 2:
                self.DeviceOPD.mover_rel(destRel)        

    #stop any movement and abort slew
    def stop(self):
        self.DeviceOPD.prog_parar()
        if "AH" in self.device:
            self.DeviceOPD.sideral_desligar()

    def tracking(self):
        if "AH" in self.device:
            if statbuf[19] == "0":
                self.DeviceOPD.sideral_ligar()
            elif statbuf[19] == "1":
                self.DeviceOPD.sideral_desligar()
        

    #Grabs text from txt
    def selectToPrecess(self): 
        if "AH" in self.device:        
            nameObj = ([item.text().split("\t")[0].strip() for item in self.listWidget.selectedItems()])[0]
            raObj = ([item.text().split("\t")[1].strip() for item in self.listWidget.selectedItems()])[0]
            if self.listWidget.selectedItems(): 
                self.setPrecess(nameObj, raObj)
        if "DEC" in self.device:
            nameObj = ([item.text().split("\t")[0].strip() for item in self.listWidget_2.selectedItems()])[0]
            raObj = ([item.text().split("\t")[1].strip() for item in self.listWidget_2.selectedItems()])[0] 
            if self.listWidget.selectedItems(): 
                self.setPrecess(nameObj, raObj)     
        
    
    #Precess object and check if its above the Horizon
    def setPrecess(self, nameObj, raObj): 
        if "AH" in self.device:
            self.txtPointRA.setText(raObj)
            self.txtPointOBJ.setText(nameObj)
        if "DEC" in self.device:
            self.txtPointDEC.setText(raObj)
            self.txtPointOBJ_2.setText(nameObj)

    def loadBSCdefault(self):  
        ##################################################
        BSCfile = self.settingsWin.txtBSCpath.text()       
        #BSCfile = "C:\\Users\\User\\Documents\\BSC_08.txt"
        ##################################################
        if BSCfile and os.path.exists(BSCfile):             
            data = open(str(BSCfile), 'r')
            dataList = data.readlines()
            if "AH" in self.device:
                self.listWidget.clear()
                for eachLine in dataList :
                    newHRstring = str(eachLine.split("\t")[0:2]).replace("[","").replace("]","").replace("'","").replace(",", "\t")
                    if len(eachLine.strip())!=0 :                        
                        self.listWidget.addItem(newHRstring.strip()) 
                    
            if "DEC" in self.device:
                self.listWidget_2.setSortingEnabled(True)
                self.listWidget_2.clear()
                for eachLine in dataList :
                    newHRstring = str(eachLine.split("\t")[0:3:2]).replace("[","").replace("]","").replace("'","").replace(",", "\t")
                    print(newHRstring)
                    if len(eachLine.strip())!=0 :
                        self.listWidget_2.addItem(newHRstring.strip())  

    #Points the telescope to a given Target
    def point(self):
        if "AH" in self.device:
            raTxt = self.txtPointRA.text()
            if len(raTxt) > 2:            
                try:            
                    if statbuf[25] == "0":
                        self.DeviceOPD.sideral_ligar()
                        self.DeviceOPD.mover_rap(raTxt)
                    else:
                        print("erro")
                            
                except Exception as e:               
                    print("error: ", e)                
            else:
                msg = "Ivalid RA"
                self.showDialog(msg)
        elif "DEC" in self.device:
            decTxt = self.txtPointDEC.text()
            if len(decTxt) > 2:            
                try:            
                    if statbuf[25] == "0":
                        self.DeviceOPD.mover_rap(decTxt)
                    else:
                        print("erro")
                            
                except Exception as e:               
                    print("error: ", e)                
            else:
                msg = "Ivalid DEC inputs"
                self.showDialog(msg)

    #Update coordinates every 1s
    def updateData(self):
        if "AH" in self.device or "DEC" in self.device:
            # year = datetime.datetime.now().strftime("%Y")
            # month = datetime.datetime.now().strftime("%m")
            # day = datetime.datetime.now().strftime("%d")
            # hours = datetime.datetime.now().strftime("%H")
            # minute = datetime.datetime.now().strftime("%M")
            utcTime = str(datetime.datetime.utcnow().strftime('%H:%M:%S'))
            
            #ephem
            gatech = ephem.Observer()
            gatech.lon, gatech.lat = '-45.5825', '-22.534444'
            #gatech.date = year+month+day+" "+hours+minute
            if "AH" in self.device:
                self.txtCoordLST.setText(str(gatech.sidereal_time()))
                self.txtCoordUTC.setText(utcTime)
            if "DEC" in self.device:
                self.txtCoordLST_2.setText(str(gatech.sidereal_time()))
                self.txtCoordUTC_2.setText(utcTime)      
        
        #AH DATA
        global statbuf
        statbuf = self.DeviceOPD.progStatus()
        self.txtProgStatus.setText(statbuf)
        if "*" in statbuf:
            self.bitStats()
            if "AH" in self.device:
                self.AHstat()
            if "DEC" in self.device:
                self.DECstat()
            if "CUP" in self.device:
                self.Domestat()
            if "TUBO" in self.device:
                self.Tubostat()
            
        if statbuf and self.checkBoxLog.isChecked():
            self.createLofFile()

    def bitStats(self):
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

    def DECstat(self):
        self.txtCoordDec.setText(statbuf[0:11])
    
    def Domestat(self):
        self.txtCoordDome.setText(statbuf[0:11])
    
    def Tubostat(self):
        self.txtCoordTubo.setText(statbuf[0:11])
            
    def AHstat(self):        
        self.txtCoordRA.setText(statbuf[0:11])
        if statbuf[19] == "1":
            self.btnTracking.setText("ON")
            self.btnTracking.setStyleSheet("background-color: lightgreen")
        else:
            self.btnTracking.setText("OFF")
            self.btnTracking.setStyleSheet("background-color: indianred")
    
    def createLofFile(self):
        year = datetime.datetime.now().strftime("%Y")
        month = datetime.datetime.now().strftime("%m")
        day = datetime.datetime.now().strftime("%d")
        hours = datetime.datetime.now().strftime("%H")
        minute = datetime.datetime.now().strftime("%M")
        seconds = datetime.datetime.now().strftime("%S")
        time_log = str(hours) + ":" + str(minute) + ":" + str(seconds)
        dirFile = self.settingsWin.txtLogPath.text()
        fileName = "LOG - " + str(year) + "-" + str(month) + "-" + str(day) + ".txt"
        pathFile = dirFile + fileName
        if os.path.exists(pathFile):
            f = open(dirFile+fileName,"a+")
            f.write(time_log + " " + self.device + " = " + statbuf + "\n")
        else:
            try:
                f = open(dirFile+fileName,"w+")
                f.write(time_log + " " + self.device + " = " + statbuf + "\n")
            except Exception as e:
                self.timerUpdate.stop()
                self.showDialog("Diretório nao existe")
                
    #simple timer (1s)
    def startTimer(self):
        self.timerUpdate.stop()
        self.timerUpdate.start(1000)      

    def showDialog(self, msgError):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setText(msgError)
        msgBox.setWindowTitle("Warning")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec()

    def closeEvent(self, event):
        close = QMessageBox()
        close.setText("Are you sure?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()

        if close == QMessageBox.Yes:            
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()

    window.show()
    sys.exit(app.exec_())
