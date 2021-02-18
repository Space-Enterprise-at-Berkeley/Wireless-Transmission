import csv
import ntpath
import os
import random
import sys
from statistics import mean
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy as sc
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from numpy.fft import irfft, rfft
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from scipy import signal
from scipy.interpolate import interp1d
from scipy.signal import lfilter, savgol_filter


class MyWidget(QMainWindow):

    def __init__(self):
        self.file, self.path = '', ''
        super().__init__()
        loadUi('dataanalysis.ui', self)
        self.y_labels = [self.y_label_2, self.y_label_3, self.y_label_4, self.y_label_5, self.y_label_6,
                         self.y_label_7, self.y_label_8, self.y_label_9, self.y_label_10, self.y_label_11, self.y_label_12]
        self.x_labels = [self.x_label_2, self.x_label_3, self.x_label_4, self.x_label_5, self.x_label_6,
                         self.x_label_7, self.x_label_8, self.x_label_9, self.x_label_10, self.x_label_11, self.x_label_12]

        # print(os.getcwd())
        self.select_button.clicked.connect(self.loadFile)
        self.highPressureConversionFunc = self.initHighPressure()
        self.sel_button.hide()
        self.sel_button_2.hide()
        self.sel_button_3.hide()
        self.sel_button.clicked.connect(self.sel_tank_data)
        self.sel_button_2.clicked.connect(self.sel_injector_data)
        self.sel_button_3.clicked.connect(self.sel_high)
        self.save_data.clicked.connect(self.store)
        self.save_data.hide();
        self.mul_sel.clicked.connect(self.multiple_sel)

    def loadFile(self):
        self.path = QFileDialog.getOpenFileName()[0]
        self.file = ntpath.basename(self.path)
        if self.file[(len(self.file)-4):] == ".csv":
            try:
                self.data_name_label.setText(self.file)
                self.highPressureConversionFunc = self.initHighPressure()
                self.read_data()
                self.sel_button.show()
                self.sel_button_2.show()
                self.sel_button_3.show()
                # self.display_all_pressure(show_high=True)
            except:
                QMessageBox.question(
                    self, 'Notice!', "Wrong File Type or No File Selected.", QMessageBox.Ok)
        else:
            QMessageBox.question(
                self, 'Notice!', "Wrong File Type or No File Selected.", QMessageBox.Ok)

    def sel_tank_data(self):
        self.type = 'tank'
        text, ok = QInputDialog.getText(
            self, 'Select Box', 'Which Data do you want to view? L for Lox or P for Propane?')
        if ok:
            if text == 'L':
                self.datatype = 'lox'
            elif text == 'P':
                self.datatype = 'propane'
            else:
                QMessageBox.question(
                    self, 'Notice!', "Invalid Input.", QMessageBox.Ok)
                self.datatype = ''
        if self.has_done_past():
            text, ok = QInputDialog.getText(
                self, 'Select Box', 'You have done this same analysis before. Would you like to see previous results? Y for Yes or N for No and continue the analysis')
            if ok:
                if text == 'Y':
                    self.load_old()
                else:
                    self.tank_process()
            else:
                self.tank_process()
        else:
            self.tank_process()

    def sel_injector_data(self):
        self.type = 'injector'
        text, ok = QInputDialog.getText(
            self, 'Select Box', 'Which Injector Data do you want to view? L for Lox or P for Propane? (Defaults to Lox)')
        if ok:
            if text == 'L':
                self.datatype = 'lox'
            elif text == 'P':
                self.datatype = 'propane'
            else:
                QMessageBox.question(
                    self, 'Notice!', "Invalid Input.", QMessageBox.Ok)
                self.datatype = 'lox'
        else:
            self.datatype = 'lox'

        if self.has_done_past():
            text, ok = QInputDialog.getText(
                self, 'Select Box', 'You have done this same analysis before. Would you like to see previous results? Y for Yes or N for No and continue the analysis')
            if ok:
                if text == 'Y':
                    self.load_old()
                else:
                    self.inj_process()
            else:
                self.inj_process()
        else:
            self.inj_process()

    def process(self):
        self.remove_lines()
        self.add_lines()
        self.edit_lines()
        self.values()
        self.save_data.show();

    def sel_high(self):

        self.type = 'high'
        self.datatype = 'high'
        if self.has_done_past():
            text, ok = QInputDialog.getText(self, 'Select Box', 'You have done this same analysis before. Would you like to see previous results? Y for Yes or N for No and continue the analysis')
            if ok:
                if text == 'Y':
                    self.load_old()
                else:
                    self.display_pressure(self.time, self.high_pressure, [])
                    self.new_data = self.detect_peaks(self.high_pressure)
                    self.process()
            else:
                self.display_pressure(self.time, self.high_pressure, [])
                self.new_data = self.detect_peaks(self.high_pressure)
                self.process()
        else:
            self.display_pressure(self.time, self.high_pressure, [])
            self.new_data = self.detect_peaks(self.high_pressure)
            self.process()

    def tank_process(self):
        if self.datatype == 'lox':
            self.display_pressure(self.time, self.lox_tank, [])
            self.new_data = self.detect_peaks(self.lox_tank)
            self.process()
        elif self.datatype == 'propane':
            self.display_pressure(self.time, self.propane_tank, [])
            self.new_data = self.detect_peaks(self.propane_tank)
            self.process()

    def inj_process(self):
        if self.datatype == 'lox':
            self.display_pressure(self.time, self.lox_injector, [])
            self.new_data = self.detect_peaks(self.lox_injector)
            self.process()
        elif self.datatype == 'propane':
            self.display_pressure(self.time, self.propane_injector, [])
            self.new_data = self.detect_peaks(self.propane_injector)
            self.process()

    def read_data(self):
        f = open(self.path)
        f.readline()
        data = pd.read_csv(f)
        # print(data)
        cols = data.columns.to_numpy()
        # print(cols)
        self.time = data["time elapsed"].to_numpy()  # time
        # print(time)
        try:
            lox_tank_temp = data[" loxTreeTemp"].to_numpy()
            lox_heater_pwm = data[" loxTreeHeater"].to_numpy()  # high pt

        except:
            print("No tank temp or heater")
        try:
            self.lox_tank = data[" loxTankPressure"].to_numpy()  # lox tank
            # propane tank
            self.propane_tank = data[" propTankPressure"].to_numpy()
            # lox injector
            self.lox_injector = data[" loxInjectorPressure"].to_numpy()
            # propane injector
            self.propane_injector = data[" propInjectorPressure"].to_numpy()
            # high pressure
            self.high_pressure = data[" highPressure"].to_numpy()

            self.propane_injector, indices = self.clean_data(
                self.propane_injector)
            self.lox_injector, indices = self.clean_data(self.lox_injector)
            self.propane_tank, indices = self.clean_data(self.propane_tank)
            self.lox_tank, indices = self.clean_data(self.lox_tank)
            self.high_pressure, indices = self.clean_data(self.high_pressure)
            self.time = [t for ind, t in enumerate(
                self.time) if ind in indices]
        except:
            QMessageBox.question(
                self, 'Notice!', "Wrong data type. Please choose the data again.", QMessageBox.Ok)

        #lox_tank2 = []
        #prop_tank2 = []
        #lox_inj2 = []
        #prop_inj2 = []
        #high_tank2 = []
        # for i in self.lox_tank:
        #    lox_tank2.append(self.lowPressureConversion(float(i)))
        # for i in self.propane_tank:
        #    prop_tank2.append(self.lowPressureConversion(float(i)))
        # for i in self.lox_injector:
        #    lox_inj2.append(self.lowPressureConversion(float(i)))
        # for i in self.propane_injector:
        #    prop_inj2.append(self.lowPressureConversion(float(i)))
        # for i in self.high_pressure:
        #    high_tank2.append(float(self.highPressureConversionFunc(float(i))))
        #self.lox_tank = lox_tank2
        #self.propane_tank = prop_tank2
        #self.lox_injector = lox_inj2
        #self.propane_injector = prop_inj2
        #self.high_pressure = high_tank2

    def display_all_pressure(self, start_time=0, end_time=-1, show_high=False):
        plt.figure(figsize=(20, 10))
        indices = np.arange(len(self.time))
        start_index, _ = self.find_closest_element(self.time, start_time)
        if end_time != -1:
            end_index, _ = self.find_closest_element(self.time, end_time)
        else:
            end_index = -1
        print("start: {}, end: {}".format(start_index, end_index))
        plt.xlabel("time (s)")
        plt.ylabel("PSI")
        plt.plot(self.time[start_index:end_index],
                 self.lox_tank[start_index:end_index], label='LOX tank')
        plt.plot(self.time[start_index:end_index],
                 self.propane_tank[start_index:end_index], label='prop tank')
        plt.plot(self.time[start_index:end_index],
                 self.lox_injector[start_index:end_index], label='lox inj')
        plt.plot(self.time[start_index:end_index],
                 self.propane_injector[start_index:end_index], label='prop inj')
        if(show_high):
            plt.plot(self.time[start_index:end_index],
                     self.high_pressure[start_index:end_index], label='Pressurant Tank')
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
        filter_data2 = lfilter(b, a, pdata)
        dary = np.array([*map(float, pdata)])
        dary -= np.average(dary)
        step = np.hstack((np.ones(len(dary)), -1*np.ones(len(dary))))

        dary_step = np.convolve(dary, step, mode='valid')
        peaksall = []
        peaks = signal.find_peaks(dary_step, width=20)[0]
        #print("first round peaks:", peaks)
        if len(peaks) > 0:
            for p in peaks:

                peaksall.append(np.array([p]))
        # adding 0 to peaks in case empty
        elif len(peaks) == 0:
            peaks = [0]

        #print("Positive Peaks:", len(peaks))
        peaks2 = signal.find_peaks(-dary_step, width=20)[0]
        #print("Negative Peaks:", len(peaks2))
        if len(peaks2) > 0:
            for p in peaks2:

                peaksall.append(np.array([p]))
        #print("Total Peaks detected:", len(peaksall))
        peaksall.sort()
        # print(peaksall)
        plt.figure()

        plt.plot(dary)

        plt.plot(dary_step/10)

        for ii in range(len(peaks)):
            plt.plot((peaks[ii], peaks[ii]), (-1500, 1500), 'r')

        # plt.show()
        # start of second round
        # creating new data set with first and last peak as lower, upper bounds
        if len(peaksall) >= 2:
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

        dary2 -= np.average(dary2)
        step2 = np.hstack((np.ones(len(dary2)), -1*np.ones(len(dary2))))

        dary_step2 = np.convolve(dary2, step2, mode='valid')

        # Get the peaks of the convolution
        # negative peaks
        peaks3 = signal.find_peaks(-dary_step2, width=20)[0]
        # positive peaks
        peaks4 = signal.find_peaks(dary_step2, width=20)[0]
        # adjusting for frame shift
        if len(peaksall) >= 2:
            if len(peaks3) > 0:
                for p in range(len(peaks3)):
                    peaksall.append(np.array([peaks3[p]+peaks[0]+1]))
                # peaksall.append(peaks3+peaks+1)
            #print("Negative Peaks Detected:", len(peaks3), "at", peaks3)
            if len(peaks4) > 0:
                for p in range(len(peaks4)):
                    peaksall.append(np.array([peaks4[p]+peaks[0]+1]))
                # peaksall.append(peaks4+peaks+1)
            #print("Positive Peaks Detected:", len(peaks4), "at", peaks4)
            # print(peaksall)
        else:
            if len(peaks3) > 0:
                for p in range(len(peaks3)):
                    peaksall.append(np.array([peaks3[p]]))
            #print("Negative Peaks Detected:", len(peaks3),"at",peaks3)
            if len(peaks4) > 0:
                for p in peaks4:

                    peaksall.append(np.array([p]))
            #print("Positive Peaks Detected:", len(peaks4),"at", peaks4)
            # print(peaksall)
        # make this more robust
        #peaks2 = signal.find_peaks(-dary_step, width=20)[0]
        # print(peaks3)

        # plots
        plt.figure()

        plt.plot(dary2)
        # orange:
        plt.plot(dary_step2/10)
        # repeat process on dary data:
        n = 20  # the larger n is, the smoother curve will be
        b = [1.0 / n] * n
        a = 1
        filter_data3 = lfilter(b, a, dary_step2/10)
        peaks40 = signal.find_peaks(filter_data3, width=20)[0]
        peaks30 = signal.find_peaks(-1*filter_data3, width=20)[0]
        peaksall2 = []
        plt.plot(filter_data3)
        for ii in range(len(peaks40)):
            plt.plot((peaks40[ii], peaks40[ii]), (-150, 150), 'green')
        # adding to master graph
        if len(peaksall) >= 2:
            if len(peaks30) > 0:
                for p in range(len(peaks30)):
                    #print("testing peaks:",peaks)
                    #print("testing peaks30:", peaks30)
                    peaksall2.append(np.array([peaks30[p]+peaks[0]+1]))
        #           print("testing something:", np.array([peaks30[p]+peaks[p]+1]))
                # peaksall2.append(peaks30+peaks+1)
        #    print("Negative Peaks Detected:", len(peaks30), "at", peaks30)
            if len(peaks40) > 0:
                for p in range(len(peaks40)):
                    peaksall2.append(np.array([peaks40[p]+peaks[0]+1]))
                # peaksall2.append(peaks40+peaks+1)
        #         print("Positive Peaks Detected:", len(peaks40), "at", peaks40)
        #         print("This is peaksall2:",peaksall2)
        else:
            if len(peaks30) > 0:
                for p in peaks30:
                    peaksall2.append(np.array([p]))
                # peaksall2.append(peaks30)
            #print("Negative Peaks Detected:", len(peaks30),"at",peaks30)
            if len(peaks40) > 0:
                for p in peaks40:
                    peaksall.append(np.array([p]))
                # peaksall2.append(peaks40)
            #print("Positive Peaks Detected:", len(peaks40),"at", peaks40)
            # print(peaksall2)
        # appending 2nd round of lines to first

        peaksall = peaksall + peaksall2
        #print("This is peaksall:", peaksall)
        peaksall.sort()

        for ii in range(len(peaks3)):
            plt.plot((peaks3[ii], peaks3[ii]), (-150, 150), 'r')

        # plt.show()

        # end of second round
        #print("end of second round")

        # start of third round
        # creating new data set with first and last peak as lower, upper bounds
        if len(peaksall) >= 2:
            data2 = pdata[int(peaksall[0][0]):int(peaksall[2][-1])]
        else:
            data2 = pdata[0:int(peaksall[-1])]
        ##
        n = 5  # the larger n is, the smoother curve will be
        b = [1.0 / n] * n
        a = 1
        filter_data4 = lfilter(b, a, data2)
        ##
        dary2 = np.array([*map(float, filter_data4)])

        dary2 -= np.average(dary2)
        step2 = np.hstack((np.ones(len(dary2)), -1*np.ones(len(dary2))))

        dary_step2 = np.convolve(dary2, step2, mode='valid')

        # Get the peaks of the convolution
        # negative peaks
        peaks3 = signal.find_peaks(-dary_step2, width=20)[0]
        # positive peaks
        peaks4 = signal.find_peaks(dary_step2, width=20)[0]
        # adjusting for frame shift
        if len(peaksall) >= 2:
            if len(peaks3) > 0:
                for p in range(len(peaks3)):
                    peaksall.append(np.array([peaks3[p]+peaks[0]+1]))
                # peaksall.append(peaks3+peaks+1)
            #print("Negative Peaks Detected:", len(peaks3), "at", peaks3)
            if len(peaks4) > 0:
                for p in range(len(peaks4)):
                    peaksall.append(np.array([peaks4[p]+peaks[0]+1]))
                # peaksall.append(peaks4+peaks+1)
            #print("Positive Peaks Detected:", len(peaks4), "at", peaks4)
            # print(peaksall)
        else:
            if len(peaks3) > 0:
                for p in range(len(peaks3)):
                    peaksall.append(np.array([peaks3[p]]))
            print("Negative Peaks Detected:", len(peaks3), "at", peaks3)
            if len(peaks4) > 0:
                for p in peaks4:

                    peaksall.append(np.array([p]))
            #print("Positive Peaks Detected:", len(peaks4),"at", peaks4)
            # print(peaksall)
        # make this more robust
        #peaks2 = signal.find_peaks(-dary_step, width=20)[0]
        # print(peaks3)

        # plots
        plt.figure()

        plt.plot(dary2)
        # orange:
        plt.plot(dary_step2/10)

        peaksall.sort()

        for ii in range(len(peaks3)):
            plt.plot((peaks3[ii], peaks3[ii]), (-150, 150), 'r')

        # plt.show()

        # end of third round
        #print("end of third round")

        #peak_times = [time[peak[0]] for peak in peaksall]

        #display_pressure(time, pdata, peak_times)
        self.mplwid.canvas.axes.clear()
        self.mplwid.canvas.axes.plot(pdata)
        for i in peaksall:
            for t in i:
                self.mplwid.canvas.axes.axvline(t, c='k', lw='1')
        self.mplwid.canvas.draw()

        return [pdata, peaksall]

    def find_closest_element(self, collection, val):
        index = min(range(len(collection)),
                    key=lambda i: abs(collection[i]-val))
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
        newlist = [x for x in templist if str(x) != 'nan']
        indices = [ind for ind, x in enumerate(templist) if str(x) != 'nan']
        return np.array(newlist), np.array(indices)

    # raw is a value from 0 to 1024 (10bit ADC)
    def lowPressureConversion(self, raw):
        return 1.2258857538273733 * raw * (1024 / pow(2, 23)) - 123.89876445934394

    # raw is a value from 0 to 1024 (10bit ADC)
    def highPressureConversion(self, raw):
        return self.highPressureConversionFunc(raw)

    def initHighPressure(self):
        data = pd.read_csv(
            os.getcwd() + "/waterflow_test/high_pt_characterization_10_10")
        highPressureConversionFunc = interp1d(
            data['raw'], data['digital'], kind='quadratic')
        # print(type(highPressureConversionFunc))
        # print(highPressureConversionFunc(900))
        return highPressureConversionFunc

    def remove_lines(self):
        # plotting input data

        peaksall = self.new_data[1]  # actual times, not indices.

        data = self.new_data[0]
        # print(peaksall)
        # plt.plot(data)
        # for i in peaksall:
        #    for t in i:
        #        plt.axvline(t, c='k', lw='1')
        # plt.show()
        #display_pressure(time, data, peaksall)

        # taking user input and removing lines
        user_input, _ = QInputDialog.getText(
            self, 'Select Box', "Index of line to be removed (starts at 0 like most lists), separated by comma, e.g. 53, 32, 9: (will find the closest line and remove it. Invalid inputs will not be counted) ")
        if user_input:
            try:
                a_list = list(map(int, user_input.split(',')))
                a_list.reverse()
                # print(a_list)
                # print(peaksall)

                # removing lines at index indicated by user input
                for t in a_list:
                    del peaksall[t]

                self.mplwid.canvas.axes.clear()
                self.mplwid.canvas.axes.plot(data)
                for i in peaksall:
                    for t in i:
                        self.mplwid.canvas.axes.axvline(t, c='k', lw='1')
                self.mplwid.canvas.draw()
                self.new_data = [data, peaksall]
            except:
                QMessageBox.question(
                    self, 'Notice!', "Invalid Input.", QMessageBox.Ok)
                self.remove_lines()

    def add_lines(self):
        # plotting input data

        peaksall = self.new_data[1]
        data = self.new_data[0]

        # print(peaksall)
        # plt.figure(dpi=100)
        # plt.plot(data)
        # for i in peaksall:
        #    for t in i:
        #        plt.axvline(t, c='k', lw='1')
        # plt.show()

        # adding new lines with user input

        user_input3, _ = QInputDialog.getText(
            self, 'Select Box', "List of lines to add, by approximate X axis value (can edit later for precision):")

        if user_input3:
            new_lines = list(map(int, user_input3.split(',')))

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

        # shifting lines with user input
        # print(peaksall)
        user_input2, _ = QInputDialog.getText(
            self, 'Select Box', "Index of time to edit (starting at 0), separated by comma, e.g. 0, 2: ")

        if user_input2:
            time_list = list(map(int, user_input2.split(',')))
            #index_list = [find_closest_element(time, t)[0] for t in time_list]
            # print(index_list)

            for i in time_list:
                for j in range(11):
                    self.x_labels[j].setText(str(peaksall[i][0]+j-5))

                for j in range(11):
                    self.y_labels[j].setText(
                        str(round((data[peaksall[i][0]+j-5]), 6)))

                user_input3, _ = QInputDialog.getText(
                    self, 'Select Box', "Choose time for new line")
                self.reset()
                if user_input3:
                    #peak_i, _ = find_closest_element(peaksall, time[i])
                    peaksall.remove(peaksall[i][0])
                    peaksall.insert(
                        peaksall[i][0], np.array([float(user_input3)]))
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

    # function for returning values
    def values(self):
        # plotting input data
        # data[0] = pressure data
        # data[1] = array of detected peaks
        peaksall = self.new_data[1]
        data = self.new_data[0]
        if len(peaksall) >= 4:

            # taking input on data type and returning parameters according to data type
            # can probably be done with radios in gui
            self.static_label.setText("Static:")
            self.dyn_label.setText("Dynamic:")
            self.et_label.setText("Emptying Time:")
            self.droop_label.setText("Droop:")
            self.roi_label.setText("Rate of Increase:")

            if "tank" in self.type:
                static_start_index = int(peaksall[0][0])
                static_end_index = int(peaksall[1][0])
                dynamic_start_index = int(peaksall[2][0])
                dynamic_end_index = int(peaksall[3][0])

                #print(static_start_index, static_end_index)
                static_condition = data[static_start_index:static_end_index]
                static_pressure = mean(static_condition)
                self.static_change.setText(str(round(static_pressure, 3)))
                dynamic_condition = data[dynamic_start_index: dynamic_end_index]
                dynamic_pressure = mean(dynamic_condition)
                self.dyn_change.setText(str(round(dynamic_pressure, 3)))
                droop = static_pressure - dynamic_pressure
                self.dr_change.setText(str(round(droop, 3)))
                emptying_time = self.time[int(
                    peaksall[3][0])]-self.time[int(peaksall[2][0])]
                self.emp_change.setText(str(round(emptying_time, 3)))
                dynamic_rate_of_increase = (
                    data[dynamic_end_index]-data[dynamic_start_index])/emptying_time
                self.roi_change.setText(
                    str(round(dynamic_rate_of_increase, 3)))
                self.finaldata = [emptying_time, dynamic_rate_of_increase,
                                  dynamic_pressure, static_pressure, droop, "NaN", "NaN"]
            elif "injector" or "high" in self.type:
                dynamic_start_index = int(peaksall[0][0])
                dynamic_end_index = int(peaksall[1][0])

                dynamic_condition = data[dynamic_start_index: dynamic_end_index]
                #print("All Peaks:", peaksall)
                self.static_change.setText("NaN")
                dynamic_pressure = mean(dynamic_condition)
                self.dyn_change.setText(str(round(dynamic_pressure, 3)))
                emptying_time = self.time[int(
                    peaksall[1][0])]-self.time[int(peaksall[0][0])]
                self.emp_change.setText(str(round(emptying_time, 3)))
                dynamic_rate_of_increase = (
                    data[dynamic_end_index]-data[dynamic_start_index])/emptying_time
                self.roi_change.setText(
                    str(round(dynamic_rate_of_increase, 3)))
                self.dr_change.setText("NaN")
                if "high" in self.type:
                    pressure_drop = (
                        data[dynamic_start_index]-data[dynamic_end_index])
                    self.droop_label.setText("Pressure Drop:")
                    self.dr_change.setText(str(round(pressure_drop, 3)))
                    self.finaldata = [emptying_time, dynamic_rate_of_increase,
                                      dynamic_pressure, "NaN", "NaN", pressure_drop, "NaN"]
                else:
                    self.finaldata = [emptying_time, dynamic_rate_of_increase,
                                      dynamic_pressure, "NaN", "NaN", "NaN", "NaN"]

        else:
            QMessageBox.question(
                self, 'Notice!', "You need a minimum of 4 lines. Try again.", QMessageBox.Ok)
            self.process()

    def reset(self):
        for j in range(11):
            self.x_labels[j].setText('')
        for j in range(11):
            self.y_labels[j].setText('')

    def store(self):
        if self.type == 'tank' or self.type == 'injector':
            filename = 'data.csv'
        else:
            filename = 'highpressure.csv'
        self.finaldata.append(self.file+'.'+self.datatype+self.type)
        fields = ['emptying_time', 'dynamic_rate_of_increase', 'dynamic_pressure',
                  'static_pressure', 'droop', 'pressure_drop', '(I dunno what this column is for)']
        with open(filename, mode='a',  newline ='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(self.finaldata)

    def has_done_past(self):
        f = open('data.csv')
        data = pd.read_csv(f)
        for i in data['name'].to_numpy():
            if self.type in i and self.datatype in i and self.file in i:
                return True
        return False

    def load_old(self):
        f = open('data.csv')
        data = pd.read_csv(f)
        ind = 0
        names = data['name'].to_numpy()
        for i in range(0, len(names)):
            if self.type in names[i] and self.datatype in names[i] and self.file in names[i]:
                ind = i
        self.static_label.setText("Static:")
        self.dyn_label.setText("Dynamic:")
        self.et_label.setText("Emptying Time:")
        self.droop_label.setText("Droop:")
        self.roi_label.setText("Rate of Increase:")
        if 'tank' in self.type:
            self.static_change.setText(
                str(round(data['static_pressure'][i], 3)))
            self.dr_change.setText(str(round(data['droop'][i], 3)))
            self.emp_change.setText(str(round(data['emptying_time'][i], 3)))
            self.roi_change.setText(
                str(round(data['dynamic_rate_of_increase'][i], 3)))
        elif 'injector' or 'high' in self.type:
            self.static_change.setText("NaN")
            self.dyn_change.setText(str(round(data['dynamic_pressure'][i], 3)))
            self.emp_change.setText(str(round(data['emptying_time'][i], 3)))
            self.roi_change.setText(
                str(round(data['dynamic_rate_of_increase'][i], 3)))
            self.dr_change.setText("NaN")
            if 'high' in self.type:
                self.droop_label.setText("Pressure Drop:")
                self.dr_change.setText(str(round(data['pressure_drop'][i], 3)))

    def multiple_sel(self):
        f = open('data.csv')
        data = pd.read_csv(f)
        data=data.to_numpy()
        new = np.array([])
        text, ok = QInputDialog.getText(self, 'Select Box', 'Input the combination of data you would like to input. (Lox tank, lox injector, propane tank, propane injector)')
        if ok:
            if "lox" in text:
                self.type = "lox"
            else:
                self.type = "propane"
            if "tank" in text:
                self.datatype = "tank"
            else:
                self.datatype = "injector"
            for i in range(0, len(data)):
                if self.type in data[i][7] and self.datatype in data[i][7]:
                    new = np.append(new, [data[i]])
            new = np.reshape(new, (2,8))
            new = np.rot90(new, 3)
            self.emptytime = new[0]
            self.dynamicROI = new[1]
            self.staticpressure = new[3]
            self.droop = new[4]
            self.mul_data = new
            print(self.staticpressure)
            print(self.emptytime)
            self.multiple_plot()
            
    def multiple_plot(self):
        def sp_vs_et(empty, pressure):
            self.multi_graph.canvas.axes.clear()
            self.multi_graph.canvas.axes.plot(empty, pressure, "o")
            self.multi_graph.canvas.axes.set_xlabel("Pressure")
            self.multi_graph.canvas.axes.set_ylabel("Emptying time")
            self.multi_graph.canvas.draw()
        # High Pressure vs Empty

        def hp_vs_et(high, empty):
            self.multi_graph.canvas.axes.clear()
            self.multi_graph.canvas.plot(high, empty, 'o')
            self.multi_graph.canvas.axes.set_ylabel('Emptying Time (s)')
            self.multi_graph.canvas.axes.set_xlabel('Higher Pressure (psi)')
            self.multi_graph.canvas.draw()
        # Droop vs High Pressure

        def dr_vs_high(droop, high):
            self.multi_graph.canvas.axes.clear()
            self.multi_graph.canvas.axes.plot(droop, high, "o")
            self.multi_graph.canvas.axes.set_ylabel('Droop')
            self.multi_graph.canvas.axes.set_xlabel('High Pressure (psi)')
            self.multi_graph.canvas.draw()
        # DynamicROI vs High Pressure

        def dyn_vs_high(dyn, high):
            self.multi_graph.canvas.axes.clear()
            self.multi_graph.canvas.axes.plot(dyn, high, 'o')
            self.multi_graph.canvas.axes.set_ylabel('Dynamic Pressure')
            self.multi_graph.canvas.axes.set_xlabel('Dynamic ROI')
            self.multi_graph.canvas.draw()

        # Calls all the functions and graphs
        text, ok = QInputDialog.getText(self, 'Select Box', "Which graph do you want to see? S for Static Pressure and Emptying Time, H for High Pressure and Emptying Time, D for Droop and High Pressure, R for Dynamic ROI and High Pressure")
        if ok:
            if text.lower() == 's':
                try:
                    sp_vs_et(self.emptytime, self.staticpressure)
                except:
                    QMessageBox.question(self, 'Notice!', "You don't have the required data for your selection.", QMessageBox.Ok)

            elif text.lower() == 'h':
                try:
                    hp_vs_et(self.highpressure, self.emptytime)
                except:
                    QMessageBox.question(self, 'Notice!', "You don't have the required data for your selection.", QMessageBox.Ok)
            elif text.lower() == 'd':
                try:
                    dr_vs_high(self.droop, self.highpressure)
                except:
                    QMessageBox.question(self, 'Notice!', "You don't have the required data for your selection.", QMessageBox.Ok)
            elif text.lower() == 'r':
                try:
                    dyn_vs_high(self.dynamicROI, self.highpressure)
                except:
                    QMessageBox.question(self, 'Notice!', "You don't have the required data for your selection.", QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.setStyle('Fusion')
    sys.exit(app.exec_())
