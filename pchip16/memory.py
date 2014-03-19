"""
pchip16 Memory classes
"""

from array import array

class Memory(object):
    """Memory with 16-bit reads and writes"""
    def __init__(self, data=None, size=2**16):
        self.size = size
        if data is None:
            self._mem = array('B', (0 for i in range(size)))
        else:
            self.fromstring(data)
    def __getitem__(self, index):
        return (self._mem[index + 1] << 8) + self._mem[index]
    def __setitem__(self, index, value):
        self._mem[index] = value & 0xFF
        self._mem[index + 1] = value >> 8
    def __delitem__(self, index):
        self._mem[index] = 0
        self._mem[index + 1] = 0
    def __len__(self):
        """Return the highest non-zero address in normal memory"""
        end = min(0xFDF0, self.size)
        while not self[end - 2]:
            end -= 2
        return end

    def tostring(self):
        """Return string representation of memory contents"""
        return self._mem[0:len(self)].tostring()

    def fromstring(self, data):
        """Return string representation of memory contents"""
        self._mem = array('B')
        self._mem.fromstring(data)
        self._mem.extend((0 for i in range(self.size - len(data))))


class Register(array):
    """16 x 16 bit registers"""
    def __new__(cls):
        return super(Register, cls).__new__(cls, 'H', (0 for i in range(16)))
