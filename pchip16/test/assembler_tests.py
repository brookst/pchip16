"""
pchip16 Assembler test runner
"""
#pylint: disable=I0011, R0904

from __future__ import print_function
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
        self.assertIsNone(self.asm.parse_line(";"))
        self.assertIsNone(self.asm.parse_line(";This is a comment"))
        self.assertIsNone(self.asm.parse_line(" ;"))

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
        self.assertEqual(self.asm.parse_line("MOV RX RY ;This is a comment"), tokens)
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
        code = b"\x24\xf1\x00\x00"
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
    def test_SUBI_rw(self):
        code = b"50014523"
        self.assertEqual(self.asm.assemble_line("SUBI R1 0x2345"), code)
    def test_SUB_rr(self):
        code = b"51210000"
        self.assertEqual(self.asm.assemble_line("SUB R1 R2"), code)
    def test_SUB_rrr(self):
        code = b"52210300"
        self.assertEqual(self.asm.assemble_line("SUB R1 R2 R3"), code)
    def test_CMPI_rw(self):
        code = b"53014523"
        self.assertEqual(self.asm.assemble_line("CMPI R1 0x2345"), code)
    def test_CMP_rr(self):
        code = b"54210000"
        self.assertEqual(self.asm.assemble_line("CMP R1 R2"), code)
## 6x - Bitwise AND (&)
    def test_ANDI_rw(self):
        code = b"60014523"
        self.assertEqual(self.asm.assemble_line("ANDI R1 0x2345"), code)
    def test_AND_rr(self):
        code = b"61210000"
        self.assertEqual(self.asm.assemble_line("AND R1 R2"), code)
    def test_AND_rrr(self):
        code = b"62210300"
        self.assertEqual(self.asm.assemble_line("AND R1 R2 R3"), code)
    def test_TSTI_rw(self):
        code = b"63014523"
        self.assertEqual(self.asm.assemble_line("TSTI R1 0x2345"), code)
    def test_TST_rr(self):
        code = b"64210000"
        self.assertEqual(self.asm.assemble_line("TST R1 R2"), code)
## 7x - Bitwise OR (|)
    def test_ORI_rw(self):
        code = b"70014523"
        self.assertEqual(self.asm.assemble_line("ORI R1 0x2345"), code)
    def test_OR_rr(self):
        code = b"71210000"
        self.assertEqual(self.asm.assemble_line("OR R1 R2"), code)
    def test_OR_rrr(self):
        code = b"72210300"
        self.assertEqual(self.asm.assemble_line("OR R1 R2 R3"), code)
## 8x - Bitwise XOR (^)
    def test_XORI_rw(self):
        code = b"80014523"
        self.assertEqual(self.asm.assemble_line("XORI R1 0x2345"), code)
    def test_XOR_rr(self):
        code = b"81210000"
        self.assertEqual(self.asm.assemble_line("XOR R1 R2"), code)
    def test_XOR_rrr(self):
        code = b"82210300"
        self.assertEqual(self.asm.assemble_line("XOR R1 R2 R3"), code)
## 9x - Multiplication
    def test_MULI_rw(self):
        code = b"90014523"
        self.assertEqual(self.asm.assemble_line("MULI R1 0x2345"), code)
    def test_MUL_rr(self):
        code = b"91210000"
        self.assertEqual(self.asm.assemble_line("MUL R1 R2"), code)
    def test_MUL_rrr(self):
        code = b"92210300"
        self.assertEqual(self.asm.assemble_line("MUL R1 R2 R3"), code)
## Ax - Division
    def test_DIVI_rw(self):
        code = b"a0014523"
        self.assertEqual(self.asm.assemble_line("DIVI R1 0x2345"), code)
    def test_DIV_rr(self):
        code = b"a1210000"
        self.assertEqual(self.asm.assemble_line("DIV R1 R2"), code)
    def test_DIV_rrr(self):
        code = b"a2210300"
        self.assertEqual(self.asm.assemble_line("DIV R1 R2 R3"), code)
    def test_MODI_rw(self):
        code = b"a3014523"
        self.assertEqual(self.asm.assemble_line("MODI R1 0x2345"), code)
    def test_MOD_rr(self):
        code = b"a4210000"
        self.assertEqual(self.asm.assemble_line("MOD R1 R2"), code)
    def test_MOD_rrr(self):
        code = b"a5210300"
        self.assertEqual(self.asm.assemble_line("MOD R1 R2 R3"), code)
    def test_REMI_rw(self):
        code = b"a6014523"
        self.assertEqual(self.asm.assemble_line("REMI R1 0x2345"), code)
    def test_REM_rr(self):
        code = b"a7210000"
        self.assertEqual(self.asm.assemble_line("REM R1 R2"), code)
    def test_REM_rrr(self):
        code = b"a8210300"
        self.assertEqual(self.asm.assemble_line("REM R1 R2 R3"), code)
