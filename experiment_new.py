import random
import sys
import time
import threading
import serial.tools.list_ports
import csv
from itertools import zip_longest
import pyqtgraph as pg
from PyQt5 import QtGui, QtCore, uic
import icons

plot_data_nr=200

## TODO: promijeniti logiku kod zaustavljanja threada koji uzima podatke sa serije

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()

        #load gui from .ui file
        uic.loadUi('experiment.ui', self)


        #flag for connection checking -> enables disconnection with the same button
        self.connected=False
        #flag for recording control
        self.recording_flag=False

        # initial values for y axis
        self.y_max=6
        self.y_min=0

        # frequency rate of the incoming data
        self.refresh_rate=10

        # initialize data and time variables
        self.plot_data = []
        self.plot_time = []

        # callback functions
        # buttons
        self.btn_quit.clicked.connect(self.closeIt)
        self.btn_connect.clicked.connect(self.plotter)
        self.btn_save.clicked.connect(self.save_data)
        self.btn_recording.clicked.connect(self.recording_setup)
        # textbox
        self.box_y_max.editingFinished.connect(self.change_y_max)
        self.box_y_min.editingFinished.connect(self.change_y_min)
        self.box_refresh_rate.editingFinished.connect(self.change_refresh_rate)

        # postavljanje pocetnih vrijednosti y osi u boxove
        self.box_y_max.setText(str(self.y_max))
        self.box_y_min.setText(str(self.y_min))

        # postavljanje pocetne vrijednosti u refresh rate box
        self.box_refresh_rate.setText(str(self.refresh_rate))

        #PADAJUCI IZBORNIK
        self.serial_ports = self.serial_ports()
        self.comboBox.addItems([i.description for i in self.serial_ports])

        # Setiranje osi grafa
        self.graphicsView.setYRange(self.y_min,self.y_max)

    def serial_ports(self):
        return serial.tools.list_ports.comports()

    def plotter(self):
        if(self.connected==False):
            port=self.serial_ports[self.comboBox.currentIndex()].device
            self.serial_port=serial.Serial(port,115200)  # zasad je baudrate zaharkodiran
            time.sleep(4)
            self.change_refresh_rate()
            self.serial_port.flushInput()
            self.connected=True
            self.btn_connect.setText("Disconnect")
            self.stop_thread = False
            self.thread=threading.Thread(target=self.updater)
            self.thread.daemon=True
            self.plotting = threading.Thread(target=self.plot)
            self.plotting.deamon=True
            self.thread.start()

        else:
            self.stop_thread=True
            self.plotting_flag=False
            #wait for the thread to finish, otherwise error will occur
            while self.stop_thread:
                pass
            self.serial_port.close()
            self.connected=False
            self.btn_connect.setText("Connect")


    def updater(self):
        self.plot_data = []
        self.plot_time = []
        self.t0 = time.time()
        #set graph to initial state
        self.graphicsView.clear()
        self.curve = self.graphicsView.getPlotItem().plot()

        # start plotting thread
        self.plotting_flag=True
        self.plotting.start()

        #MOŽDA nam ne treba ova linija, odnosno treba drugačije postupiti
        self.serial_port.flushInput()

        while not self.stop_thread:
            self.serial_port.reset_input_buffer()
            data = self.serial_port.readline().decode().split('\r\n')
            data=data[0].split("/")
            if len(data)==2:
                t=float(data[0])
                value=float(data[1])
                self.plot_data.append(value)
                self.plot_time.append(t)
                if self.recording_flag:
                    self.data.append(value)
                    self.time.append(t)
                self.plot_data=self.plot_data[-plot_data_nr:]
                self.plot_time=self.plot_time[-plot_data_nr:]
        self.stop_thread=False

    def plot(self):
        period=0.15
        while self.plotting_flag:
            self.curve.setData(self.plot_time, self.plot_data)
            time.sleep(period)
        self.plotting_flag=False

    def save_data(self):
        # check if there is any data recorded
        try:
            filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '.csv')
            with open(filename[0], 'w',newline='') as csv_file:
                wr = csv.DictWriter(csv_file, fieldnames=["Data", "Time"])
                wr.writeheader()
                date_time = zip_longest(self.data,self.time)
                wr.writerows({'Data':row[0], 'Time':row[1]} for row in date_time)

        except:
            pass


    def recording_setup(self):
        if not self.recording_flag:
            self.btn_recording.setText("Stop recording")
            self.data = []
            self.time = []
            self.recording_flag=True
        else:
            self.btn_recording.setText("Start recording")
            self.recording_flag=False
    def change_y_max(self):
        try:
            self.y_max=float(self.box_y_max.text())
            self.graphicsView.setYRange(min(self.y_min, self.y_max),max(self.y_min, self.y_max))
        except:
            print("ERROR")
    def change_y_min(self):
        try:
            self.y_min=float(self.box_y_min.text())
            self.graphicsView.setYRange(min(self.y_min, self.y_max), max(self.y_min, self.y_max))
        except:
            print("ERROR")

    def change_refresh_rate(self):
        try:
            self.refresh_rate=int(self.box_refresh_rate.text())
            self.serial_port.flushOutput()
            self.serial_port.write((str(self.refresh_rate)+"\r\n").encode())
        except:
            print("ERROR")

    def closeIt(self):
        if self.connected==True:
            self.plotter()
        exit(0)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())