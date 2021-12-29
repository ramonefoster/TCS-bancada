import sys, os
import time
import ephem
import datetime

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QTimer, QDateTime, QObject, QThread, pyqtSignal, QUrl, pyqtSlot, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QStyle, QWidget, QLabel, QLineEdit, QTextEdit, QGridLayout, QMessageBox
import controller.MoveAxis as AxisDevice
import controller.Dome as Dome

pyQTfileName = "main.ui" 
Ui_MainWindow, QtBaseClass = uic.loadUiType(pyQTfileName)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        global device
        device = "NONE"

        #clear prog erros
        self.actionLimpar.triggered.connect(self.clearBits)

        #connect devices
        self.btnStartAH.clicked.connect(self.connAH)
        self.btnStartDEC.clicked.connect(self.connDEC)
        self.btnStartDome.clicked.connect(self.connDome)

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

        self.timerUpdate = QTimer()
        self.timerUpdate.timeout.connect(self.updateData)
        self.startTimer()

        #precess
        self.btnPrecess.clicked.connect(self.selectToPrecess)
        self.btnOpenBSCfile.clicked.connect(self.loadBSCdefault)
        self.btnPrecess_2.clicked.connect(self.selectToPrecess)
        self.btnOpenBSCfile_2.clicked.connect(self.loadBSCdefault)

    def DomeCW(self):
        self.DeviceOPD.DomeCW()
    
    def DomeCCW(self):
        self.DeviceOPD.DomeCCW()
    
    def DomeJOG(self):
        self.DeviceOPD.DomeJOG()
    
    def domeRAP(self):
        self.DeviceOPD.DomeRAP()
    
    def domeStop(self):
        self.DeviceOPD.stopDome()
    
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
        device = "AH"
        self.label_sideral.setText("Sideral")
        self.DeviceOPD = AxisDevice.AxisControll(device)
    
    def connDEC(self):
        device = "DEC"
        self.label_sideral.setText("Sideral")
        self.DeviceOPD = AxisDevice.AxisControll(device)
    
    def connDome(self):
        device = "CUP"
        self.label_sideral.setText("Trapeira")
        self.DeviceOPD = Dome.DomeControll(device)
    
    # def connTubo(self):
    #     device = "TUBO"
    #     self.DeviceOPD = EixoAH.AHControll(device)

    def clearBits(self):
        self.DeviceOPD.progErros()
    
    def moverRel(self):
        if "AH" in device:
            destRel = self.txtIndexer.text()
            if len(destRel) > 2:
                self.DeviceOPD.mover_rel(destRel)
        if "DEC" in device:
            destRel = self.txtIndexer_2.text()
            if len(destRel) > 2:
                self.DeviceOPD.mover_rel(destRel)        

    #stop any movement and abort slew
    def stop(self):
        self.DeviceOPD.prog_parar()
        if "AH" in device:
            self.DeviceOPD.sideral_desligar()

    def tracking(self):
        if "AH" in device:
            if statbuf[19] == "0":
                self.DeviceOPD.sideral_ligar()
            elif statbuf[19] == "1":
                self.DeviceOPD.sideral_desligar()
        

    #Grabs text from txt
    def selectToPrecess(self): 
        if "AH" in device:        
            nameObj = ([item.text().split("\t")[0].strip() for item in self.listWidget.selectedItems()])[0]
            raObj = ([item.text().split("\t")[1].strip() for item in self.listWidget.selectedItems()])[0] 
            self.setPrecess(nameObj, raObj)
        if "DEC" in device:
            nameObj = ([item.text().split("\t")[0].strip() for item in self.listWidget_2.selectedItems()])[0]
            raObj = ([item.text().split("\t")[1].strip() for item in self.listWidget_2.selectedItems()])[0] 
            self.setPrecess(nameObj, raObj)       
        
    
    #Precess object and check if its above the Horizon
    def setPrecess(self, nameObj, raObj): 
        if "AH" in device:
            self.txtPointRA.setText(raObj)
            self.txtPointOBJ.setText(nameObj)
        if "DEC" in device:
            self.txtPointDEC.setText(raObj)
            self.txtPointOBJ_2.setText(nameObj)

    def loadBSCdefault(self):  
        ##################################################       
        BSCfile = "C:\\Users\\User\\Documents\\BSC_08.txt"
        ##################################################
        if BSCfile: 
            print(BSCfile)
            data = open(str(BSCfile), 'r')
            dataList = data.readlines()

            if "AH" in device:
                self.listWidget.clear()
                for eachLine in dataList :
                    if len(eachLine.strip())!=0 :
                        self.listWidget.addItem(eachLine.strip().split()[1]) 
            if "DEC" in device:
                self.listWidget_2.clear()
                for eachLine in dataList :
                    if len(eachLine.strip())!=0 :
                        self.listWidget_2.addItem(eachLine.strip().split()[2]) 

    #Points the telescope to a given Target
    def point(self):
        if "AH" in device:
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
        elif "DEC" in device:
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
        if "AH" in device or "DEC" in device:
            year = datetime.datetime.now().strftime("%Y")
            month = datetime.datetime.now().strftime("%m")
            day = datetime.datetime.now().strftime("%d")
            hours = datetime.datetime.now().strftime("%H")
            minute = datetime.datetime.now().strftime("%M")
            utcTime = str(datetime.datetime.utcnow().strftime('%H:%M:%S'))
            
            #ephem
            gatech = ephem.Observer()
            gatech.lon, gatech.lat = '-45.5825', '-22.534444'
            #gatech.date = year+month+day+" "+hours+minute
            if "AH" in device:
                self.txtCoordLST.setText(str(gatech.sidereal_time()))
                self.txtCoordUTC.setText(utcTime)
            if "DEC" in device:
                self.txtCoordLST_2.setText(str(gatech.sidereal_time()))
                self.txtCoordUTC_2.setText(utcTime)      
        
        #AH DATA
        global statbuf
        statbuf = self.DeviceOPD.progStatus()
        self.txtProgStatus.setText(statbuf)
        if "*" in statbuf:
            self.bitStats()
            if "AH" in device:
                self.AHstat()
            if "DEC" in device:
                self.DECstat()

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
        self.txtCoordDEC.setText(statbuf[0:11])
            
    def AHstat(self):        
        self.txtCoordRA.setText(statbuf[0:11])
        if statbuf[19] == "1":
            self.btnTracking.setText("ON")
            self.btnTracking.setStyleSheet("background-color: lightgreen")
        else:
            self.btnTracking.setText("OFF")
            self.btnTracking.setStyleSheet("background-color: indianred")
        

    #simple timer (1s)
    def startTimer(self):
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