## Bx - Logical/Arithmetic Shifts
    def test_SHL_rn(self):
        code = b"b0010200"
        self.assertEqual(self.asm.assemble_line("SHL R1 0x2"), code)
    def test_SHR_rn(self):
        code = b"b1010200"
        self.assertEqual(self.asm.assemble_line("SHR R1 0x2"), code)
    def test_SAL_rn(self):
        code = b"b0010200"
        self.assertEqual(self.asm.assemble_line("SAL R1 0x2"), code)
    def test_SAR_rn(self):
        code = b"b1010200"
        self.assertEqual(self.asm.assemble_line("SAR R1 0x2"), code)
    def test_SHL_rr(self):
        code = b"b2210000"
        self.assertEqual(self.asm.assemble_line("SHL R1 R2"), code)
    def test_SHR_rr(self):
        code = b"b3210000"
        self.assertEqual(self.asm.assemble_line("SHR R1 R2"), code)
    def test_SAL_rr(self):
        code = b"b4210000"
        self.assertEqual(self.asm.assemble_line("SAL R1 R2"), code)
    def test_SAR_rr(self):
        code = b"b5210000"
        self.assertEqual(self.asm.assemble_line("SAR R1 R2"), code)
## Cx - Push/Pop
    def test_PUSH_r(self):
        code = b"c0010000"
        self.assertEqual(self.asm.assemble_line("PUSH R1"), code)
    def test_SHR_r(self):
        code = b"c1010000"
        self.assertEqual(self.asm.assemble_line("POP R1"), code)
    def test_PUSHALL(self):
        code = b"c2000000"
        self.assertEqual(self.asm.assemble_line("PUSHALL"), code)
    def test_POPALL(self):
        code = b"c3000000"
        self.assertEqual(self.asm.assemble_line("POPALL"), code)
    def test_PUSHF(self):
        code = b"c4000000"
        self.assertEqual(self.asm.assemble_line("PUSHF"), code)
    def test_POPF(self):
        code = b"c5000000"
        self.assertEqual(self.asm.assemble_line("POPF"), code)
## Dx - Palette
    def test_PAL_w(self):
        code = b"d0003412"
        self.assertEqual(self.asm.assemble_line("PAL 0x1234"), code)
    def test_PAL_r(self):
        code = b"d1010000"
        self.assertEqual(self.asm.assemble_line("PAL R1"), code)
## Ex - Not/Neg
    def test_NOTI_rw(self):
        code = b"e0014523"
        self.assertEqual(self.asm.assemble_line("NOTI R1 0x2345"), code)
    def test_NOT_r(self):
        code = b"e1010000"
        self.assertEqual(self.asm.assemble_line("NOT R1"), code)
    def test_NOT_rr(self):
        code = b"e2210000"
        self.assertEqual(self.asm.assemble_line("NOT R1 R2"), code)
    def test_NEGI_rw(self):
        code = b"e3014523"
        self.assertEqual(self.asm.assemble_line("NEGI R1 0x2345"), code)
    def test_NEG_r(self):
        code = b"e4010000"
        self.assertEqual(self.asm.assemble_line("NEG R1"), code)
    def test_NEG_rr(self):
        code = b"e5210000"
        self.assertEqual(self.asm.assemble_line("NEG R1 R2"), code)

class TestExampleCode(TestAssembler):
    source = """ ldi r6, 3   ; reset score
        ldi r0, 0xFF13
        ;stm r0, ascii_score_val ; and in memory too!
        ldi r0, 40
        stm r0, 0xF300  ; timer mult. const. = 40
        ldi r0, 0x15
        stm r0, 0xF302  ; move cnt reset value = 0x15
    """
    def test_assembly(self):
        self.asm.source = self.source
        print(self.asm.assemble())
