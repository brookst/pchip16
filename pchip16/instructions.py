"""
chip16 instruction format strings
"""
#pylint: disable=W0142,R0903
from pchip16.utils import to_hex

class SignatureMismatch(Exception):
    """Tokens do not match operator match"""
    pass

class Expectation(object):
    """Template for token expectations"""
    pass

class Reg(Expectation):
    """Expectation of a unary_register identifier"""
    @staticmethod
    def __call__(token):
        if len(token) == 2 and token[0] == 'R':
            try:
                return int(token[1], 16)
            except ValueError:
                pass
        raise ValueError("Not a unary_register %s" %token)

class Sp(Expectation):
    """Expectation of the stack pointer identifier"""
    @staticmethod
    def __call__(token):
        if token == 'SP':
            return ""
        raise ValueError("Not stack pointer %s" %token)
class Word(Expectation):
    """Expectation of a unary_word sized value"""
    def __init__(self, size=16):
        self.size = size
        self.d_max = (2 ** (size - 1)) -1
        self.d_min = -(2 ** (size - 1))
    def __call__(self, token):
        value = 0
        if token[:2] == '0X':
            try:
                value = to_hex(int(token, 16))
                return ((value & 0xFF) << 8) | value >> 8
            except ValueError:
                raise ValueError("Not a value %s" %token)
        else:
            return to_hex(int(token))
        raise ValueError("Not a value %s" %token)

class Nibble(Word):
    """Expectation of a nibble sized value"""
    def __init__(self):
        Word.__init__(self, 4)
    def __call__(self, token):
        value = 0
        if token[:2] == '0X':
            try:
                return int(token, 16)
            except ValueError:
                raise ValueError("Not a value %s" %token)
        else:
            return int(token)
        if self.d_max >= value >= self.d_min:
            return value
        raise ValueError("Not a value %s" %token)
class Byte(Word):
    """Expectation of a byte sized value"""
    def __init__(self, size=8):
        Word.__init__(self, 8)
    def __call__(self, token):
        value = 0
        if token[:2] == '0X':
            try:
                return int(token, 16)
            except ValueError:
                raise ValueError("Not a value %s" %token)
        else:
            return int(token)
        if self.d_max >= value >= self.d_min:
            return value
        raise ValueError("Not a value %s" %token)
class Op(Expectation):
    """Expectation of the op code"""
    def __init__(self, code):
        self.code = code
    def __call__(self, token):
        return self.code
def match(tokens, *args):
    """Check tokens match expectation"""
    if len(tokens) != len(args):
        return False
    for arg, token in zip(args, tokens):
        try:
            arg(token)
        except ValueError:
            return False
    return True
def signature(pattern, *expectations):
    """Instruction closure"""
    def ret(tokens):
        """Encode closed operation"""
        if match(tokens, *expectations):
            tokens = [expectation(token) for expectation, token in \
                     zip(expectations, tokens)]
            return pattern.format(*tokens)
        else:
            raise SignatureMismatch()
    return ret

def nullary(code):
    """0 operand instruction closure"""
    return signature("{0:02x}000000", Op(code))
def unary_reg(code):
    """1 operand instruction closure"""
    return signature("{0:02x}0{1:01x}0000", Op(code), Reg())
def unary_word(code):
    """1 operand instruction closure"""
    return signature("{0:02x}00{1:04x}", Op(code), Word())
def nibble(code):
    """1 operand instruction closure"""
    return signature("{0:02x}00{1:02x}00", Op(code), Nibble())
def binary_reg_reg(code):
    """2 operand instruction closure"""
    return signature("{0:02x}{2:01x}{1:01x}0000", Op(code), Reg(), Reg())
def binary_reg_word(code):
    """2 operand instruction closure"""
    return signature("{0:02x}0{1:01x}{2:04x}", Op(code), Reg(), Word())
def binary_reg_nibble(code):
    """2 operand instruction closure"""
    return signature("{0:02x}0{1:01x}0{2:01x}00", Op(code), Reg(), Nibble())
def byte_word(code):
    """2 operand instruction closure"""
    return signature("{0:02x}{1:02x}{2:04x}", Op(code), Byte(), Word())
def binary_sp_word(code):
    """2 operand instruction closure"""
    return signature("{0:02x}00{2:04x}", Op(code), Sp(), Word())
def trinary_reg_reg_reg(code):
    """3 operand instruction closure"""
    return signature("{0:02x}{2:01x}{1:01x}0{3:01x}00", Op(code), Reg(), Reg(),
            Reg())
def trinary_reg_reg_word(code):
    """3 operand instruction closure"""
    return signature("{0:02x}{2:01x}{1:01x}{3:0x}", Op(code), Reg(), Reg(),
            Word())
