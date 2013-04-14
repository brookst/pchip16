import unittest
from pchip16 import VM

class TestVM(unittest.TestCase):
    def test_program_counter_starts_at_zero(self):
        vm = VM()
        self.assertEqual(0, vm.pc)
