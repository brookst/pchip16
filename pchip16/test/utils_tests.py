"""
pchip16 utils tests
"""
#pylint: disable=I0011,R0904

import unittest
import pchip16.utils as utils

class TestTwosCompliment(unittest.TestCase):
    """Test twos-compliment helper functions"""
    def test_0_to_dec(self):
        self.assertEqual(utils.to_dec(0x0), 0)
    def test_0_to_hex(self):
        self.assertEqual(utils.to_hex(0), 0x0)
    def test_1_to_dec(self):
        self.assertEqual(utils.to_dec(0x1), 1)
    def test_1_to_hex(self):
        self.assertEqual(utils.to_hex(1), 0x1)
    def test_max_to_dec(self):
        self.assertEqual(utils.to_dec(0x7FFF), 32767)
    def test_max_to_hex(self):
        self.assertEqual(utils.to_hex(32767), 0x7FFF)
    def test_neg_one_to_dec(self):
        self.assertEqual(utils.to_dec(0xFFFF), -1)
    def test_neg_one_to_hex(self):
        self.assertEqual(utils.to_hex(-1), 0xFFFF)
    def test_neg_max_to_dec(self):
        self.assertEqual(utils.to_dec(0x8000), -32768)
    def test_neg_max_to_hex(self):
        self.assertEqual(utils.to_hex(-32768), 0x8000)
