"""
pchip16 rom test runner
"""
#pylint: disable=I0011, R0904

import unittest
from pchip16.rom_tests import TestROM
from pchip16.memory import Memory
from pchip16.rom import ROM

class TestROMLoading(TestROM):
    """Test loading ROM into memory"""
    def setUp(self):
        super(TestROMLoading, self).setUp()
        self.mem = Memory(self.rom.data, len(self.rom.data))
    def test_len(self):
        self.assertEqual(len(self.mem), len(self.rom.data) )
    def test_rom_load(self):
        self.assertEqual(self.mem.tostring(), self.rom.data.tostring() )

class TestChecksum(TestROMLoading):
    """Test checksum algorithm gives the same result"""
    def test_checksum(self):
        rom = ROM()
        rom.data.fromstring(self.mem.tostring())
        self.assertEqual(rom.calc_checksum(), 0xD7B62213)
