#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.WARNING)

import xmlrpc.client
import requests, sys, os
from json import loads
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QFontDatabase
from datetime import datetime,timezone

def relpath(filename):
		try:
			base_path = sys._MEIPASS # pylint: disable=no-member
		except:
			base_path = os.path.abspath(".")
		return os.path.join(base_path, filename)

def load_fonts_from_dir(directory):
		families = set()
		for fi in QDir(directory).entryInfoList(["*.ttf", "*.woff", "*.woff2"]):
			_id = QFontDatabase.addApplicationFont(fi.absoluteFilePath())
			families |= set(QFontDatabase.applicationFontFamilies(_id))
		return families

class MainWindow(QtWidgets.QMainWindow):
    """http://www.dxsummit.fi/api/v1/spots?include=14MHz&include_modes=CW,PHONE&limit_time=true&refresh=1636741291778"""
    dxsummiturl="http://www.dxsummit.fi/api/v1/spots"
    spotsorteddic={}
    rigctl_addr = "localhost"
    rigctl_port = 12345
    bw = {}
    lastclicked = ""

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(self.relpath("dialog.ui"), self)
        self.listWidget.clicked.connect(self.spotclicked)
        self.comboBox_band.currentTextChanged.connect(self.getspots)
        self.comboBox_mode.currentTextChanged.connect(self.getspots)
        self.server = xmlrpc.client.ServerProxy(f"http://{self.rigctl_addr}:{self.rigctl_port}")


    def relpath(self, filename):
        try:
            base_path = sys._MEIPASS # pylint: disable=no-member
        except:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, filename)

    """
    {"info": "TNX GENNADY DSW 73DXDETEXAS LARRY", "dx_country": "Asiatic Russia", "de_latitude": 31.92, "dx_latitude": 56.22,
    "dx_longitude": -73.27, "de_call": "K5SNA-@", "frequency": 14074.0, "time": "2021-09-15T02:42:18", "dx_call": "UA9MA",
    "de_longitude": 96.23, "id": 52387129}
    """ 

    def getspots(self):
        self.time.setText(str(datetime.now(timezone.utc)).split()[1].split(".")[0][0:5])
        spots = False
        try:
            URL = self.dxsummiturl
            if self.comboBox_mode.currentText() != "All":
                URL += "?include_modes="+self.comboBox_mode.currentText()
            request=requests.get(URL,timeout=15.0)
            spots = loads(request.text)
            self.listWidget.clear()
        except:
            return
        justonce=[]
        count = 0
        for i in spots:
            if self.comboBox_band.currentText() == 'All' or self.getband(i['frequency']) == self.comboBox_band.currentText():
                if i['dx_call'] in justonce:
                    continue
                count += 1
                if count > 20:
                    return
                justonce.append(i['dx_call'])
                #summit = i['dx_country']
                if i['time'] == None or i['de_call'] == None or i['dx_call'] == None or i['dx_country'] == None or i['frequency'] == None:
                    continue
                spot = f"{i['time'][11:16]}  {i['de_call'].ljust(10)}  {i['dx_call'].rjust(10)}  {i['dx_country'].ljust(20)}  {i['frequency']}"
                self.listWidget.addItem(spot)
                if spot[5:] == self.lastclicked[5:]:
                    founditem = self.listWidget.findItems(spot[5:], QtCore.Qt.MatchFlag.MatchContains)
                    founditem[0].setSelected(True)

    def spotclicked(self):
        """
        If rigctld is running on this PC, tell it to tune to the spot freq.
        Otherwise die gracefully.
        """
        try:
            item = self.listWidget.currentItem()
            self.lastclicked = item.text()
            line = item.text().split()
            logging.debug(line)
            freq = line[-1:][0].split(".")
            mode = None
            combfreq = freq[0]+freq[1].ljust(3,'0')
            self.server.rig.set_frequency(float(combfreq))
            if self.comboBox_mode.currentText() != "All":
                mode = self.comboBox_mode.currentText()
            if mode == 'PHONE':
                if int(combfreq) > 10000000:
                    mode = 'USB'
                else:
                    mode = 'LSB'
            if mode == None or mode == 'DIGI':
                return
            self.server.rig.set_mode(mode)
        except Exception as e:
            logging.warning(f"{e}")

    def getband(self, freq):
        """
        Convert a (string) frequency in hz into a (string) band.
        Returns a (string) band.
        Returns a "0" if frequency is out of band.
        """
        if freq:
            frequency = int(freq)*1000
            if frequency > 1800000 and frequency < 2000000:
                return "160"
            if frequency > 3500000 and frequency < 4000000:
                return "80"
            if frequency > 5330000 and frequency < 5406000:
                return "60"
            if frequency > 7000000 and frequency < 7300000:
                return "40"
            if frequency > 10100000 and frequency < 10150000:
                return "30"
            if frequency > 14000000 and frequency < 14350000:
                return "20"
            if frequency > 18068000 and frequency < 18168000:
                return "17"
            if frequency > 21000000 and frequency < 21450000:
                return "15"
            if frequency > 24890000 and frequency < 24990000:
                return "12"
            if frequency > 28000000 and frequency < 29700000:
                return "10"
            if frequency > 50000000 and frequency < 54000000:
                return "6"
            if frequency > 144000000 and frequency < 148000000:
                return "2"
        else:
            return "0"

app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion')
font_dir = relpath("font")
families = load_fonts_from_dir(os.fspath(font_dir))
logging.info(families)
window = MainWindow()
window.show()
window.getspots()
timer = QtCore.QTimer()
timer.timeout.connect(window.getspots)
timer.start(30000)
app.exec()