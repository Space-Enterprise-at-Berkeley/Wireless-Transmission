import serial
import serial.tools.list_ports
import sys

rfSerial = serial.Serial('COM3', 57600)
rfSerial.flushInput()

f = open('rf_write_to_file_test.txt', "a")
while True:
    if(not f):
        f=open('rf_write_to_file_test.txt', 'a')
    if(not rfSerial):
        rfSerial = serial.Serial('COM3', 57600)
    try:
        if(rfSerial.available()):
            print("serial line has messages")
            data = rfSerial.readline()
            f.write(data + "\n")
            print(data+"\n")
    except:
        print("Getting errors")
        rfSerial.close()
        f.close()

rfSerial.close()
f.close()
