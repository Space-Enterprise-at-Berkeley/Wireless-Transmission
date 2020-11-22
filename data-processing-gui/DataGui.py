from  PyQt5.QtWidgets  import *
from  matplotlib.backends.backend_qt5agg  import  FigureCanvas
from  matplotlib.figure  import  Figure
import sys
import random
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import numpy as np
import ntpath
import matplotlib.pyplot as plt
import pandas as pd
from time import sleep
import os
import scipy as sc
from scipy.interpolate import interp1d
from numpy.fft import rfft, irfft
from scipy import signal
from scipy.signal import savgol_filter, lfilter
from statistics import mean
import random

class MyWidget(QMainWindow):
    def __init__(self):
        self.file, self.path = '', ''
        super().__init__()
        loadUi('dataanalysis.ui',self)
        #print(os.getcwd())
        self.select_button.clicked.connect(self.loadFile)
        self.highPressureConversionFunc = self.initHighPressure()
        self.sel_button.clicked.connect(self.sel_tank_data)
        self.sel_button_2.clicked.connect(self.sel_injector_data)
        self.sel_button_3.clicked.connect(self.sel_high)


    def loadFile(self):
        self.path = QFileDialog.getOpenFileName()[0]
        self.file = ntpath.basename(self.path)
        self.data_name_label.setText(self.file)
        self.highPressureConversionFunc = self.initHighPressure()
        self.read_data()
        #self.display_all_pressure(show_high=True)

    def sel_tank_data(self):
        text, ok = QInputDialog.getText(self, 'Select Box', 'Which Data do you want to view? L for Lox or P for Propane?')
        if ok:
            if text == 'L':
                self.datatype = 'lox'
            elif text == 'P':
                self.datatype = 'propane'
            else:
                QMessageBox.question(self, 'Notice!', "Invalid Input.", QMessageBox.Ok)
                self.datatype = ''
        if self.datatype == 'lox':
            self.display_pressure(self.time, self.lox_tank, [])
            self.new_data = self.detect_peaks(self.lox_tank)
            self.remove_lines()
            self.add_lines()
            self.edit_lines()
            self.values()
        elif self.datatype == 'propane':
            self.display_pressure(self.time, self.propane_tank, [])
            self.new_data = self.detect_peaks(self.propane_tank)
            self.remove_lines()
            self.add_lines()
            self.edit_lines()
            self.values()

    def sel_injector_data(self):
        text, ok = QInputDialog.getText(self, 'Select Box', 'Which Injector Data do you want to view? L for Lox or P for Propane?')
        if ok:
            if text == 'L':
                self.datatype = 'lox'
            elif text == 'P':
                self.datatype = 'propane'
            else:
                QMessageBox.question(self, 'Notice!', "Invalid Input.", QMessageBox.Ok)
                self.datatype = ''
        if self.datatype == 'lox':
            self.display_pressure(self.time, self.lox_injector, [])
            self.new_data = self.detect_peaks(self.lox_injector)
            self.remove_lines()
            self.add_lines()
            self.edit_lines()
            self.values()
        elif self.datatype == 'propane':
            self.display_pressure(self.time, self.propane_injector, [])
            self.new_data = self.detect_peaks(self.propane_injector)
            self.remove_lines()
            self.add_lines()
            self.edit_lines()
            self.values()

    def sel_high(self):
        self.display_pressure(self.time, self.high_pressure, [])
        self.new_data = self.detect_peaks(self.high_pressure)
        self.remove_lines()
        self.add_lines()
        self.edit_lines()
        self.values()

    def read_data(self):
        f = open(self.path)
        f.readline()
        data = pd.read_csv(f)
        #print(data)
        cols = data.columns.to_numpy()
        #print(cols)
        self.time = data["time elapsed"].to_numpy()# time
        #print(time)
        try:
            lox_tank_temp = data[" loxTreeTemp"].to_numpy()
            lox_heater_pwm = data[" loxTreeHeater"].to_numpy()  # high pt

        except:
            print("No tank temp or heater")
        self.lox_tank = data[" loxTankPressure"].to_numpy() # lox tank
        self.propane_tank = data[" propTankPressure"].to_numpy()  # propane tank
        self.lox_injector = data[" loxInjectorPressure"].to_numpy()  # lox injector
        self.propane_injector = data[" propInjectorPressure"].to_numpy() #propane injector
        self.high_pressure = data[" highPressure"].to_numpy() #high pressure

        self.propane_injector, indices = self.clean_data(self.propane_injector)
        self.lox_injector, indices = self.clean_data(self.lox_injector)
        self.propane_tank, indices = self.clean_data(self.propane_tank)
        self.lox_tank, indices = self.clean_data(self.lox_tank)
        self.high_pressure, indices = self.clean_data(self.high_pressure) 
        self.time = [t for ind, t in enumerate(self.time) if ind in indices]


        lox_tank2 = []
        prop_tank2 = []
        lox_inj2 = []
        prop_inj2 = []
        high_tank2 = []
        for i in self.lox_tank:
            lox_tank2.append(self.lowPressureConversion(float(i)))
        for i in self.propane_tank:
            prop_tank2.append(self.lowPressureConversion(float(i)))
        for i in self.lox_injector:
            lox_inj2.append(self.lowPressureConversion(float(i)))
        for i in self.propane_injector:
            prop_inj2.append(self.lowPressureConversion(float(i)))
        for i in self.high_pressure:
            high_tank2.append(float(self.highPressureConversionFunc(float(i))))
        self.lox_tank = lox_tank2
        self.propane_tank = prop_tank2
        self.lox_injector = lox_inj2
        self.propane_injector = prop_inj2
        self.high_pressure = high_tank2

    def display_all_pressure(self, start_time = 0, end_time = -1, show_high=False):
        plt.figure(figsize=(20,10))
        indices = np.arange(len(self.time))
        start_index, _ = self.find_closest_element(self.time, start_time)
        if end_time != -1:
            end_index, _ = self.find_closest_element(self.time, end_time)
        else:
            end_index = -1
        print("start: {}, end: {}".format(start_index, end_index))
        plt.xlabel("time (s)")
        plt.ylabel("PSI")
        plt.plot(self.time[start_index:end_index], self.lox_tank[start_index:end_index], label='LOX tank')
        plt.plot(self.time[start_index:end_index], self.propane_tank[start_index:end_index], label='prop tank')
        plt.plot(self.time[start_index:end_index], self.lox_injector[start_index:end_index], label='lox inj')
        plt.plot(self.time[start_index:end_index], self.propane_injector[start_index:end_index], label='prop inj')
        if(show_high):
            plt.plot(self.time[start_index:end_index], self.high_pressure[start_index:end_index], label='Pressurant Tank')
        plt.legend()
        plt.show()

    def display_pressure(self, time, data, peaks):
        self.mplwid.canvas.axes.clear()
        self.mplwid.canvas.axes.plot(time, data)
        for i in peaks:
            for t in i:
                self.mplwid.canvas.axes.axvline(t, c='k', lw='1')
        self.mplwid.canvas.draw()

    def detect_peaks(self, pdata):
        #time = data[0]
        #pdata = data[1]
        #print("Amount of Data Points:", len(pdata))
        n = 100  # the larger n is, the smoother curve will be
        b = [1.0 / n] * n
        a = 1
        filter_data2 = lfilter(b,a,pdata)
        dary = np.array([*map(float, pdata)])
        dary -=np.average(dary)
        step = np.hstack((np.ones(len(dary)), -1*np.ones(len(dary))))

        dary_step = np.convolve(dary, step, mode='valid')
        peaksall=[]
        peaks = signal.find_peaks(dary_step, width=20)[0]
        #print("first round peaks:", peaks)
        if len(peaks)>0:
            for p in peaks:

                peaksall.append(np.array([p]))
        ##adding 0 to peaks in case empty
        elif len(peaks)==0:
            peaks=[0]

        #print("Positive Peaks:", len(peaks))
        peaks2 = signal.find_peaks(-dary_step, width=20)[0]
        #print("Negative Peaks:", len(peaks2))
        if len(peaks2)>0:
            for p in peaks2:

                peaksall.append(np.array([p]))
        #print("Total Peaks detected:", len(peaksall))
        peaksall.sort()
        #print(peaksall)
        plt.figure()

        plt.plot(dary)

        plt.plot(dary_step/10)

        for ii in range(len(peaks)):
            plt.plot((peaks[ii], peaks[ii]), (-1500, 1500), 'r')

        #plt.show()
        ##start of second round
        #creating new data set with first and last peak as lower, upper bounds
        if len(peaksall)>=2:
            data2 = pdata[int(peaksall[0][0]):int(peaksall[-1][-1])]
        else:
            data2 = pdata[0:int(peaksall[-1])]
        ##
        n = 5  # the larger n is, the smoother curve will be
        b = [1.0 / n] * n
        a = 1
        #filter_data = lfilter(b,a,data2)
        ##
        dary2 = np.array([*map(float, data2)])

        dary2 -=np.average(dary2)
        step2 = np.hstack((np.ones(len(dary2)), -1*np.ones(len(dary2))))

        dary_step2 = np.convolve(dary2, step2, mode='valid')

        # Get the peaks of the convolution
        #negative peaks
        peaks3 = signal.find_peaks(-dary_step2, width=20)[0]
        #positive peaks
        peaks4 = signal.find_peaks(dary_step2, width=20)[0]
        #adjusting for frame shift
        if len(peaksall)>=2:
            if len(peaks3)>0:
                for p in range(len(peaks3)):
                    peaksall.append(np.array([peaks3[p]+peaks[0]+1]))
                #peaksall.append(peaks3+peaks+1)
            #print("Negative Peaks Detected:", len(peaks3), "at", peaks3)
            if len(peaks4)>0:
                for p in range(len(peaks4)):
                    peaksall.append(np.array([peaks4[p]+peaks[0]+1]))
                #peaksall.append(peaks4+peaks+1)
            #print("Positive Peaks Detected:", len(peaks4), "at", peaks4)
            #print(peaksall)
        else:
            if len(peaks3)>0:
                for p in range(len(peaks3)):
                    peaksall.append(np.array([peaks3[p]]))
            #print("Negative Peaks Detected:", len(peaks3),"at",peaks3)
            if len(peaks4)>0:
                for p in peaks4:

                    peaksall.append(np.array([p]))
            #print("Positive Peaks Detected:", len(peaks4),"at", peaks4)
            #print(peaksall)
        ###make this more robust
        #peaks2 = signal.find_peaks(-dary_step, width=20)[0]
        #print(peaks3)

        # plots
        plt.figure()

        plt.plot(dary2)
        #orange:
        plt.plot(dary_step2/10)
        #repeat process on dary data:
        n = 20  # the larger n is, the smoother curve will be
        b = [1.0 / n] * n
        a = 1
        filter_data3 = lfilter(b,a,dary_step2/10)
        peaks40 = signal.find_peaks(filter_data3, width=20)[0]
        peaks30 = signal.find_peaks(-1*filter_data3, width=20)[0]
        peaksall2=[]
        plt.plot(filter_data3)
        for ii in range(len(peaks40)):
            plt.plot((peaks40[ii], peaks40[ii]), (-150, 150), 'green')
        ##adding to master graph
        if len(peaksall)>=2:
            if len(peaks30)>0:
                for p in range(len(peaks30)):
                    #print("testing peaks:",peaks)
                    #print("testing peaks30:", peaks30)
                    peaksall2.append(np.array([peaks30[p]+peaks[0]+1]))
        #           print("testing something:", np.array([peaks30[p]+peaks[p]+1]))
                #peaksall2.append(peaks30+peaks+1)
        #    print("Negative Peaks Detected:", len(peaks30), "at", peaks30)
            if len(peaks40)>0:
                for p in range(len(peaks40)):
                    peaksall2.append(np.array([peaks40[p]+peaks[0]+1]))
                #peaksall2.append(peaks40+peaks+1)
        #         print("Positive Peaks Detected:", len(peaks40), "at", peaks40)
        #         print("This is peaksall2:",peaksall2)
        else:
            if len(peaks30)>0:
                for p in peaks30:
                    peaksall2.append(np.array([p]))
                #peaksall2.append(peaks30)
            #print("Negative Peaks Detected:", len(peaks30),"at",peaks30)
            if len(peaks40)>0:
                for p in peaks40:
                    peaksall.append(np.array([p]))
                #peaksall2.append(peaks40)
            #print("Positive Peaks Detected:", len(peaks40),"at", peaks40)
            #print(peaksall2)
        ## appending 2nd round of lines to first

        peaksall = peaksall + peaksall2
        #print("This is peaksall:", peaksall)
        peaksall.sort()


        for ii in range(len(peaks3)):
            plt.plot((peaks3[ii], peaks3[ii]), (-150, 150), 'r')

        #plt.show()

        ##end of second round
        #print("end of second round")

        ##start of third round
        #creating new data set with first and last peak as lower, upper bounds
        if len(peaksall)>=2:
            data2 = pdata[int(peaksall[0][0]):int(peaksall[2][-1])]
        else:
            data2 = pdata[0:int(peaksall[-1])]
        ##
        n = 5  # the larger n is, the smoother curve will be
        b = [1.0 / n] * n
        a = 1
        filter_data4 = lfilter(b,a,data2)
        ##
        dary2 = np.array([*map(float, filter_data4)])

        dary2 -=np.average(dary2)
        step2 = np.hstack((np.ones(len(dary2)), -1*np.ones(len(dary2))))

        dary_step2 = np.convolve(dary2, step2, mode='valid')

        # Get the peaks of the convolution
        #negative peaks
        peaks3 = signal.find_peaks(-dary_step2, width=20)[0]
        #positive peaks
        peaks4 = signal.find_peaks(dary_step2, width=20)[0]
        #adjusting for frame shift
        if len(peaksall)>=2:
            if len(peaks3)>0:
                for p in range(len(peaks3)):
                    peaksall.append(np.array([peaks3[p]+peaks[0]+1]))
                #peaksall.append(peaks3+peaks+1)
            #print("Negative Peaks Detected:", len(peaks3), "at", peaks3)
            if len(peaks4)>0:
                for p in range(len(peaks4)):
                    peaksall.append(np.array([peaks4[p]+peaks[0]+1]))
                #peaksall.append(peaks4+peaks+1)
            #print("Positive Peaks Detected:", len(peaks4), "at", peaks4)
            #print(peaksall)
        else:
            if len(peaks3)>0:
                for p in range(len(peaks3)):
                    peaksall.append(np.array([peaks3[p]]))
            print("Negative Peaks Detected:", len(peaks3),"at",peaks3)
            if len(peaks4)>0:
                for p in peaks4:

                    peaksall.append(np.array([p]))
            #print("Positive Peaks Detected:", len(peaks4),"at", peaks4)
            #print(peaksall)
        ###make this more robust
        #peaks2 = signal.find_peaks(-dary_step, width=20)[0]
        #print(peaks3)

        # plots
        plt.figure()

        plt.plot(dary2)
        #orange:
        plt.plot(dary_step2/10)

        peaksall.sort()


        for ii in range(len(peaks3)):
            plt.plot((peaks3[ii], peaks3[ii]), (-150, 150), 'r')

        #plt.show()

        ##end of third round
        #print("end of third round")


        #peak_times = [time[peak[0]] for peak in peaksall]


        #display_pressure(time, pdata, peak_times)
        self.mplwid.canvas.axes.clear()
        self.mplwid.canvas.axes.plot(pdata)
        for i in peaksall:
            for t in i:
                self.mplwid.canvas.axes.axvline(t, c='k', lw='1')
        self.mplwid.canvas.draw()

        return [pdata,peaksall]

    def find_closest_element(self, collection, val):
        index = min(range(len(collection)), key=lambda i: abs(collection[i]-val))
        return index, collection[index]

    def tank_injector_diff(self, Injector, Tank, time):
        differential = []
        for i in range(600, len(Injector)):
            differential.append(Tank[i] - Injector[i])
        plt.plot(time[600:], differential)
        plt.ylabel('Differential')
        plt.xlabel('Time Elapsed')
        plt.title('Tank Injector Differential')
        plt.show()

    def clean_data(self, data):
        templist = list(data)
        newlist = [x for x in templist if str(x)!='nan']
        indices = [ind for ind, x in enumerate(templist) if str(x)!='nan']
        return np.array(newlist), np.array(indices)

    def lowPressureConversion(self, raw):  # raw is a value from 0 to 1024 (10bit ADC)
        return 1.2258857538273733 * raw * (1024 / pow(2, 23)) - 123.89876445934394

    def highPressureConversion(self, raw):  # raw is a value from 0 to 1024 (10bit ADC)
        return self.highPressureConversionFunc(raw)

    def initHighPressure(self):
        data = pd.read_csv(
            os.getcwd() + "/waterflow_test/high_pt_characterization_10_10")
        highPressureConversionFunc = interp1d(
            data['raw'], data['digital'], kind='quadratic')
        print('hi')
        # print(type(highPressureConversionFunc))
        # print(highPressureConversionFunc(900))
        return highPressureConversionFunc

    def remove_lines(self):
        ##plotting input data

        peaksall = self.new_data[1] # actual times, not indices.

        data = self.new_data[0]
        #print(peaksall)
        #plt.plot(data)
        #for i in peaksall:
        #    for t in i:
        #        plt.axvline(t, c='k', lw='1')
        #plt.show()
        #display_pressure(time, data, peaksall)

        ##taking user input and removing lines
        user_input, _ = QInputDialog.getText(self, 'Select Box', "Index of line to be removed (starts at 0 like most lists), separated by comma, e.g. 53, 32, 9: (will find the closest line and remove it) ")
        if user_input:
            a_list =  list(map(int,user_input.split(',')))
            #print(a_list)
            #print(peaksall)

            #removing lines at index indicated by user input, using inserts to maintain list length in process
            for t in a_list:
                #i, _ = find_closest_element(peaksall, t)
                del peaksall[t]
                peaksall.insert(t, 69.69)

            #display_pressure(time, data, peaksall)

            peaksall = [x for x in peaksall if x!=69.69]\

            self.mplwid.canvas.axes.clear()
            self.mplwid.canvas.axes.plot(data)
            for i in peaksall:
                for t in i:
                    self.mplwid.canvas.axes.axvline(t, c='k', lw='1')
            self.mplwid.canvas.draw()
            self.new_data = [data, peaksall]

    def add_lines(self):
        ##plotting input data

        peaksall = self.new_data[1]
        data = self.new_data[0]


        #print(peaksall)
        #plt.figure(dpi=100)
        #plt.plot(data)
        #for i in peaksall:
        #    for t in i:
        #        plt.axvline(t, c='k', lw='1')
        #plt.show()

        ##adding new lines with user input

        user_input3, _ = QInputDialog.getText(self, 'Select Box', "List of lines to add, by approximate X axis value (can edit later for precision):")

        if user_input3:
            new_lines =  list(map(int,user_input3.split(',')))

            for i in new_lines:
                peaksall.append(np.array([i]))

            self.mplwid.canvas.axes.clear()
            self.mplwid.canvas.axes.plot(data)
            for i in peaksall:
                for t in i:
                    self.mplwid.canvas.axes.axvline(t, c='k', lw='1')
            self.mplwid.canvas.draw()

        peaksall.sort()
        self.new_data = [data, peaksall]

    def edit_lines(self):
        self.reset()
        peaksall = self.new_data[1]
        data = self.new_data[0]


        ###shifting lines with user input
        #print(peaksall)
        user_input2, _ = QInputDialog.getText(self, 'Select Box', "Times of lines to edit, separated by comma, e.g. 103, 58, 12: ")

        if user_input2:
            time_list =  list(map(int,user_input2.split(',')))
            #index_list = [find_closest_element(time, t)[0] for t in time_list]
            #print(index_list)

            for i in time_list:

                self.x_label_2.setText(str(i-5))
                self.x_label_3.setText(str(i-4))
                self.x_label_4.setText(str(i-3))
                self.x_label_5.setText(str(i-2))
                self.x_label_6.setText(str(i-1))
                self.x_label_7.setText(str(i))
                self.x_label_8.setText(str(i+1))
                self.x_label_9.setText(str(i+2))
                self.x_label_10.setText(str(i+3))
                self.x_label_11.setText(str(i+4))
                self.x_label_12.setText(str(i+5))
                self.y_label_2.setText(str(data[i-5]))
                self.y_label_3.setText(str(data[i-4]))
                self.y_label_4.setText(str(data[i-3]))
                self.y_label_5.setText(str(data[i-2]))
                self.y_label_6.setText(str(data[i-1]))
                self.y_label_7.setText(str(data[i]))
                self.y_label_8.setText(str(data[i+1]))
                self.y_label_9.setText(str(data[i+2]))
                self.y_label_10.setText(str(data[i+3]))
                self.y_label_11.setText(str(data[i+4]))
                self.y_label_12.setText(str(data[i+5]))

                user_input3, _ = QInputDialog.getText(self, 'Select Box', "Choose time for new line")
                self.reset()
                if user_input3:
                    #peak_i, _ = find_closest_element(peaksall, time[i])
                    peaksall.remove(i)
                    peaksall.insert(i, np.array([float(user_input3)]))
                else:
                    None


        #display_pressure(time, data, peaksall)
        self.mplwid.canvas.axes.clear()
        self.mplwid.canvas.axes.plot(data)
        for i in peaksall:
            for t in i:
                self.mplwid.canvas.axes.axvline(t, c='k', lw='1')
        self.mplwid.canvas.draw()

        peaksall.sort()
        self.new_data = [data, peaksall]

    ##function for returning values
    def values(self):
        ##plotting input data
        ##data[0] = pressure data
        ##data[1] = array of detected peaks
        peaksall = self.new_data[1]
        data = self.new_data[0]
              
        ##taking input on data type and returning parameters according to data type
        ##can probably be done with radios in gui
        self.static_label.setText("Static:")
        self.dyn_label.setText("Dynamic:")
        self.et_label.setText("Emptying Time:")
        self.droop_label.setText("Droop:")
        self.roi_label.setText("Rate of Increase:")

        done = False
        while done == False:
            data_type, ok = QInputDialog.getText(self, 'Select Box', "Data Type (high, injector, or tank)")
            if ok:
                if "tank" in data_type:
                    static_start_index = int(peaksall[0][0])
                    static_end_index = int(peaksall[1][0])
                    dynamic_start_index= int(peaksall[2][0])
                    dynamic_end_index = int(peaksall[3][0])
                    
                    #print(static_start_index, static_end_index)
                    static_condition = data[static_start_index:static_end_index]
                    static_pressure = mean(static_condition)
                    self.static_change.setText(str(static_pressure))
                    dynamic_condition = data[dynamic_start_index: dynamic_end_index]
                    dynamic_pressure = mean(dynamic_condition)
                    self.dyn_change.setText(str(dynamic_pressure))
                    droop = static_pressure - dynamic_pressure
                    self.dr_change.setText(str(droop))
                    emptying_time = self.time[int(peaksall[3][0])]-self.time[int(peaksall[2][0])]
                    self.emp_change.setText(str(emptying_time))
                    dynamic_rate_of_increase = (data[dynamic_end_index]-data[dynamic_start_index])/emptying_time
                    self.roi_change.setText(str(dynamic_rate_of_increase))
                    return [emptying_time, dynamic_rate_of_increase, dynamic_pressure, static_pressure, droop, "NaN", "NaN"]
                elif "injector" or "high" in data_type:
                    dynamic_start_index= int(peaksall[0][0])
                    dynamic_end_index = int(peaksall[1][0])
                    
                    dynamic_condition = data[dynamic_start_index: dynamic_end_index]
                    #print("All Peaks:", peaksall)
                    self.static_change.setText("NaN")
                    dynamic_pressure = mean(dynamic_condition)
                    self.dyn_change.setText(str(dynamic_pressure))
                    emptying_time = self.time[int(peaksall[1][0])]-self.time[int(peaksall[0][0])]
                    self.emp_change.setText(str(emptying_time))
                    dynamic_rate_of_increase = (data[dynamic_end_index]-data[dynamic_start_index])/emptying_time
                    self.roi_change.setText(str(dynamic_rate_of_increase))
                    self.dr_change.setText("NaN")
                    if "high" in data_type:
                        pressure_drop = (data[dynamic_start_index]-data[dynamic_end_index])
                        self.droop_label.setText("Pressure Drop:")
                        self.dr_change.setText(str(pressure_drop))
                        return [emptying_time, dynamic_rate_of_increase, dynamic_pressure , "NaN", "NaN", pressure_drop, "NaN"]
                    return [emptying_time, dynamic_rate_of_increase, dynamic_pressure , "NaN", "NaN", "NaN", "NaN"]
                else:
                    QMessageBox.question(self, 'Notice!', "Invalid Input. Please re-enter", QMessageBox.Ok)
            else:
                QMessageBox.question(self, 'Notice!', "Invalid Input. Please re-enter", QMessageBox.Ok)

    def reset(self):
        self.x_label_2.setText("")
        self.x_label_3.setText("")
        self.x_label_4.setText("")
        self.x_label_5.setText("")
        self.x_label_6.setText("")
        self.x_label_7.setText("")
        self.x_label_8.setText("")
        self.x_label_9.setText("")
        self.x_label_10.setText("")
        self.x_label_11.setText("")
        self.x_label_12.setText("")
        self.y_label_2.setText("")
        self.y_label_3.setText("")
        self.y_label_4.setText("")
        self.y_label_5.setText("")
        self.y_label_6.setText("")
        self.y_label_7.setText("")
        self.y_label_8.setText("")
        self.y_label_9.setText("")
        self.y_label_10.setText("")
        self.y_label_11.setText("")
        self.y_label_12.setText("")
     

app = QApplication([])
widget = MyWidget()
widget.show()
app.setStyle('Fusion')
sys.exit(app.exec_())
