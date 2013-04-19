"""
pchip16 Memory classes
"""

from array import array

class Memory(object):
    """Memory with 16-bit reads and writes"""
    def __init__(self, size = 2**16):
        self.size = size
        self._mem = array('B', (0 for i in range(size) ) )
    def __getitem__(self, index):
        return (self._mem[index + 1] << 8) + self._mem[index]
    def __setitem__(self, index, value):
        self._mem[index] = value & 0xFF
        self._mem[index + 1] = value >> 8
    def __delitem__(self, index):
        self._mem[index] = 0
        self._mem[index + 1] = 0
    def __len__(self):
        return self.size

class Register(array):
    """16 x 16 bit registers"""
    def __new__(cls):
        return super(Register, cls).__new__(cls, 'H', (0 for i in range(16) ) )
