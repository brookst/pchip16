"""
pchip16 test runner
"""
#pylint: disable=I0011, R0904, C0111

import unittest
from pchip16 import VM

class TestVM(unittest.TestCase):
    """Test aspects of the virtual machine"""
    def test_program_counter(self):
        vmac = VM()
        self.assertEqual(0, vmac.program_counter)
        vmac.step()
        self.assertEqual(1, vmac.program_counter)
    def test_nop_instruction(self):
        vmac = VM()
        vmac.execute(0x00000000)
    def test_JMP_HHLL_instruction(self):
        vmac = VM()
        vmac.execute(0x10000000)
        self.assertEqual(0, vmac.program_counter)
        vmac.execute(0x10003412)
        self.assertEqual(0x1234, vmac.program_counter)
