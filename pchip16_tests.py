"""
pchip16 test runner
"""
#pylint: disable=I0011, R0904, C0111

import unittest
from pchip16 import VM

class TestVM(unittest.TestCase):
    """Test aspects of the virtual machine"""
    def setUp(self):
        self.vmac = VM()

class TestMisc(TestVM):
    def test_program_counter(self):
        self.assertEqual(0, self.vmac.program_counter)
        self.vmac.step()
        self.assertEqual(1, self.vmac.program_counter)
    def test_nop_instruction(self):
        self.vmac.execute(0x00000000)

class TestJumpCodes(TestVM):
    def test_JMP_HHLL_instruction(self):
        self.vmac.execute(0x10000000)
        self.assertEqual(0, self.vmac.program_counter)
        self.vmac.execute(0x10003412)
        self.assertEqual(0x1234, self.vmac.program_counter)
    def test_JME_RX_RY_HHLL_instruction(self):
        self.vmac.execute(0x13563412)
        self.assertEqual(0x1234, self.vmac.program_counter)
        self.vmac.register[0x6] = 0x1
        self.vmac.execute(0x13569078)
        self.assertEqual(0x1234, self.vmac.program_counter)

class TestStoreCodes(TestVM):
    def test_STM_RX_HHLL_instruction(self):
        self.vmac.register[0x1] = 0x1
        self.vmac.execute(0x30014523)
        self.assertEqual(self.vmac.mem[0x2345], 0x1)
    def test_STM_RX_RY_instruction(self):
        self.vmac.register[0x1] = 0x1
        self.vmac.register[0x2] = 0x2
        self.vmac.execute(0x31210000)
        self.assertEqual(self.vmac.mem[0x2], 0x1)
