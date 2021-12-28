import sys, os
import time
import ephem
import datetime

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QTimer, QDateTime, QObject, QThread, pyqtSignal, QUrl, pyqtSlot, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QStyle, QWidget, QLabel, QLineEdit, QTextEdit, QGridLayout, QMessageBox
import controller.MoveAxis as EixoAH

pyQTfileName = "main.ui" 
Ui_MainWindow, QtBaseClass = uic.loadUiType(pyQTfileName)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.AHx = EixoAH.AHControll()

        self.actionLimpar.triggered.connect(self.clearBits)

        #Telescope buttons
        self.btnPoint.clicked.connect(self.point)
        self.btnTracking.clicked.connect(self.tracking)
        self.btnStop.clicked.connect(self.stop) 
        self.btnMoveRel.clicked.connect(self.moverRel)

        self.timerUpdate = QTimer()
        self.timerUpdate.timeout.connect(self.updateData)
        self.startTimer()

        #precess
        self.btnPrecess.clicked.connect(self.selectToPrecess)
        self.btnOpenBSCfile.clicked.connect(self.loadBSCdefault)

    def clearBits(self):
        self.AHx.progErros()
    
    def moverRel(self):
        destRel = self.txtIndexer.text()
        if len(destRel) > 2:
            self.AHx.mover_rel(destRel)

    #stop any movement and abort slew
    def stop(self):
        self.AHx.prog_parar()
        self.AHx.sideral_desligar()

    def tracking(self):
        if statbuf[19] == "0":
            self.AHx.sideral_ligar()
        elif statbuf[19] == "1":
            self.AHx.sideral_desligar()
        

    #Grabs text from txt
    def selectToPrecess(self):         
        nameObj = ([item.text().split("\t")[0].strip() for item in self.listWidget.selectedItems()])[0]
        raObj = ([item.text().split("\t")[1].strip() for item in self.listWidget.selectedItems()])[0]        
        magObj = ([item.text().split("\t")[3].strip() for item in self.listWidget.selectedItems()])[0]
        
        self.setPrecess(nameObj, raObj, magObj)
    
    #Precess object and check if its above the Horizon
    def setPrecess(self, nameObj, raObj, magObj): 
        self.txtPointRA.setText(raObj)
        self.txtPointOBJ.setText(nameObj)
        self.txtPointMag.setText(magObj)    

    def loadBSCdefault(self):  
        ##################################################       
        BSCfile = "C:\\Users\\User\\Documents\\BSC_08.txt"
        ##################################################
        if BSCfile: 
            print(BSCfile)
            data = open(str(BSCfile), 'r')
            dataList = data.readlines()

            self.listWidget.clear()

            for eachLine in dataList :
                if len(eachLine.strip())!=0 :
                    self.listWidget.addItem(eachLine.strip()) 

    #Points the telescope to a given Target
    def point(self):
        raTxt = self.txtPointRA.text()
        if len(raTxt) > 2:            
            try:            
                if statbuf[15] == "0":
                    self.AHx.sideral_ligar()
                    self.AHx.mover_rap(raTxt)
                    print("Foi")
                else:
                    print("erro AH")
                        
            except Exception as e:               
                print("error: ", e)                
        else:
            msg = "Ivalid RA or DEC inputs"
            self.showDialog(msg)
    

    #Update coordinates every 1s
    def updateData(self):
        year = datetime.datetime.now().strftime("%Y")
        month = datetime.datetime.now().strftime("%m")
        day = datetime.datetime.now().strftime("%d")
        hours = datetime.datetime.now().strftime("%H")
        minute = datetime.datetime.now().strftime("%M")
        utcTime = str(datetime.datetime.utcnow().strftime('%H:%M:%S'))
        self.txtCoordUTC.setText(utcTime)
        #ephem
        gatech = ephem.Observer()
        gatech.lon, gatech.lat = '-45.5825', '-22.534444'
        #gatech.date = year+month+day+" "+hours+minute
        self.txtCoordLST.setText(str(gatech.sidereal_time()))
        #AH DATA
        global statbuf
        statbuf = self.AHx.progStatus()
        self.txtProgStatus.setText(statbuf)
        if "*" in statbuf:
            self.txtCoordRA.setText(statbuf[0:11])
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
                self.btnTracking.setText("ON")
                self.btnTracking.setStyleSheet("background-color: lightgreen")
            else:
                self.stat6.setStyleSheet("background-color: indianred")
                self.btnTracking.setText("OFF")
                self.btnTracking.setStyleSheet("background-color: indianred")
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
        self.AHx.closePort()

        if close == QMessageBox.Yes:            
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()

    window.show()
    sys.exit(app.exec_())
