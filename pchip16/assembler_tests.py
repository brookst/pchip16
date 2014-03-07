"""
pchip16 Assembler test runner
"""
#pylint: disable=I0011, R0904

import unittest
from pchip16.assembler import Assembler

class TestAssembler(unittest.TestCase):
    """Test aspects of the assembler"""
    def setUp(self):
        self.asm = Assembler()

class TestParsing(TestAssembler):
    """Test source text parsing"""
    def test_empty_lines(self):
        self.assertIsNone(self.asm.parse_line(""))
    def test_spaced_lines(self):
        self.assertIsNone(self.asm.parse_line("    "))
    def test_tabbed_lines(self):
        self.assertIsNone(self.asm.parse_line("	"))
    def test_comment_lines(self):
        self.assertIsNone(self.asm.parse_line("#"))
        self.assertIsNone(self.asm.parse_line("#This is a comment"))
        self.assertIsNone(self.asm.parse_line(" #"))

    def test_nullary_op(self):
        tokens = ["NOP"]
        self.assertEqual(self.asm.parse_line("NOP"), tokens)
    def test_unary_op(self):
        tokens = ["JMP", "RX"]
        self.assertEqual(self.asm.parse_line("JMP RX"), tokens)
    def test_binary_op(self):
        tokens = ["MOV", "RX", "RY"]
        self.assertEqual(self.asm.parse_line("MOV RX RY"), tokens)
    def test_trinary_op(self):
        tokens = ["ADD","RX","RY","RZ"]
        self.assertEqual(self.asm.parse_line("ADD RX RY RZ"), tokens)

    def test_ops_with_comment(self):
        tokens = ["MOV", "RX", "RY"]
        self.assertEqual(self.asm.parse_line("MOV RX RY #This is a comment"), tokens)
    def test_lowercase(self):
        tokens = ["MOV", "RX", "RY"]
        self.assertEqual(self.asm.parse_line("mov rx ry"), tokens)
    def test_commas(self):
        tokens = ["MOV", "RX", "RY"]
        self.assertEqual(self.asm.parse_line("MOV RX, RY"), tokens)

class TestLineAssembly(TestAssembler):
    """Test source text parsing"""
    def test_nullary_op(self):
        code = b"01000000"
        self.assertEqual(self.asm.assemble_line("CLS"), code)
    def test_unary_op(self):
        code = b"16010000"
        self.assertEqual(self.asm.assemble_line("JMP r1"), code)
    def test_binary_op(self):
        code = b"24f10000"
        self.assertEqual(self.asm.assemble_line("mov r1 rf"), code)
    def test_trinary_op(self):
        code = b"42210300"
        self.assertEqual(self.asm.assemble_line("ADD R1, R2, R3"), code)

class TestOPAssembly(TestAssembler):
    """Test OP Codes are assembled properly"""
## 0x - Misc/Video/Audio
    def test_NOP(self):
        code = b"00000000"
        self.assertEqual(self.asm.assemble_line("NOP"), code)
    def test_CLS(self):
        code = b"01000000"
        self.assertEqual(self.asm.assemble_line("CLS"), code)
    def test_VBLNK(self):
        code = b"02000000"
        self.assertEqual(self.asm.assemble_line("VBLNK"), code)
    def test_BGC(self):
        code = b"03000100"
        self.assertEqual(self.asm.assemble_line("BGC 0x1"), code)
    def test_SPR_w(self):
        code = b"04003412"
        self.assertEqual(self.asm.assemble_line("SPR 0x1234"), code)
    def test_DRW_rrw(self):
        code = b"05215634"
        self.assertEqual(self.asm.assemble_line("DRW r1 r2 0x3456"), code)
    def test_DRW_rrr(self):
        code = b"06210300"
        self.assertEqual(self.asm.assemble_line("DRW r1 r2 r3"), code)
    def test_RND_rw(self):
        code = b"07014523"
        self.assertEqual(self.asm.assemble_line("RND r1 0x2345"), code)
    def test_FLIP_00(self):
        code = b"08000000"
        self.assertEqual(self.asm.assemble_line("FLIP 0, 0"), code)
    def test_FLIP_01(self):
        code = b"08000001"
        self.assertEqual(self.asm.assemble_line("FLIP 0, 1"), code)
    def test_FLIP_10(self):
        code = b"08000002"
        self.assertEqual(self.asm.assemble_line("FLIP 1, 0"), code)
    def test_FLIP_11(self):
        code = b"08000003"
        self.assertEqual(self.asm.assemble_line("FLIP 1, 1"), code)
    def test_SND0(self):
        code = b"09000000"
        self.assertEqual(self.asm.assemble_line("SND0"), code)
    def test_SND1_w(self):
        code = b"0a003412"
        self.assertEqual(self.asm.assemble_line("SND1 0x1234"), code)
    def test_SND2_w(self):
        code = b"0b003412"
        self.assertEqual(self.asm.assemble_line("SND2 0x1234"), code)
    def test_SND3_w(self):
        code = b"0c003412"
        self.assertEqual(self.asm.assemble_line("SND3 0x1234"), code)
    def test_SNP_rw(self):
        code = b"0d014523"
        self.assertEqual(self.asm.assemble_line("SNP r1, 0x2345"), code)
    def test_SNG_bw(self):
        code = b"0eff3412"
        self.assertEqual(self.asm.assemble_line("SNG 0xFF, 0x1234"), code)

