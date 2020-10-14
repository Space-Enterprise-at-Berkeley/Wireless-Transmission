import serial
import csv


RFser = serial.Serial('COM3', 9600)
ser.flushInput()

while True:
    try:
        line = RFser.readline().strip()
        data = line.split(',')
        if(data[0] == "GPRMC"):
            lat = data[3]
            lat_dir = data[4]
            
            lon = data[5]
            lon_dir = data[6]

            latitude = convert_to_decimal_degrees(int(lat[:2]), int(lat[2:]), 0)

            longitude = convert_to_decimal_degrees(int(lon[:3]), int(lon[3:]), 0)

            latitude *= -1 if lat_dir == 'S'
            longitude *= -1 if lon_dir == 'W'
            print("{},{}".format(latitude, longitude))



def convert_to_decimal_degrees(degrees, minutes, seconds):
    return degrees + (minutes/60) + (seconds/3600)
