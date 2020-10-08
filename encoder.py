
class Encoder:
    def __init__(self, id, data):
        self.encoding = self.encode_data(id, data)

    def get_encoding(self):
        return self.encoding

    def encode_data(self, id, data):
        encoding = str(id)
        for i in data:
            encoding += "," + str(i)
        checksum = fletcher16(encoding)
        encoding = "{" + encoding + "|" + checksum + "}"
        return encoding

def fletcher16(message):
    sum1 = 0
    sum2 = 0
    # converts string into an array of bytes for easy math
    for byte in message.encode('ascii'):
        sum1 = (byte + sum1) % 255
        sum2 = (sum1 + sum2) % 255
    return "{:04X}".format(sum2 << 8 | sum1)