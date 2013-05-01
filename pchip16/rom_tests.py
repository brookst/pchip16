"""
pchip16 rom test runner
"""
#pylint: disable=I0011, R0904

FILE_PATH = "data/Bounce.c16"

import unittest
from pchip16 import ROM

class TestInit(unittest.TestCase):
    def test_empty_init(self):
        rom = ROM()
    def test_file_init(self):
        with open(FILE_PATH, 'rb') as file_handle:
            rom = ROM(file_handle)

class TestROM(unittest.TestCase):
    """Test functions of ROM class"""
    def setUp(self):
        with open(FILE_PATH, 'rb') as file_handle:
            self.rom = ROM(file_handle)

class TestHeaders(TestROM):
    """Test header fields are read correctly"""
    def test_rom_version(self):
        self.assertEqual(self.rom.version, "1.1")
    def test_rom_size(self):
        self.assertEqual(self.rom.size, 0xe0)
    def test_rom_start_address(self):
        self.assertEqual(self.rom.start_address, 0x0)
    def test_rom_checksum(self):
        self.assertEqual(self.rom.checksum, 0xD7B62213)

class TestChecksum(TestROM):
    """Test checksum algorithm gives the same result"""
    def test_checksum(self):
        self.assertEqual(self.rom.calc_checksum(), 0xD7B62213)
