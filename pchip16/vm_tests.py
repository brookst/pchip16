"""
pchip16 test runner
"""
#pylint: disable=I0011, R0904

import unittest
from pchip16 import VM
from pchip16.vm import CARRY, ZERO, OVERFLOW, NEGATIVE
import pchip16.utils as utils

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
    def test_CALL_HHLL_instruction(self):
        self.vmac.mem[0x1234] = 0x5678
        self.vmac.program_counter = 0xBEEF
        self.vmac.execute(0x14003412)
        self.assertEqual(self.vmac.mem[self.vmac.stack_pointer - 2], 0xBEEF)
        self.assertEqual(self.vmac.stack_pointer, 0xFDF2)
        self.assertEqual(self.vmac.program_counter, 0x5678)
    def test_RET_instruction(self):
        self.vmac.stack_pointer = 0xFDF2
        self.vmac.mem[0xFDF0] = 0xBEEF
        self.vmac.program_counter = 0x5678
        self.vmac.execute(0x15000000)
        self.assertEqual(self.vmac.stack_pointer, 0xFDF0)
        self.assertEqual(self.vmac.program_counter, 0xBEEF)
    def test_JMP_RX_instruction(self):
        self.vmac.register[1] = 0xBEEF
        self.vmac.execute(0x16010000)
        self.assertEqual(self.vmac.program_counter, 0xBEEF)
        self.assertRaises(ValueError, self.vmac.execute, 0x16001234)
    def test_CALL_RX_instruction(self):
        self.vmac.register[1] = 0x5678
        self.vmac.program_counter = 0xBEEF
        self.vmac.execute(0x17010000)
        self.assertEqual(self.vmac.mem[self.vmac.stack_pointer - 2], 0xBEEF)
        self.assertEqual(self.vmac.stack_pointer, 0xFDF2)
        self.assertEqual(self.vmac.program_counter, 0x5678)
        self.assertRaises(ValueError, self.vmac.execute, 0x17001234)
    def test_invalid_instruction(self):
        self.assertRaises(ValueError, self.vmac.execute, 0x19000000)

class TestLoadCodes(TestVM):
    def test_LDI_RX_HHLL_instruction(self):
        self.vmac.mem[0x2345] = 0x1
        self.vmac.execute(0x20014523)
        self.assertEqual(self.vmac.register[0x1], 0x1)
        self.vmac.mem[0x2345] = 0xAA55
        self.vmac.execute(0x20014523)
        self.assertEqual(self.vmac.register[0x1], 0xAA55)
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
        self.vmac.register[0x1] = 0xBEEF
        self.vmac.register[0x2] = 0x2
        self.vmac.execute(0x31210000)
        self.assertEqual(self.vmac.mem[0x2], 0xBEEF)
        self.assertRaises(ValueError, self.vmac.execute, 0x31001234)
    def test_invalid_instruction(self):
        self.assertRaises(ValueError, self.vmac.execute, 0x32000000)

