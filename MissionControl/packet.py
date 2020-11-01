"""
Input format: {1,2,3,4|sum} where 1 is the sensor ID, 2, 3, 4 is the data,
and sum is the result returned from checksum.
Packet object format: integer id, integer list data, and string checksum.
"""


class Packet:
    def __init__(self, data, id = None):
        self.debug = False
        self.is_valid = False
        # If no ID is passed in, `data` will be a raw data packet to be decoded
        if not id:
            self.sensor_id, self.data, self.checksum = self.decode_message(data)
            if self.sensor_id and self.data and self.checksum:
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

    def is_valid(self):
        return True

    def encode_data(self):
        encoding = str(self.sensor_id)
        for i in self.data:
            encoding += "," + str(i)
        checksum = fletcher16(encoding)
        self.checksum = checksum
        encoding = "{" + encoding + "|" + self.checksum + "}"
        return encoding

    def decode_message(self, data):
        if "{" in data and "|" in data and "}" in data:
            start = data.index("{")
            pipe = data.index("|")
            end = data.index("}")
            data = data[start:end+1] # remove leading "b'" from binary message
            # print("Fixed data:",data)
            tracker = len(data) - 1
            if '|' not in data:
                self.is_valid = False
                if self.debug:
                    print("Invalied packet: No Data Termination Character ('|') found")
                return None, None, None
            while data[tracker] != "|":
                tracker -= 1
            old_sum = data[tracker + 1:len(data) - 1]

            # Get sensor id.
            i = 0
            while data[i] != ",":
                i += 1
            if self.debug:
                print("Beginning: ",data[0])
                print("Id num:", data[1:i])
            sensor_id = int(data[1:i])

            # Calculate new checksum and compare.
            checksum_data = data[1:tracker]
            new_sum = fletcher16(checksum_data)
            new_sum = new_sum.lower()
            print("Old_sum: ", old_sum, "New_sum", new_sum)
            if old_sum != new_sum:
                self.is_valid = False
                if self.debug:
                    print("Calculated checksum does not match the transmitted checksum")
                return None, None, None

            # Get sensor data.
            data = checksum_data.split(",")
            data = [float(data[i]) for i in range(len(data))]
            self.is_valid = True
            if self.debug:
                print("Is Valid: ", self.is_valid)

            return sensor_id, data, new_sum
        else:
            if self.debug:
                print("Malformed packet")
            return None, None, None

def fletcher16(message):
    sum1 = 0
    sum2 = 0
    # converts string into an array of bytes for easy math
    for byte in message.encode('ascii'):
        sum1 = (byte + sum1) % 255
        sum2 = (sum1 + sum2) % 255
    return "{:04X}".format(sum2 << 8 | sum1)