## 1x - Jumps (Branches)
    def test_JMP_w(self):
        code = b"10003412"
        self.assertEqual(self.asm.assemble_line("JMP 0x1234"), code)
    #TODO: Jx
    # def test_Jc_w(self):
    #     code = b"12013412"
    #     self.assertEqual(self.asm.assemble_line("Jc 0x1234"), code)
    # def test_Jz_w(self):
    #     code = b"12023412"
    #     self.assertEqual(self.asm.assemble_line("Jz 0x1234"), code)
    # def test_Jo_w(self):
    #     code = b"12063412"
    #     self.assertEqual(self.asm.assemble_line("Jo 0x1234"), code)
    # def test_Jn_w(self):
    #     code = b"12073412"
    #     self.assertEqual(self.asm.assemble_line("Jn 0x1234"), code)
    def test_JME_rrw(self):
        code = b"13215634"
        self.assertEqual(self.asm.assemble_line("JME r1, r2, 0x3456"), code)
    def test_CALL_w(self):
        code = b"14003412"
        self.assertEqual(self.asm.assemble_line("CALL 0x1234"), code)
    def test_RET(self):
        code = b"15000000"
        self.assertEqual(self.asm.assemble_line("RET"), code)
    def test_JMP_r(self):
        code = b"16010000"
        self.assertEqual(self.asm.assemble_line("JMP r1"), code)
    #TODO: implement conditional operators
    # def test_Cc_w(self):
    #     code = b"17013412"
    #     self.assertEqual(self.asm.assemble_line("Cc 0x1234"), code)
    # def test_Cz_w(self):
    #     code = b"17023412"
    #     self.assertEqual(self.asm.assemble_line("Cz 0x1234"), code)
    # def test_Co_w(self):
    #     code = b"17063412"
    #     self.assertEqual(self.asm.assemble_line("Co 0x1234"), code)
    # def test_Cn_w(self):
    #     code = b"17073412"
    #     self.assertEqual(self.asm.assemble_line("Cn 0x1234"), code)
    def test_CALL_r(self):
        code = b"18010000"
        self.assertEqual(self.asm.assemble_line("CALL r1"), code)

## 2x - Loads
    def test_LDI_rw(self):
        code = b"20014523"
        self.assertEqual(self.asm.assemble_line("LDI r1, 0x2345"), code)
    def test_LDI_sw(self):
        code = b"21003412"
        self.assertEqual(self.asm.assemble_line("LDI sp, 0x1234"), code)
    def test_LDM_rw(self):
        code = b"22014523"
        self.assertEqual(self.asm.assemble_line("LDM r1, 0x2345"), code)
    def test_LDM_rr(self):
        code = b"23210000"
        self.assertEqual(self.asm.assemble_line("LDM r1, r2"), code)
    def test_MOV(self):
        code = b"24f10000"
        self.assertEqual(self.asm.assemble_line("mov r1 rf"), code)

## 3x - Stores
    def test_STM_rw(self):
        code = b"30014523"
        self.assertEqual(self.asm.assemble_line("STM r1, 0x2345"), code)
    def test_STM_rr(self):
        code = b"31210000"
        self.assertEqual(self.asm.assemble_line("STM r1, r2"), code)

## 4x - Addition
    def test_ADDI_rw(self):
        code = b"40014523"
        self.assertEqual(self.asm.assemble_line("ADDI R1 0x2345"), code)
    def test_ADD_rr(self):
        code = b"41210000"
        self.assertEqual(self.asm.assemble_line("ADD R1 R2"), code)
    def test_ADD_rrr(self):
        code = b"42210300"
        self.assertEqual(self.asm.assemble_line("ADD R1 R2 R3"), code)
## 5x - Subtraction
## 6x - Bitwise AND (&)
## 7x - Bitwise OR (|)
## 8x - Bitwise XOR (^)
## 9x - Multiplication
## Ax - Division
## Bx - Logical/Arithmetic Shifts
## Cx - Push/Pop
## Dx - Palette
## Ex - Not/Neg
