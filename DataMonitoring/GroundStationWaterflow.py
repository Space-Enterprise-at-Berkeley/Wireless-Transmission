from datetime import datetime
import os
import argparse
import select
import sys
import numpy as np
import matplotlib.pyplot as plt
import serial
import serial.tools.list_ports
import time
import csv
import matplotlib
matplotlib.use("tkAgg")
# import pandas as pd


def main(args):

    NUMDATAPOINTS = 400

    print("Starting")

    chosenCom = ""
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        # print(p)
        # print(p.description)
        # print(p[0])
        # print(p.name)
        if "Arduino" in p.description or "ACM" in p.description or "ACM" in p.name or "cu.usbmodem" in p[0]:
            chosenCom = p[0]
            # print("Chosen COM: {}".format(p))
    print("Chosen COM {}".format(chosenCom))
    # ser = serial.Serial('/dev/tty/COM3')
    ser = serial.Serial(chosenCom, 9600)
    ser.flushInput()

    plot_window = 1000
    display = True
    display_all = False

    if args.file:
        filename = next_file_name(args.file)
    else:
        filename = next_file_name("waterflow")
    # filename = input("Which file should the data be written to?\n")
    print("Writing data to: {}".format(filename))


''' Joey's startup code
currLine = str(ser.readline())
while("Waiting for Initiation" not in currLine):
    time.sleep(5)
    currLine = str(ser.readline())
    print("Waiting for Initiation")
if("Waiting for Initiation" in currLine):
        print("Detected")
        ser.write("0\r\n".encode('utf-8'))
        print("wrote 0")

currLine = str(ser.readline())
while ("low pressure sensors" not in currLine):
    time.sleep(500)
    currLine = str(ser.readline())
    print("looking for low pressure input")
numLowSensors = int(input(currLine + "\n"))
byteNum = (str(numLowSensors) + "\r\n").encode('utf-8')
print("write low sensor nums: {}".format(ser.write(byteNum)))

currLine = str(ser.readline())
while ("high pressure sensors" not in currLine):
    # time.sleep(500)
    currLine = str(ser.readline())
    print("looking for high pressure input")
numHighSensors = int(input(currLine + "\n"))
byteNum = (str(numHighSensors) + "\r\n").encode('utf-8')
print("write high sensor nums: {}".format(ser.write(byteNum)))

sensors = numLowSensors + numHighSensors
'''
 currLine = str(ser.readline())
  start = time.time()
   while ("low pressure sensors" not in currLine and "low pt" not in currLine):
        currLine = str(ser.readline())
        print(currLine)
        if time.time() - start > 1.5:
            start = time.time()
            print("looking for low pressure input")
    numLowSensors = int(input(currLine + "\n"))
    byteNum = (str(numLowSensors) + "\r\n").encode('utf-8')
    print("write low sensor nums: {}".format(ser.write(byteNum)))

    currLine = str(ser.readline())
    while ("high pressure sensors" not in currLine):
        # time.sleep(500)
        currLine = str(ser.readline())
        print("looking for high pressure input")
    numHighSensors = int(input(currLine + "\n"))
    byteNum = (str(numHighSensors) + "\r\n").encode('utf-8')
    print("write high sensor nums: {}".format(ser.write(byteNum)))

    sensors = numLowSensors + numHighSensors
    # sensors = int(input("How many sensors are connected?\n")) #set to how many sensors are connected
    # There are x low PTs and x high PTs.
    print(ser.readline().decode("utf-8"))
    headers = ser.read_until().decode("utf-8")  # low1, low2, low3, high1.....
    headerList = headers.split(",")
    print(headerList)

    print("num sensors: {}".format(sensors))
    data = [[] for i in range(sensors)]
    toDisplay = [[] for i in range(sensors)]

    plt.ion()
    fig, ax = plt.subplots(2, max(numLowSensors, numHighSensors))
    if max(numLowSensors, numHighSensors) == 1:
        ax = np.reshape(ax, (-1, 1))
    plt.show()
    print(np.shape(ax))
    plots = []

    for num in range(numLowSensors):
        ax[0, num].set_title(headerList[num])
        plot, = ax[0, num].plot(data[num])
        plots.append(plot)

    for num in range(numHighSensors):
        ax[1, num].set_title(headerList[num + numLowSensors])
        plot, = ax[1, num].plot(data[num + numLowSensors])
        plots.append(plot)

    with open(filename, "a") as f:
        headers = "time," + headers
        f.write(headers + "\n")

    ser.write("0\r\n".encode('utf-8'))

    def getLatestSerialInput():
        line = ser.readline()
        while(ser.in_waiting > 0):
            line = ser.readline()
        return line.decode('utf-8').strip()

    last_first_value = 0
    last_values = [0] * 5

    print("starting loop")
    while True:
        try:
            line = getLatestSerialInput()
            values = line.strip().split(',')

            if values[0] == '':
                values[0] = str(last_first_value)
            if len(values) < sensors:
                print("not enough data, continuing")
                continue
            last_values = values
            values = [val.strip() for val in values]
            last_first_value = values[0]

            print("values: {}".format(values))

            with open(filename, "a") as f:
                toWrite = str(time.time()) + "," + ",".join(values) + "\n"
                f.write(toWrite)
                writer = csv.writer(f, delimiter=",")
                writer.writerow(np.array([time.time(), values]).flatten())

            for i in range(sensors):
                data[i].append(float(values[i]))
                print(len(data[i]))
                toDisplay[i] = data[i][-NUMDATAPOINTS:]
                print(len(toDisplay[i]))

                if display_all:
                    plots[i].set_ydata(data[i])
                    plots[i].set_xdata(range(len(data[i])))
                else:
                    plots[i].set_ydata(toDisplay[i])
                    plots[i].set_xdata(range(len(toDisplay[i])))

            if display:
                for num in range(numLowSensors):
                    ax[0, num].relim()
                    ax[0, num].autoscale_view()

                for num in range(numHighSensors):
                    ax[1, num].relim()
                    ax[1, num].autoscale_view()

                fig.canvas.draw()
                fig.canvas.flush_events()

            data_in = select.select([sys.stdin], [], [], 0.1)[0]
            if data_in:
                c = sys.stdin.readline().rstrip()
                if (c == "q"):
                    print("Exiting")
                    sys.exit(0)
                elif c == '0':
                    display = not display
                    print("toggling display")
                elif c == 't':
                    display = True
                elif c == 'f':
                    display = False
                elif c == 'd':
                    display_all = not display_all
                    print("toggle display all data")
                elif c == "c":
                    data = [[] for i in range(sensors)]
                    toDisplay = [[] for i in range(sensors)]
                else:
                    print("You entered: %s" % c)
            else:
                continue

        except Exception as e:
            print("Crash: {}".format(e))
            ser.close()
            break

    ser.close()

'''Given a base file name BASE, will return the correct full name "BASE_MM-DD-YY_#{i}", based off the
files that already exist in the directory STORED.'''


def next_file_name(base, stored='data'):
    if '#' in base:
        raise Exception("Incorrectly Formatted Filename: cannot contain '#'")
    files = os.listdir(stored)
    largest = 0
    suffix_num = 0
    for f in files:
        if base in f:
            suffix_num = int((f.split('#')[-1]).split('.')[0])
            if suffix_num > largest:
                largest = suffix_num
    return base + "_{}_#{}.txt".format(datetime.today().strftime('%m-%d-%y'), suffix_num + 1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Tool to interact with ground station hardware to retrieve and display waterflow data")

    parser.add_argument(
        '-f',
        '--file',
        help="Base filename for data to be recorded into"
    )

    args = parser.parse_args()
    main(args)
