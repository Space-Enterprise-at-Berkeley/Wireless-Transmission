from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import time, traceback, sys, random, select
import numpy as np
import csv

import serial
import serial.tools.list_ports

'''this is NOT finalized - just a placehold for actual values'''
id_to_sensor = {
    1 : "Propane Tank",
    1 : "LOX Tank",
    3 : "Injector"
}

class SerialThread(QRunnable):
    '''
    Main Serial Thread

    Args:
    graphs -

    sensor_nums - a dictionary of the format
        sensor_type:# in use

    valve_signals -  is a dictionary that is kinda acting like a queue...
    should replace it with an actual queue. Right now it has all values set to 0, and will send the
    value as a message if it is non-zero

    filename - the name of the file to write the data to

    '''

    running = True

    def __init__(self, graphs, sensor_nums, valve_signals, filename):
        super(SerialThread, self).__init__()
        self.signals = SerialSignals()
        self.name = "Serial Thread"

        # ---------- Serial Config ----------------------------------

        self.graph_titles = {'low_pt':['Lox Tank', 'Propane Tank', 'Lox Injector', 'Propane Injector'],'high_pt':['Pressurant Tank']}
        self.sensor_types = ['low_pt']# 'high_pt', 'temp']

        self.numLowPressure = 3
        self.numHighPressure = 1
        self.ser = None

        self.valve_signals = valve_signals
        self.filename = filename


        # ---------- Display Config ---------------------------------

        self.graphs = graphs
        self.canvas = graphs["low_pt"][0]

        # I think this is irrelevant now?
        n_data = 400
        self.xdata = list(range(n_data))
        self.ydata = [0 for i in range(n_data)]#[random.randint(0, 10) for i in range(n_data)]

        #Initialize Plot
        # plot_refs = self.canvas.axes.plot(self.xdata, self.ydata, 'b')
        # self._plot_ref = plot_refs[0]

        # Create canvases based on the number of sensors that are actually in use
        self.low_plot_ref_list = []#[self._plot_ref]
        self.canvas_dict = {}

        for sensor in self.sensor_types:
            self.canvas_dict[sensor] = []
            for i in range(len(graphs[sensor])):
                canvas = graphs[sensor][i]
                self.canvas_dict[sensor].append(canvas)
                # Get plot reference that can be used to update graph later
                plot_refs = canvas.axes.plot(self.xdata, self.ydata, 'b')
                self.low_plot_ref_list.append(plot_refs[0])
                canvas.axes.set_title(self.graph_titles[sensor][i])


    @pyqtSlot()
    def run(self):
        '''
        Initialize the independent thread
        '''

        # while SerialThread.running:
        #     result = random.randint(0, 10)
        #     self.update_plot(result)
        #     time.sleep(0.01)


        NUMDATAPOINTS = 400
        fail_num = 15
        should_print = False

        print("Starting")

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

        display = True
        display_all = False
        repeat = 1

        # filename = input("Which file should the data be written to?\n")
        print("Writing data to: {}".format(self.filename))


        fails = 0
        currLine = str(ser.readline())
        start = time.time()
        while ("low pressure sensors" not in currLine and "low pt" not in currLine):
            currLine = str(ser.readline())
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
        numLowSensors = self.numLowPressure
        byteNum = (str(numLowSensors) + "\r\n").encode('utf-8')
        print("write low sensor nums: {}".format(ser.write(byteNum)))

        currLine = str(ser.readline())
        start = time.time()
        while ("high pressure sensors" not in currLine):
            currLine = str(ser.readline())
            if time.time() - start > 1.5:
                start = time.time()
                print("looking for high pressure input")
        numHighSensors = self.numHighPressure
        byteNum = (str(numHighSensors)+"\r\n").encode('utf-8')
        print("write high sensor nums: {}".format(ser.write(byteNum)))

        sensors = numLowSensors + numHighSensors
        #sensors = int(input("How many sensors are connected?\n")) #set to how many sensors are connected
        print(ser.readline().decode("utf-8")) # There are x low PTs and x high PTs.
        headers = ser.read_until().decode("utf-8") # low1, low2, low3, high1.....
        headerList = headers.split(",")
        print(headerList)

        print("num sensors: {}".format(sensors))
        data = [[] for i in range(sensors)]
        toDisplay = [[] for i in range(sensors)]
        #
        # plt.ion()
        # fig, ax = plt.subplots(2, max(numLowSensors, numHighSensors))
        # if max(numLowSensors, numHighSensors) == 1:
        #     ax = np.reshape(ax, (-1, 1))
        # plt.show()
        # print(np.shape(ax))
        # plots = []
        #
        # for num in range(numLowSensors):
        #     ax[0,num].set_title(headerList[num])
        #     plot, = ax[0,num].plot(data[num])
        #     plots.append(plot)
        #
        # for num in range(numHighSensors):
        #     ax[1,num].set_title(headerList[num+numLowSensors])
        #     plot, = ax[1,num].plot(data[num+numLowSensors])
        #     plots.append(plot)
        #
        with open(self.filename,"a") as f:
            headers = "time," + headers
            f.write(headers+"\n")

        plots = self.low_plot_ref_list #[self._plot_ref]

        ser.write("0\r\n".encode('utf-8'))


        #TODO: Figure out why this is crashing on close
        def getLatestSerialInput():
            if ser:
                line = ser.readline()
                start = time.time()
                while(ser.in_waiting > 0):
                    if ser:
                        line = ser.readline()
                        if time.time() - start > 1.5:
                            start = time.time()
                            print("looking for low pressure input")
                return line.decode('utf-8').strip()


        last_first_value = 0
        last_values = [0] * 5

        print("starting loop")
        while SerialThread.running:
            # try:
            line = getLatestSerialInput()
            if ',' in line:
                values = line.strip().split(',')

                if values[0] == '':
                    values[0] = str(last_first_value);
                if len(values) < sensors:
                    print("not enough data, continuing")
                    continue
                last_values = values
                values = [val.strip() for val in values]
                last_first_value = values[0]

                if should_print:
                    print("values: {}".format(values))


                with open(self.filename,"a") as fe:
                    toWrite = str(time.time())+"," + ",".join(values)+"\n"
                    fe.write(toWrite)
                    writer = csv.writer(fe,delimiter=",")
                    # writer.writerow(np.array([time.time(),values]).flatten())
                # print("Repeat: {}".format(repeat))

                for i in range(len(plots)):  #TODO: CHANGE BACK range(sensors):
                    data[i].append(float(values[i]))
                    toDisplay[i] = data[i][-NUMDATAPOINTS:]
                    if should_print:
                        print(len(data[i]))
                        print(len(toDisplay[i]))

                    if display_all:
                        plots[i].set_ydata(data[i])
                        plots[i].set_xdata(range(len(data[i])))
                    else:
                        plots[i].set_ydata(toDisplay[i])
                        plots[i].set_xdata(range(len(toDisplay[i])))
                    # else:
                    #     self.ydata = [0 for i in range(400-len(toDisplay[i]))].extend[toDisplay[i]]
                    #     plots[i].set_ydata(self.ydata)

                # original for 1
                if display and repeat % 2 == 0:
                    for sensor in self.sensor_types:
                        canvas_list = self.canvas_dict[sensor]
                        for j in range(len(plots)):

                            canvas_list[j].axes.relim()
                            canvas_list[j].axes.autoscale_view()

                        # for num in range(numHighSensors):
                        #     ax[1,num].relim()
                        #     ax[1,num].autoscale_view()

                            canvas_list[j].draw()
                        # self.canvas.flush_events()
                    repeat = 1
                else:
                    repeat += 1

                # valve stuff
                for name in self.valve_signals.keys():
                    if (self.valve_signals[name] != 0):
                        print(self.valve_signals[name])
                        byteNum = (str(self.valve_signals[name]) + "\r\n").encode('utf-8')
                        ser.write(byteNum)
                        self.valve_signals[name] = 0

                # data_in = select.select([sys.stdin], [], [], 0.1)[0]
                # if data_in:
                #     c = sys.stdin.readline().rstrip()
                #     if (c == "q"):
                #         print("Exiting")
                #         sys.exit(0)
                #     elif c == '0':
                #         display = not display
                #         print("toggling display")
                #     elif c == 't':
                #         display = True
                #     elif c == 'f':
                #         display = False
                #     elif c == 'd':
                #         display_all = not display_all
                #         print("toggle display all data")
                #     elif c == "c":
                #         data = [[] for i in range(sensors)]
                #         toDisplay = [[] for i in range(sensors)]
                #     else:
                #         print("You entered: %s" % c)
            else:
                print(line)

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


    def stop_thread(self,msg=''):
        SerialThread.running = False
        if self.ser:
            self.ser.close()
        if msg:
            print("{}: ".format(self.name),msg)
        self.signals.finished.emit()


    def update_plot(self):

            self._plot_ref.set_ydata(self.ydata)
            self._plot_ref.set_xdata(self.xdata)

            self.canvas.draw()

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
