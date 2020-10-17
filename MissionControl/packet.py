"""
Input format: {1,2,3,4|sum} where 1 is the sensor ID, 2, 3, 4 is the data,
and sum is the result returned from checksum.
Packet object format: integer id, integer list data, and string checksum.
"""


class Packet:
    def __init__(self, data, id = None):
        # If no ID is passed in, `data` will be a raw data packet to be decoded
        if not id:
            self.sensor_id, self.data, self.checksum = self.decode_message(data)
            if not self.sensor_id and not self.data and not self.checksum:
                self.encoded_message = data
            else:
                self.encoded_message = None
        # If an ID is passed in, `data` will be information to be encoded with ID into a packet
        else:
            self.sensor_id = id
            self.data = data
            self.encoded_message = self.encode_data()

    def get_id(self):
        return self.sensor_id

    def get_data(self):
        return self.data

    def get_sum(self):
        return self.checksum

    def encode_data(self):
        encoding = str(self.sensor_id)
        for i in self.data:
            encoding += "," + str(i)
        checksum = fletcher16(encoding)
        self.checksum = checksum
        encoding = "{" + encoding + "|" + self.checksum + "}"
        return encoding

    def decode_message(self, data):
        tracker = len(data) - 1
        if '|' not in data:
            print("Invalied packet: No Data Termination Character ('|') found")
            return None, None, None
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
        if old_sum != new_sum:
            print("Calculated checksum does not match the transmitted checksum")
            return None, None, None

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
