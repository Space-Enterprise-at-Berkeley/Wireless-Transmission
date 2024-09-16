import select
import random
import sys
import traceback
import time
import serial.tools.list_ports
import serial
import sensorParsing
import csv
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import matplotlib
matplotlib.use('Qt5Agg')

import time, traceback, sys, random, select
import numpy as np
import csv
import math
import random

import serial
import serial.tools.list_ports

# Custom modules
from Sensor_IDs import *
from packet import *
from sensorParsing import *

"""
GUI_threads.py
Select and monitor a serial input for incoming telemetry, extra data from packets, and update graphs accordingly


Classes:

    MplCanvas
    StatusGroup
    Status
    MainWindow
    Entry

Functions:

    full_file_name(base_name)

Misc variables:

    N/A
"""

highPressureConversionFunc = initHighPressure()

initHighPressure()


class SerialThread(QRunnable):
    '''
    Main Serial Thread

    Args:
    graphs - dict with canvas object for each graph in display, keyed by unique packet ID

    sensor_nums - a dictionary of the format
        sensor_type: # in use

    valve_signals -  is a dictionary that is kinda acting like a queue...
    should replace it with an actual queue. Right now it has all values set to 0, and thread will send the
    value as a message if it is non-zero

    filename - the name of the file to write the data to

    '''

    running = True

    def __init__(self, graphs, sensor_nums, valve_signals, filename):
        super(SerialThread, self).__init__()
        self.signals = SerialSignals()
        self.name = "Serial Thread"
        self.initializing = True

        # ---------- Serial Config ----------------------------------

        self.sensor_nums = sensor_nums
        self.graph_titles = {'low_pt':['Lox Tank', 'Propane Tank', 'Lox Injector', 'Propane Injector'],'high_pt':['Pressurant Tank']}
        self.sensor_types = ['low_pt','high_pt']#, 'temp']

        self.ser = None

        self.valve_signals = valve_signals

        # ---------- Recording Config ----------------------------------

        self.raw_filename = filename
        self.filename = None
        self.save_test = False
        self.headers = None

        # ---------- Display Config ---------------------------------

        # generate data to set base line on eacg graph
        n_data = 400
        xdata = list(range(n_data))
        ydata = [-1 for i in range(n_data)]#[random.randint(0, 10) for i in range(n_data)]

        self.graphs = graphs

        # Create canvases based on the number of sensors that are actually in use
        self.plot_ref_dict = {}  # [self._plot_ref]
        self.canvas_dict = {}

        self.plot_ref_list = []
        for i in range(len(self.graphs)):
            self.plot_ref_list.append([])
            for j in range(len(self.graphs[i])):
                canvas = self.graphs[i][j]
                # Get plot reference that can be used to update graph later
                plot_refs = canvas.axes.plot(xdata, ydata, 'b', label="No Data")
                self.plot_ref_list[i].append(plot_refs[0])
                print(i,j)
                canvas.axes.set_title(tab_graph_titles[i][j]) #TODO need to use "pretty" version of name as title
                canvas.axes.legend(loc='upper right')
        self.packet_ids = sensor_id_graph_mapping.keys()
        # ---------- Simulation Config ---------------------------------
        self.low_pt_ids = [1,2,3,4]
        self.high_pt_id = 5
        self.packet_gen = self.packet_generator()
        self.simulate = False
        self.interpolate = True
        self.debug = False

        # 207 for 12-bit on-board ADC
        self.high_threshold = 1702887

    @pyqtSlot()
    def run(self):
        '''
        Initialize the independent serial monitoring thread
        '''

        #TODO: Figure out why this is crashing on close
        def getLatestSerialInput():
            if not self.simulate:
                if ser:
                    line = ser.readline()
                    start = time.time()
                    while(ser.in_waiting > 0):
                        if ser:
                            line = ser.readline()
                            if time.time() - start > 1.5:
                                start = time.time()
                                print("looking for low pressure input")
                    # print(line)
                    # a = line.decode('utf-8').strip()
                    # return a
                    try:
                        a = line.decode('utf-8').strip()
                        return a
                    except:
                        print("Decoding Error: ",line)
                        return ''
            else:
                return next(self.packet_gen)

        last_first_value = 0
        last_values = [0] * 5

        start = time.time()
        print("starting loop")
        while SerialThread.running:

            # ----------- Initialization -------------

            if self.initializing:

                # Controls how many data points are being displayed on the graph
                NUMDATAPOINTS = 400
                fail_num = 15
                should_print = False
                display = True
                display_all = False
                repeat = 1

                pressure_timer = time.time()

                if not self.simulate:
                    print("Initializing")
                    chosenCom = ""
                    ports = list(serial.tools.list_ports.comports())
                    for p in ports:
                        print(p)
                        if "Arduino" in p.description or "ACM" in p.description or "cu.usbmodem" in p[0]:
                            chosenCom = p[0]
                            print("Chosen COM: {}".format(p))
                    if not chosenCom:
                        self.stop_thread("No Valid Com Found")
                        return
                    print("Chosen COM {}".format(chosenCom))
                    baudrate = 9600
                    print("Baud Rate {}".format(baudrate))
                    try:
                        ser = serial.Serial(chosenCom, baudrate,timeout=3)
                        self.ser = ser
                    except Exception as e:
                        self.stop_thread("Invalid Serial Connection")
                        return
                    ser.flushInput()

                    fails = 0
                    currLine = str(ser.readline())
                    start = time.time()
                    is_packet = False
                    pack = ''
                    while not is_packet and "low pressure sensors" not in currLine and "low pt" not in currLine:
                        currLine = str(ser.readline())
                        print("Received line: ",currLine)
                        # currLine = "b'{1,4297496.00,879057.00,6773916.00,6723986.00,4853986.00|a306}\r\r\n'"
                        pack = Packet(currLine)
                        # print(type(pack))
                        # print(pack.get_id())
                        # print(pack.is_valid)
                        is_packet = pack.is_valid
                        print(pack.is_valid)
                        if (currLine != "b''"):
                            print(currLine)
                            if time.time() - start > 1.5:
                                start = time.time()
                                print("looking for low pressure input")
                        else:
                            fails += 1
                        if (fails == fail_num):
                            self.stop_thread("Connection Lost")
                            return

                    # If data coming in is not a valid packet, need to continue with initialization
                    if not is_packet:
                        numLowSensors = self.sensor_nums['low_pt']
                        byteNum = (str(numLowSensors) + "\r\n").encode('utf-8')
                        print("write low sensor nums: {}".format(ser.write(byteNum)))

                        currLine = str(ser.readline())
                        start = time.time()
                        while ("high pressure sensors" not in currLine):
                            currLine = str(ser.readline())
                            if time.time() - start > 1.5:
                                start = time.time()
                                print("looking for high pressure input")
                        numHighSensors = self.sensor_nums['high_pt']
                        byteNum = (str(numHighSensors)+"\r\n").encode('utf-8')
                        print("write high sensor nums: {}".format(ser.write(byteNum)))

                        total_sensors = numLowSensors + numHighSensors #TODO: add in temp sensor
                        #sensors = int(input("How many sensors are connected?\n")) #set to how many sensors are connected
                        print(ser.readline().decode("utf-8")) # There are x low PTs and x high PTs.
                        self.headers = ser.read_until().decode("utf-8") # low1, low2, low3, high1.....
                        headerList = self.headers.split(",")
                        print(headerList)

                        print("num sensors: {}".format(total_sensors))

                data_dict = {}
                toDisplay_dict = {}
                for id in self.packet_ids:
                    data_dict[id] = []
                    toDisplay_dict[id] = []
                    for i in range(len(sensor_id_graph_mapping[id])):
                        data_dict[id].append([])
                        toDisplay_dict[id].append([])



                print("Writing raw data to: {}".format(self.raw_filename))
                with open(self.raw_filename,"a") as f:
                    self.headers = "time elapsed, loxTankPressure, propTankPressure, loxInjectorPressure, propInjectorPressure, highPressure, loxTreeTemp, loxHeater, boardVoltage, energyConsumed, loxTankTemp, chamberTemp1, chamberTemp2, chamberTemp3"
                    f.write(self.headers+"\n")

                # if not self.simulate:
                #     ser.write("0\r\n".encode('utf-8'))

                self.initializing = False

            # ----------- Main Loop ------------------

            # try:
            line = getLatestSerialInput()
            if self.debug:
                print(line)
            pack = Packet(line.strip())
            time_recevied = time.time()
            #Record exactly what was received, even if is invalid packet
            with open(self.raw_filename,"a") as fe:
                toWrite = str(time_recevied-start)+ "," + line + "\n"
                fe.write(toWrite)
                writer = csv.writer(fe,delimiter=",")

            if pack.encoded_message != None:


                # TODO - add logic to take other actions depending on packet ID (e.g. )
                # @Bridget - this is where something could be done like this:
                #     if pack.get_id() == 3:
                #           process_data(pack.get_data()[1], time_recevied)

                # if the value is -1, that means there is no data for that sensor
                # Retrieve and update the appropriate datalists and

                id = pack.get_id()

                if id in sensor_id_graph_mapping.keys():

                    # Saving data to files - how to write all at once for data cominng in a different speeds?
                    if self.save_test:
                        with open(self.filename,"a") as fe:
                            if id == 0:
                                print_str = "{},{},NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN".format(*(pack.get_data()))
                            elif id == 1:
                                print_str = "NaN,NaN,{},{},{},{},{},NaN,NaN,NaN,NaN,NaN,NaN,NaN".format(*(pack.get_data()))
                            elif id == 2:
                                print_str = "NaN,NaN,NaN,NaN,NaN,NaN,NaN,{},{},{},NaN,NaN,NaN,NaN".format(*(pack.get_data()))
                            elif id == 4:
                                print_str = "NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,{},{},{},{}".format(*(pack.get_data()))

                            toWrite = str(time_recevied-self.test_start)+ "," + print_str + "\n"
                            fe.write(toWrite)
                            writer = csv.writer(fe, delimiter=",")


                    arrangement_list = sensor_id_graph_mapping[id]
                    data_list = data_dict[id]
                    toDisplay_list = toDisplay_dict[id]
                    if len(arrangement_list) == len(pack.get_data()):
                        for i in range(len(arrangement_list)):
                            data = data_list[i]
                            toDisplay = toDisplay_list[i]
                            tab, graph, _ = arrangement_list[i]
                            # print("tab ", tab, "graph ",graph)
                            # print(len(plot_ref_list))
                            # print(len(plot_ref_list[0]))
                            plot = self.plot_ref_list[tab][graph]
                            val = float(pack.get_data()[i])
                            if id == 1:
                                if i == 4:
                                    print(val)
                                    if float(val) > self.high_threshold:
                                        if self.interpolate:
                                            val = highPressureConversionFunc(float(val))
                                    else:
                                        val = 0
                                else:
                                    val = lowPressureConversion(float(val))
                            # if val < 0:
                            #     if len(data) > 0:
                            #         val = data[-1]
                            #     else:
                            #         val = 0
                            data.append(val)
                            toDisplay_list[i] = data[-NUMDATAPOINTS:]
                            if should_print:
                                print("Val: {}".format(float(val)))
                                print(len(data), data)
                                print(len(toDisplay), toDisplay)
                                print("Id: {} Sensor: {}".format(id, sensor_id_to_name[id]))

                            if display_all:
                                # plot.set_ydata(data)
                                plot.set_xdata(range(len(data)))
                                print("Displaying all data")
                            else:
                                plot.set_ydata(toDisplay)
                                plot.set_xdata(range(len(toDisplay)))

                        if should_print:
                            should_print = True

                        # # update graph display & rescale based off data
                        # if display: #and repeat % 2 == 0:
                        id = pack.get_id()
                        arrangement_list = sensor_id_graph_mapping[id]
                        data_list = data_dict[id]
                        toDisplay_list = toDisplay_dict[id]
                        for i in range(len(arrangement_list)):
                            data = data_list[i]
                            toDisplay = toDisplay_list[i]
                            tab, graph, _ = arrangement_list[i]
                            plot = self.plot_ref_list[tab][graph]


                            # canvas = self.canvas_dict[pack.get_id()]
                            canvas = self.graphs[tab][graph]
                            canvas.axes.relim()
                            canvas.axes.autoscale_view()
                            canvas.draw()
                            leg = canvas.axes.legend(loc="upper right")
                            leg.get_texts()[0].set_text("{:.1f}".format(sum(toDisplay[-11:-1])/10))
                        # else:
                        #     repeat += 1
                    else:
                        print("Data indexing error: Data has {} values but expected {}".format(len(pack.get_data()),len(arrangement_list)))
                        print(pack.get_data())
                        print(line)
                else:
                    print("Id not in database")
                    print(line)

                # Sending Commands for valve opening
                for name in self.valve_signals.keys():
                    if (self.valve_signals[name] != 0):
                        print("Sending:",self.valve_signals[name])
                        byteNum = (str(self.valve_signals[name]) + "\r\n").encode('utf-8')
                        if not self.simulate:
                            ser.write(byteNum)
                        self.valve_signals[name] = 0

                # Sends out a small packet with interpolated tank vals for LCD
                # if time.time() - pressure_timer > 3:
                #     pressure_timer = time.time()
                #     data = [data_dict[1][0][-1],data_dict[1][1][-1]]
                #     data = list(map(lambda x: round(x,1),data))
                #     p = Packet(data,id=30)
                #     # print(p.encode_data());
                #     byteNum = (p.encode_data() + "\r\n").encode('utf-8')
                #     if not self.simulate:
                #         ser.write(byteNum)




            else:
                print("SerialThread Error: Invalid Telemetry Packet")
                print("Error: ",line)

            # except Exception as e:
            #     # self.stop_thread("Error in reading loop\nCrash: {}".format(e))
            #     print("Error in reading loop\nCrash: {}")#.format(e))
            #
            #     exception_type, exception_object, exception_traceback = sys.exc_info()
            #     filename = exception_traceback.tb_frame.f_code.co_filename
            #     line_number = exception_traceback.tb_lineno
            #
            #     print("Exception type: ", exception_type)
            #     print("File name: ", filename)
            #     print("Line number: ", line_number)
            #
            #     ser.close()
            #     break

        self.stop_thread("Thread Stopped")

    def stop_thread(self, msg=''):
        SerialThread.running = False
        if self.ser:
            self.ser.close()
        if msg:
            print("{}: ".format(self.name), msg)
        self.signals.finished.emit()

    def update_plot(self):

        self._plot_ref.set_ydata(self.ydata)
        self._plot_ref.set_xdata(self.xdata)

        self.canvas.draw()

    def start_saving_test(self, filename, metadata):
        if self.headers:
            self.filename = "data/" + filename
            self.test_start = time.time()
            print("Writing data to: {}".format(filename))
            with open(self.filename,"a") as f:
                    f.write(metadata+"\n")
                    f.write(self.headers+"\n")
            self.save_test = True
        else:
            print("Error: data collection has not started")

    def stop_saving_test(self):
        self.save_test = False

    def packet_generator(self):
        funcs = [lambda x: 100*math.cos(x/20), lambda x: 40*math.cos(x/25),
                 lambda x: 70*math.cos(x/10), lambda x: 65*math.cos(x/15)]


        def pt_line(num):
            if x % 3 == 0:
                return num + random.uniform(-5,5)
            else:
                return num

        funcs[0] = lambda x: 8 + random.uniform(-1,1)
        funcs[1] = lambda x: pt_line(12)


        x = 0
        while True:

            data = []
            for j in range(4):
                data.append(funcs[j](x))
            data.append(1200)
            pack = Packet(data,id=1)

            yield pack.encode_data() #"{1,4297496.00,879057.00,6773916.00,6723986.00,4853986.00|a306}" #pack.encode_data()
            x += 1
            data = [0,0,0,0]
            data = list(map(funcs[0],data))
            pack = Packet(data,id=4)
            yield pack.encode_data()




class SerialSignals(QObject):
    '''
    Defines the signals available from a running worker thread

    Suported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    data = pyqtSignal(object)



# TODO: Create a separate Data Processing thread. Maybe add timestamps when data comes in?, and use that
# when graphing, so that it's not based on the time it actually gets out of the queue?
