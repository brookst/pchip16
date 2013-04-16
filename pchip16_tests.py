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

class TestLoadCodes(TestVM):
    def test_LDI_RX_HHLL_instruction(self):
        self.vmac.mem[0x2345] = 0x1
        self.vmac.execute(0x20014523)
        self.assertEqual(self.vmac.register[0x1], 0x1)
        self.vmac.mem[0x2345] = 0xFFFF
        self.vmac.execute(0x20014523)
        self.assertEqual(self.vmac.register[0x1], 0xFFFF)
    def test_LDI_SP_HHLL_instruction(self):
        self.vmac.mem[0x2345] = 0x1
        self.vmac.execute(0x21004523)
        self.assertEqual(self.vmac.stack_pointer, 0x1)
    def test_LDM_RX_HHLL_instruction(self):
        self.vmac.mem[0x2345] = 0x6789
        self.vmac.mem[0x6789] = 0x1
        self.vmac.execute(0x22014523)
        self.assertEqual(self.vmac.register[0x1], 0x1)
    def test_LDM_RX_RY_instruction(self):
        self.vmac.mem[0x2345] = 0x1
        self.vmac.register[0x2] = 0x2345
        self.vmac.execute(0x23210000)
        self.assertEqual(self.vmac.register[0x1], 0x1)
        self.assertRaises(ValueError, self.vmac.execute, 0x23001234)
    def test_MOV_RX_RY_instruction(self):
        self.vmac.register[0x2] = 0x1234
        self.vmac.execute(0x24210000)
        self.assertEqual(self.vmac.register[0x1], 0x1234)
        self.assertRaises(ValueError, self.vmac.execute, 0x24001234)
    def test_invalid_instruction(self):
        self.assertRaises(ValueError, self.vmac.execute, 0x25000000)

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
        self.assertRaises(ValueError, self.vmac.execute, 0x31001234)
    def test_invalid_instruction(self):
        self.assertRaises(ValueError, self.vmac.execute, 0x32000000)

class TestAdditionCodes(TestVM):
    def test_ADDI_RX_HHLL_instructions(self):
        self.vmac.register[0x1] = 0x23
        self.vmac.mem[0x2345] = 0x07
        self.vmac.execute(0x40014523)
        self.assertEqual(self.vmac.register[0x1], 0x2a)
        self.vmac.register[0x1] = 0x23
        self.assertRaises(ValueError, self.vmac.execute, 0x32000000)
    def test_ADD_RX_RY_instruction(self):
        self.vmac.register[0x1] = 0x7
        self.vmac.register[0x2] = 0x23
        self.vmac.execute(0x41210000)
        self.assertEqual(self.vmac.register[0x1], 0x2a)
        self.assertRaises(ValueError, self.vmac.execute, 0x41001234)
    def test_ADD_RX_RY_RZ_instruction(self):
        self.vmac.register[0x1] = 0x7
        self.vmac.register[0x2] = 0x20
        self.vmac.register[0x3] = 0x3
        self.vmac.execute(0x42210300)
        self.assertEqual(self.vmac.register[0x1], 0x2a)
        self.assertRaises(ValueError, self.vmac.execute, 0x42001000)
        self.assertRaises(ValueError, self.vmac.execute, 0x42001023)
        self.assertRaises(ValueError, self.vmac.execute, 0x42001023)
    def test_invalid_instruction(self):
        self.assertRaises(ValueError, self.vmac.execute, 0x43000000)
