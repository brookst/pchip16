"""
pchip16 ROM module - for loading programs into memory from file
"""

from .utils import to_word
from crcmod import mkCrcFun
from array import array

CRC32_FUNC = mkCrcFun(0x104C11DB7, initCrc=0, xorOut=0xFFFFFFFF)

class ROM(object):
    """Memory contents and state representation"""
    data = array('B')
    version = "1.0"
    size = 0
    start_address = 0
    checksum = 0
    def __init__(self, file_handle=None):
        """Initialise rom with contents of file_handle"""    

        if file_handle:
            self.load_file(file_handle)

    def load_file(self, file_handle):
        """Load contents of file_handle into memory"""
        self.size = file_handle.tell()
        header = file_handle.read(16)
        if header[0:4] == b"CH16":
            ## Do this conversion in a 2/3 safe method
            header = [ord(header[c:c+1]) for c in range(len(header))]
            version = header[5]
            self.version = "%d.%d" % (version >> 4, version & 0xF)
            size = header[6:0xA]
            self.size = (size[3] << 24) | (size[2] << 16) | (size[1] << 8) \
                | size[0]
            self.size = to_word(header[6:0xA])
            self.start_address = (header[0xB] << 8) + header[0xA] 
            self.checksum = to_word(header[0xC:0x10])
        data = file_handle.read()
        self.data = array('B')
        self.data.fromstring(data)

    def calc_checksum(self):
        """Compute the checksum of current ROM data"""
        return CRC32_FUNC(self.data.tostring() )
