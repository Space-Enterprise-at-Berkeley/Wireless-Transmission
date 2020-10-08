"""
Input format: {1,2,3,4|sum} where 1 is the sensor ID, 2, 3, 4 is the data,
and sum is the result returned from checksum.
Packet object format: integer id, integer list data, and string checksum.
"""


class Packet:
    def __init__(self, data):
        self.sensor_id, self.data, self.checksum = self.decode_message(data)

    def get_id(self):
        return self.sensor_id

    def get_data(self):
        return self.data

    def get_sum(self):
        return self.checksum

    def decode_message(self, data):
        tracker = len(data) - 1
        while data[tracker] != "|":
            tracker -= 1
        old_sum = data[tracker + 1:len(data) - 1]

        # Get sensor id.
        i = 0
        while data[i] != ",":
            i += 1
        sensor_id = int(data[1:i])

        # Calculate new checksum and compare.
        checksum_data = data[1:tracker]
        new_sum = fletcher16(checksum_data)
        if old_sum == new_sum:
            print("Check sum succeeded")
        else:
            print("New sum does not match the old sum")

        # Get sensor data.
        data = checksum_data.split(",")
        data = [float(data[i]) for i in range(len(data))]
        return sensor_id, data, new_sum

def fletcher16(message):
    sum1 = 0
    sum2 = 0
    # converts string into an array of bytes for easy math
    for byte in message.encode('ascii'):
        sum1 = (byte + sum1) % 255
        sum2 = (sum1 + sum2) % 255
    return "{:04X}".format(sum2 << 8 | sum1)