class TestAddition(TestVM):
    def test_add_op_zero(self):
        self.vmac.flags |= OVERFLOW | CARRY | NEGATIVE
        value = self.vmac._add(0xFFF9, 0x07)
        self.assertEqual(value, 0x0)
        self.assertFalse(self.vmac.flags & OVERFLOW)
        self.assertTrue(self.vmac.flags & CARRY)
        self.assertTrue(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_add_op_pos(self):
        self.vmac.flags |= OVERFLOW | CARRY | ZERO | NEGATIVE
        value = self.vmac._add(0x23, 0x07)
        self.assertEqual(value, 0x2a)
        self.assertFalse(self.vmac.flags & OVERFLOW)
        self.assertFalse(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_add_op_pos_overflow(self):
        self.vmac.flags |= CARRY | ZERO
        value = self.vmac._add(0x7FFF, 0x0001)
        self.assertEqual(value, 0x8000)
        self.assertTrue(self.vmac.flags & OVERFLOW)
        self.assertFalse(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)
    def test_add_op_neg(self):
        self.vmac.flags |= OVERFLOW | ZERO
        value = self.vmac._add(0xFFFF, 0xFFFF)
        self.assertEqual(value, 0xFFFE)
        self.assertFalse(self.vmac.flags & OVERFLOW)
        self.assertTrue(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)
    def test_add_op_neg_overflow(self):
        self.vmac.flags |= ZERO | NEGATIVE
        value = self.vmac._add(0xFFFF, 0x8000)
        self.assertEqual(value, 0x7FFF)
        self.assertTrue(self.vmac.flags & OVERFLOW)
        self.assertTrue(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)

class TestAdditionCodes(TestVM):
    def test_ADDI_RX_HHLL_instruction(self):
        self.vmac.register[0x1] = 70
        self.vmac.mem[0x2345] = 350
        self.vmac.execute(0x40014523)
        self.assertEqual(self.vmac.register[0x1], 420)
        self.assertRaises(ValueError, self.vmac.execute, 0x40100000)
    def test_ADD_RX_RY_instruction(self):
        self.vmac.register[0x1] = 0x7
        self.vmac.register[0x2] = 0x23
        self.vmac.execute(0x41210000)
        self.assertEqual(self.vmac.register[0x1], 0x2a)
        self.assertRaises(ValueError, self.vmac.execute, 0x41001234)
    def test_ADD_RX_RY_RZ_instruction(self):
        self.vmac.register[0x1] = 0x7
        self.vmac.register[0x2] = 0x23
        self.vmac.execute(0x42210300)
        self.assertEqual(self.vmac.register[0x3], 0x2a)
        self.assertRaises(ValueError, self.vmac.execute, 0x42001000)
        self.assertRaises(ValueError, self.vmac.execute, 0x42000023)
        self.assertRaises(ValueError, self.vmac.execute, 0x42001023)
    def test_invalid_instruction(self):
        self.assertRaises(ValueError, self.vmac.execute, 0x43000000)

class TestSubtraction(TestVM):
    def test_sub_op_zero_zero_zero(self):
        # Subtract 0 from 0
        self.vmac.flags |= OVERFLOW | CARRY | NEGATIVE
        value = self.vmac._sub(0,0)
        self.assertEqual(value, 0)
        self.assertFalse(self.vmac.flags & OVERFLOW)
        self.assertFalse(self.vmac.flags & CARRY)
        self.assertTrue(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_sub_op_pos_pos_zero(self):
        # Subtract 7 from 7
        self.vmac.flags |= OVERFLOW | CARRY | NEGATIVE
        value = self.vmac._sub(7,7)
        self.assertEqual(value, 0x0)
        self.assertFalse(self.vmac.flags & OVERFLOW)
        self.assertFalse(self.vmac.flags & CARRY)
        self.assertTrue(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_sub_op_pos_zero_pos(self):
        # Subtract 0 from 7
        self.vmac.flags |= OVERFLOW | CARRY | ZERO | NEGATIVE
        value = self.vmac._sub(7,0)
        self.assertEqual(value, 7)
        self.assertFalse(self.vmac.flags & OVERFLOW)
        self.assertFalse(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_sub_op_pos_pos_pos(self):
        # Subtract 7 from 49
        self.vmac.flags |= OVERFLOW | CARRY | ZERO | NEGATIVE
        value = self.vmac._sub(49, 7)
        self.assertEqual(value, 42)
        self.assertFalse(self.vmac.flags & OVERFLOW)
        self.assertFalse(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_sub_op_pos_pos_neg(self):
        # Subtract 49 from 7
        self.vmac.flags |= OVERFLOW | ZERO
        value = self.vmac._sub(7, 49)
        self.assertEqual(value, utils.to_hex(-42) )
        self.assertFalse(self.vmac.flags & OVERFLOW)
        self.assertTrue(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)
    def test_sub_op_neg_pos_pos_underflow(self):
        # Subtract POS_MAX from -2
        self.vmac.flags |= CARRY | ZERO | NEGATIVE
        value = self.vmac._sub(utils.to_hex(-2), 0x7FFF)
        self.assertEqual(value, 0x7FFF)
        self.assertTrue(self.vmac.flags & OVERFLOW)
        self.assertFalse(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_sub_op_pos_neg_neg_overflow(self):
        # Subtract -2 from POS_MAX
        self.vmac.flags |= ZERO
        value = self.vmac._sub(0x7FFF, utils.to_hex(-2) )
        self.assertEqual(value, 0x8001)
        self.assertTrue(self.vmac.flags & OVERFLOW)
        self.assertTrue(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)
    def test_sub_op_neg_pos_pos_overflow(self):
        # Subtract 1 from NEG_MIN
        self.vmac.flags |= ZERO | NEGATIVE
        value = self.vmac._sub(0x8000, 0x1)
        self.assertEqual(value, 0x7FFF)
        self.assertTrue(self.vmac.flags & OVERFLOW)
        self.assertFalse(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_sub_op_pos_neg_pos_underflow(self):
        # Subtract 1 from NEG_MIN
        self.vmac.flags |= ZERO | NEGATIVE
        value = self.vmac._sub(0x1, 0x8000)
        self.assertEqual(value, 0x8001)
        self.assertTrue(self.vmac.flags & OVERFLOW)
        self.assertTrue(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)

class TestSubtractionCodes(TestVM):
    def test_SUBI_RX_HHLL_instruction(self):
        self.vmac.register[0x1] = 70
        self.vmac.mem[0x2345] = 490
        self.vmac.execute(0x50014523)
        self.assertEqual(self.vmac.register[0x1], utils.complement(420) )
        self.assertRaises(ValueError, self.vmac.execute, 0x50100000)
    def test_SUB_RX_RY_instruction(self):
        self.vmac.register[0x1] = 7
        self.vmac.register[0x2] = 49
        self.vmac.execute(0x51210000)
        self.assertEqual(self.vmac.register[0x1], utils.complement(42) )
        self.assertRaises(ValueError, self.vmac.execute, 0x51001234)
    def test_SUB_RX_RY_RZ_instruction(self):
        self.vmac.register[0x1] = 7
        self.vmac.register[0x2] = 49
        self.vmac.execute(0x52210300)
        self.assertEqual(self.vmac.register[0x3], utils.complement(42) )
        self.assertRaises(ValueError, self.vmac.execute, 0x52001000)
        self.assertRaises(ValueError, self.vmac.execute, 0x52000023)
        self.assertRaises(ValueError, self.vmac.execute, 0x52001023)
    def test_CMPI_RX_HHLL_instruction(self):
        self.vmac.register[0x1] = 70
        self.vmac.mem[0x2345] = 490
        self.vmac.execute(0x53014523)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)
        self.vmac.register[0x1] = 700
        self.vmac.mem[0x2345] = 700
        self.vmac.execute(0x53014523)
        self.assertTrue(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
        self.assertRaises(ValueError, self.vmac.execute, 0x53100000)
    def test_CMP_RX_RY_instruction(self):
        self.vmac.register[0x1] = 7
        self.vmac.register[0x2] = 49
        self.vmac.execute(0x54210000)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)
        self.vmac.register[0x1] = 7
        self.vmac.register[0x2] = 7
        self.vmac.execute(0x54210000)
        self.assertTrue(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
        self.assertRaises(ValueError, self.vmac.execute, 0x54001234)
    def test_invalid_instruction(self):
        self.assertRaises(ValueError, self.vmac.execute, 0x55000000)

class TestBitwiseAnd(TestVM):
    def test_and_zero_zero_zero(self):
        value = self.vmac._and(0, 0)
        self.assertEqual(value, 0)
        self.assertTrue(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_and_pos_pos_pos(self):
        value = self.vmac._and(0x6666, 0x3333)
        self.assertEqual(value, 0x2222)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_and_neg_neg_neg(self):
        value = self.vmac._and(0xAAAA, 0xCCCC)
        self.assertEqual(value, 0x8888)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)

class TestBitwiseAndCodes(TestVM):
    def test_ANDI_RX_HHLL_instruction(self):
        self.vmac.register[0x1] = 0x6666
        self.vmac.mem[0x2345] = 0x3333
        self.vmac.execute(0x60014523)
        self.assertEqual(self.vmac.register[0x1], 0x2222)
        self.assertRaises(ValueError, self.vmac.execute, 0x60100000)
    def test_AND_RX_RY_instruction(self):
        self.vmac.register[0x1] = 0x6666
        self.vmac.register[0x2] = 0x3333
        self.vmac.execute(0x61210000)
        self.assertEqual(self.vmac.register[0x1], 0x2222)
        self.assertRaises(ValueError, self.vmac.execute, 0x61001234)
    def test_AND_RX_RY_RZ_instruction(self):
        self.vmac.register[0x1] = 0x6666
        self.vmac.register[0x2] = 0x3333
        self.vmac.execute(0x62210300)
        self.assertEqual(self.vmac.register[0x3], 0x2222)
        self.assertRaises(ValueError, self.vmac.execute, 0x62001000)
        self.assertRaises(ValueError, self.vmac.execute, 0x62000023)
        self.assertRaises(ValueError, self.vmac.execute, 0x62001023)
    def test_TSTI_RX_HHLL_instruction(self):
        self.vmac.register[0x1] = 0xAAAA
        self.vmac.mem[0x2345] = 0xCCCC
        self.vmac.execute(0x63014523)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)
        self.vmac.register[0x1] = 0x6666
        self.vmac.mem[0x2345] = 0x9999
        self.vmac.execute(0x63014523)
        self.assertTrue(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
        self.assertRaises(ValueError, self.vmac.execute, 0x63100000)
    def test_TST_RX_RY_instruction(self):
        self.vmac.register[0x1] = 0xAAAA
        self.vmac.register[0x2] = 0xCCCC
        self.vmac.execute(0x64210000)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)
        self.vmac.register[0x1] = 0x6666
        self.vmac.register[0x2] = 0x9999
        self.vmac.execute(0x64210000)
        self.assertTrue(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
        self.assertRaises(ValueError, self.vmac.execute, 0x64001234)
    def test_invalid_instruction(self):
        self.assertRaises(ValueError, self.vmac.execute, 0x65000000)

class TestBitwiseOr(TestVM):
    def test_or_zero_zero_zero(self):
        value = self.vmac._or(0, 0)
        self.assertEqual(value, 0)
        self.assertTrue(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_or_pos_pos_pos(self):
        value = self.vmac._or(0x6666, 0x3333)
        self.assertEqual(value, 0x7777)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_or_neg_neg_neg(self):
        value = self.vmac._or(0xAAAA, 0xCCCC)
        self.assertEqual(value, 0xEEEE)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)

class TestBitwiseOrCodes(TestVM):
    def test_ORI_RX_HHLL_instruction(self):
        self.vmac.register[0x1] = 0x6666
        self.vmac.mem[0x2345] = 0x3333
        self.vmac.execute(0x70014523)
        self.assertEqual(self.vmac.register[0x1], 0x7777)
        self.assertRaises(ValueError, self.vmac.execute, 0x70100000)
    def test_OR_RX_RY_instruction(self):
        self.vmac.register[0x1] = 0x6666
        self.vmac.register[0x2] = 0x3333
        self.vmac.execute(0x71210000)
        self.assertEqual(self.vmac.register[0x1], 0x7777)
        self.assertRaises(ValueError, self.vmac.execute, 0x71001234)
    def test_OR_RX_RY_RZ_instruction(self):
        self.vmac.register[0x1] = 0x6666
        self.vmac.register[0x2] = 0x3333
        self.vmac.execute(0x72210300)
        self.assertEqual(self.vmac.register[0x3], 0x7777)
        self.assertRaises(ValueError, self.vmac.execute, 0x72001000)
        self.assertRaises(ValueError, self.vmac.execute, 0x72000023)
        self.assertRaises(ValueError, self.vmac.execute, 0x72001023)
    def test_invalid_instruction(self):
        self.assertRaises(ValueError, self.vmac.execute, 0x73000000)

class TestBitwiseXor(TestVM):
    def test_xor_zero_zero_zero(self):
        value = self.vmac._xor(0, 0)
        self.assertEqual(value, 0)
        self.assertTrue(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_xor_pos_pos_pos(self):
        value = self.vmac._xor(0x6666, 0x3333)
        self.assertEqual(value, 0x5555)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_xor_neg_pos_neg(self):
        value = self.vmac._xor(0xAAAA, 0x6666)
        self.assertEqual(value, 0xCCCC)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)
    def test_xor_neg_neg_pos(self):
        value = self.vmac._xor(0xAAAA, 0xCCCC)
        self.assertEqual(value, 0x6666)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)

class TestBitwiseXorCodes(TestVM):
    def test_XORI_RX_HHLL_instruction(self):
        self.vmac.register[0x1] = 0x6666
        self.vmac.mem[0x2345] = 0x3333
        self.vmac.execute(0x80014523)
        self.assertEqual(self.vmac.register[0x1], 0x5555)
        self.assertRaises(ValueError, self.vmac.execute, 0x80100000)
    def test_XOR_RX_RY_instruction(self):
        self.vmac.register[0x1] = 0x6666
        self.vmac.register[0x2] = 0x3333
        self.vmac.execute(0x81210000)
        self.assertEqual(self.vmac.register[0x1], 0x5555)
        self.assertRaises(ValueError, self.vmac.execute, 0x81001234)
    def test_XOR_RX_RY_RZ_instruction(self):
        self.vmac.register[0x1] = 0x6666
        self.vmac.register[0x2] = 0x3333
        self.vmac.execute(0x82210300)
        self.assertEqual(self.vmac.register[0x3], 0x5555)
        self.assertRaises(ValueError, self.vmac.execute, 0x82001000)
        self.assertRaises(ValueError, self.vmac.execute, 0x82000023)
        self.assertRaises(ValueError, self.vmac.execute, 0x82001023)
    def test_invalid_instruction(self):
        self.assertRaises(ValueError, self.vmac.execute, 0x83000000)

class TestMultiplication(TestVM):
    def test_mul_op_zero(self):
        self.vmac.flags |= CARRY | NEGATIVE
        value = self.vmac._mul(0x0, 0x7)
        self.assertEqual(value, 0x0)
        self.assertFalse(self.vmac.flags & CARRY)
        self.assertTrue(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_mul_op_pos(self):
        self.vmac.flags |= CARRY | ZERO | NEGATIVE
        value = self.vmac._mul(3, 14)
        self.assertEqual(value, 0x2a)
        self.assertFalse(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_mul_op_pos_overflow(self):
        self.vmac.flags |= CARRY | ZERO
        value = self.vmac._mul(0x7FFF, 0x7FFF)
        self.assertEqual(value, 1)
        self.assertTrue(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_mul_op_neg(self):
        self.vmac.flags |= ZERO
        value = self.vmac._mul(0xFFFF, 0xFFFF)
        self.assertEqual(value, 1)
        self.assertFalse(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_mul_op_neg_overflow(self):
        self.vmac.flags |= ZERO | NEGATIVE
        value = self.vmac._mul(0x8FFF, 0x8000)
        self.assertEqual(value, 0x8000)
        self.assertTrue(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)

class TestMultiplicationCodes(TestVM):
    def test_MULI_RX_HHLL_instruction(self):
        self.vmac.register[0x1] = 3
        self.vmac.mem[0x2345] = 1400
        self.vmac.execute(0x90014523)
        self.assertEqual(self.vmac.register[0x1], 4200)
        self.assertRaises(ValueError, self.vmac.execute, 0x90100000)
    def test_MUL_RX_RY_instruction(self):
        self.vmac.register[0x1] = 3
        self.vmac.register[0x2] = 14
        self.vmac.execute(0x91210000)
        self.assertEqual(self.vmac.register[0x1], 42)
        self.assertRaises(ValueError, self.vmac.execute, 0x91001234)
    def test_MUL_RX_RY_RZ_instruction(self):
        self.vmac.register[0x1] = 3
        self.vmac.register[0x2] = 14
        self.vmac.execute(0x92210300)
        self.assertEqual(self.vmac.register[0x3], 42)
        self.assertRaises(ValueError, self.vmac.execute, 0x92001000)
        self.assertRaises(ValueError, self.vmac.execute, 0x92000023)
        self.assertRaises(ValueError, self.vmac.execute, 0x92001023)
    def test_invalid_instruction(self):
        self.assertRaises(ValueError, self.vmac.execute, 0x93000000)

class TestDivision(TestVM):
    def test_div_op_zero(self):
        self.vmac.flags |= CARRY | NEGATIVE
        value = self.vmac._div(0x0, 0x7)
        self.assertEqual(value, 0x0)
        self.assertFalse(self.vmac.flags & CARRY)
        self.assertTrue(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_div_op_pos(self):
        self.vmac.flags |= CARRY | ZERO | NEGATIVE
        value = self.vmac._div(84, 2)
        self.assertEqual(value, 0x2a)
        self.assertFalse(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_div_op_pos_overflow(self):
        self.vmac.flags |= ZERO | NEGATIVE
        value = self.vmac._div(85, 2)
        self.assertEqual(value, 42)
        self.assertTrue(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
    def test_div_op_neg(self):
        self.vmac.flags |= CARRY | ZERO
        value = self.vmac._div(4, 0xFFFE)
        self.assertEqual(value, 0xFFFE)
        self.assertFalse(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)
    def test_div_op_neg_overflow(self):
        self.vmac.flags |= ZERO
        value = self.vmac._div(5, 0xFFFE)
        self.assertEqual(value, 0xFFFD)
        self.assertTrue(self.vmac.flags & CARRY)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)

class TestDivisionCodes(TestVM):
    def test_DIVI_RX_HHLL_instruction(self):
        self.vmac.register[0x1] = 84
        self.vmac.mem[0x2345] = 2
        self.vmac.execute(0xA0014523)
        self.assertEqual(self.vmac.register[0x1], 42)
        self.assertRaises(ValueError, self.vmac.execute, 0xA0100000)
    def test_DIV_RX_RY_instruction(self):
        self.vmac.register[0x1] = 84
        self.vmac.register[0x2] = 2
        self.vmac.execute(0xA1210000)
        self.assertEqual(self.vmac.register[0x1], 42)
        self.assertRaises(ValueError, self.vmac.execute, 0xA1001234)
    def test_DIV_RX_RY_RZ_instruction(self):
        self.vmac.register[0x1] = 84
        self.vmac.register[0x2] = 2
        self.vmac.execute(0xA2210300)
        self.assertEqual(self.vmac.register[0x3], 42)
        self.assertRaises(ValueError, self.vmac.execute, 0xA2001000)
        self.assertRaises(ValueError, self.vmac.execute, 0xA2000023)
        self.assertRaises(ValueError, self.vmac.execute, 0xA2001023)
    def test_invalid_instruction(self):
        self.assertRaises(ValueError, self.vmac.execute, 0xA3000000)

class TestShiftCodes(TestVM):
    def test_SHL_RX_N_instruction(self):
        self.vmac.flags |= ZERO | NEGATIVE
        self.vmac.register[0x1] = 0xAAAA
        self.vmac.execute(0xB0010100)
        self.assertEqual(self.vmac.register[0x1], 0x5554)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
        self.assertRaises(ValueError, self.vmac.execute, 0xB0001023)
    def test_SHR_RX_N_instruction(self):
        self.vmac.flags |= ZERO | NEGATIVE
        self.vmac.register[0x1] = 0xAAAA
        self.vmac.execute(0xB1010100)
        self.assertEqual(self.vmac.register[0x1], 0x5555)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
        self.assertRaises(ValueError, self.vmac.execute, 0xB1001023)
    def test_SAR_RX_N_instruction(self):
        self.vmac.flags |= ZERO | NEGATIVE
        self.vmac.register[0x1] = 0xAAAA
        self.vmac.execute(0xB2010100)
        self.assertEqual(self.vmac.register[0x1], 0xD555)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)
        self.assertRaises(ValueError, self.vmac.execute, 0xB2001023)
    def test_SHL_RX_RY_instruction(self):
        self.vmac.flags |= ZERO | NEGATIVE
        self.vmac.register[0x1] = 0xAAAA
        self.vmac.register[0x2] = 1
        self.vmac.execute(0xB3210000)
        self.assertEqual(self.vmac.register[0x1], 0x5554)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
        self.assertRaises(ValueError, self.vmac.execute, 0xB3001234)
    def test_SHR_RX_RY_instruction(self):
        self.vmac.flags |= ZERO | NEGATIVE
        self.vmac.register[0x1] = 0xAAAA
        self.vmac.register[0x2] = 1
        self.vmac.execute(0xB4210000)
        self.assertEqual(self.vmac.register[0x1], 0x5555)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertFalse(self.vmac.flags & NEGATIVE)
        self.assertRaises(ValueError, self.vmac.execute, 0xB4001023)
    def test_SAR_RX_RY_instruction(self):
        self.vmac.flags |= ZERO | NEGATIVE
        self.vmac.register[0x1] = 0xAAAA
        self.vmac.register[0x2] = 1
        self.vmac.execute(0xB5210000)
        self.assertEqual(self.vmac.register[0x1], 0xD555)
        self.assertFalse(self.vmac.flags & ZERO)
        self.assertTrue(self.vmac.flags & NEGATIVE)
        self.assertRaises(ValueError, self.vmac.execute, 0xB5001023)
    def test_invalid_instruction(self):
        self.assertRaises(ValueError, self.vmac.execute, 0xB6000000)

class TestStackCodes(TestVM):
    def test_PUSH_RX_instruction(self):
        self.vmac.register[0x1] = 0xAAAA
        self.vmac.execute(0xC0010000)
        self.assertEqual(self.vmac.mem[0xFDF0], 0xAAAA)
        self.assertEqual(self.vmac.stack_pointer, 0xFDF2)
        self.assertRaises(ValueError, self.vmac.execute, 0xC0001234)
    def test_POP_RX_instruction(self):
        self.vmac.stack_pointer = 0xFDF2
        self.vmac.mem[0xFDF2] = 0xAAAA
        self.vmac.execute(0xC1010000)
        self.assertEqual(self.vmac.register[1], 0xAAAA)
        self.assertEqual(self.vmac.stack_pointer, 0xFDF0)
        self.assertRaises(ValueError, self.vmac.execute, 0xC1001234)
    def pattern(self, x):
        return (x << 12) + (x << 8) + (x << 4) + x
    def test_PUSHALL_instruction(self):
        for i in range(16):
            self.vmac.register[i] = self.pattern(i)
        self.vmac.execute(0xC2000000)
        for i in range(16):
            self.assertEqual(self.vmac.mem[0xFDF0 + 2 * i], self.pattern(i) )
        self.assertEqual(self.vmac.stack_pointer, 0xFE10)
        self.assertRaises(ValueError, self.vmac.execute, 0xC2123456)
    def test_POPALL_instruction(self):
        self.vmac.stack_pointer = 0xFDF0 + 32
        for i in range(16):
            self.vmac.mem[0xFDF0 + 2 * i] = self.pattern(i)
        self.vmac.execute(0xC3000000)
        self.assertEqual(self.vmac.stack_pointer, 0xFDF0)
        for i in range(16):
            self.assertEqual(self.vmac.register[i], self.pattern(i) )
        self.assertRaises(ValueError, self.vmac.execute, 0xC3123456)
    def test_PUSHF_instruction(self):
        self.vmac.flags = 0xAAAA
        self.vmac.execute(0xC4000000)
        self.assertEqual(self.vmac.mem[self.vmac.stack_pointer -2], 0xAAAA)
        self.assertEqual(self.vmac.stack_pointer, 0xFDF2)
        self.assertRaises(ValueError, self.vmac.execute, 0xC4123456)
    def test_POPF_instruction(self):
        self.vmac.stack_pointer = 0xFDF2
        self.vmac.mem[0xFDF0] = 0xAAAA
        self.vmac.execute(0xC5000000)
        self.assertEqual(self.vmac.flags, 0xAAAA)
        self.assertEqual(self.vmac.stack_pointer, 0xFDF0)
        self.assertRaises(ValueError, self.vmac.execute, 0xC5123456)
    def test_invalid_instruction(self):
        self.assertRaises(ValueError, self.vmac.execute, 0xC6000000)