def flip(tokens):
    """Specialised flip instruction formatter"""
    if (0 <= int(tokens[1]) <= 1) and (0 <= int(tokens[2]) <= 1):
        val = (int(tokens[1]) << 1) | int(tokens[2])
        return "0800000{0:01d}".format(val)
    else:
        raise ValueError("Invalid operands: %s"%(" ".join(tokens)))
INSTRUCTIONS = {
## 0x - Misc/Video/Audio
        'NOP': [nullary(0x00)],
        'CLS': [nullary(0x01)],
        'VBLNK': [nullary(0x02)],
        'BGC' : [nibble(0x03)],
        'SPR': [unary_word(0x04)],
        'DRW': [trinary_reg_reg_reg(0x06), trinary_reg_reg_word(0x05)],
        'RND': [binary_reg_word(0x07)],
        'FLIP': [flip],
        'SND0': [nullary(0x09)],
        'SND1': [unary_word(0x0A)],
        'SND2': [unary_word(0x0B)],
        'SND3': [unary_word(0x0C)],
        'SNP': [binary_reg_word(0x0D)],
        'SNG': [binary_reg_word(0x0D), byte_word(0x0E)],
## 1x - Jumps (Branches)
        'JMP': [unary_word(0x10), unary_reg(0x16)],
        'JME': [trinary_reg_reg_word(0x13)],
        'CALL': [unary_word(0x14), unary_reg(0x18)],
        'RET': [nullary(0x15)],
## 2x - Loads
        'LDI': [binary_reg_word(0x20), binary_sp_word(0x21)],
        'LDM': [binary_reg_word(0x22), binary_reg_reg(0x23)],
        'MOV': [binary_reg_reg(0x24)],
## 3x - Stores
        'STM': [binary_reg_word(0x30), binary_reg_reg(0x31)],
## 4x - Addition
        'ADDI': [binary_reg_word(0x40)],
        'ADD': [binary_reg_reg(0x41), trinary_reg_reg_reg(0x42)],
## 5x - Subtraction
        'SUBI': [binary_reg_word(0x50)],
        'SUB': [binary_reg_reg(0x51), trinary_reg_reg_reg(0x52)],
        'CMPI': [binary_reg_word(0x53)],
        'CMP': [binary_reg_reg(0x54)],
## 6x - Bitwise AND (&)
        'ANDI': [binary_reg_word(0x60)],
        'AND': [binary_reg_reg(0x61), trinary_reg_reg_reg(0x62)],
        'TSTI': [binary_reg_word(0x63)],
        'TST': [binary_reg_reg(0x64)],
## 7x - Bitwise OR (|)
        'ORI': [binary_reg_word(0x70)],
        'OR': [binary_reg_reg(0x71), trinary_reg_reg_reg(0x72)],
## 8x - Bitwise XOR (^)
        'XORI': [binary_reg_word(0x80)],
        'XOR': [binary_reg_reg(0x81), trinary_reg_reg_reg(0x82)],
## 9x - Multiplication
        'MULI': [binary_reg_word(0x90)],
        'MUL': [binary_reg_reg(0x91), trinary_reg_reg_reg(0x92)],
## Ax - Division
        'DIVI': [binary_reg_word(0xA0)],
        'DIV': [binary_reg_reg(0xA1), trinary_reg_reg_reg(0xA2)],
        'MODI': [binary_reg_word(0xA3)],
        'MOD': [binary_reg_reg(0xA4), trinary_reg_reg_reg(0xA5)],
        'REMI': [binary_reg_word(0xA6)],
        'REM': [binary_reg_reg(0xA7), trinary_reg_reg_reg(0xA8)],
## Bx - Logical/Arithmetic Shifts
        'SHL': [binary_reg_nibble(0xB0), binary_reg_reg(0xB2)],
        'SHR': [binary_reg_nibble(0xB1), binary_reg_reg(0xB3)],
        'SAL': [binary_reg_nibble(0xB0), binary_reg_reg(0xB4)],
        'SAR': [binary_reg_nibble(0xB1), binary_reg_reg(0xB5)],
## Cx - Push/Pop
        'PUSH': [unary_reg(0xC0)],
        'POP': [unary_reg(0xC1)],
        'PUSHALL': [nullary(0xC2)],
        'POPALL': [nullary(0xC3)],
        'PUSHF': [nullary(0xC4)],
        'POPF': [nullary(0xC5)],
## Dx - Palette
        'PAL': [unary_word(0xD0), unary_reg(0xD1)],
## Ex - Not/Neg
        'NOTI': [binary_reg_word(0xE0)],
        'NOT': [unary_reg(0xE1), binary_reg_reg(0xE2)],
        'NEGI': [binary_reg_word(0xE3)],
        'NEG': [unary_reg(0xE4), binary_reg_reg(0xE5)],
}
