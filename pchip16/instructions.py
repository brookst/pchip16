"""
chip16 instruction format strings
"""
#pylint: disable=W0142

class SignatureMismatch(Exception):
    """Tokens do not match operator signature"""
    pass

def signature(tokens, *args):
    """Check tokens match expectation"""
    if len(tokens) != len(args):
        return False
    return all([arg(tokens[i]) for i, arg in enumerate(args)])

def get_op(tokens, op_code):
    """Coerce first token into op_code"""
    tokens[0] = op_code

def is_reg(token):
    """Expectation of register"""
    return len(token) == 2 and token[0] == 'R'

def get_reg(tokens, index):
    """Coerce token at index into register"""
    tokens[index] = int(tokens[index][1], 16)

def is_sp(token):
    """Expectation of stack pointer"""
    return token == 'SP'

def is_word(token):
    """Expectation of word"""
    return len(token) >= 3 and len(token) <= 6 and token[:2] == '0X'

def get_word(tokens, index):
    """Coerce token at index into word"""
    val = int(tokens[index][2:], 16)
    lla = val & 0xFF
    hha = val >> 8
    tokens[index] = (lla << 8) | hha

def is_byte(token):
    """Expectation of byte"""
    return token[:2] == '0X' and len(token) <= 4

def get_byte(tokens, index):
    """Coerce token at index into byte"""
    tokens[index] = int(tokens[index][2:], 16)

def is_nibble(token):
    """Expectation of nibble"""
    return len(token) == 3 and token[:2] == '0X'

def get_nibble(tokens, index):
    """Coerce token at index into nibble"""
    tokens[index] = int(tokens[index][2:], 16)
#get_nibble = get_byte

def is_bit(token):
    """Expectation of bit"""
    return token == "0" or token == "1"

def is_this(op_code):
    """Get an expectation of this op_code being correct"""
    return lambda x: x == op_code

def nullary(op_code):
    """0 operand instruction closure"""
    def ret(tokens):
        """Encode closed operation"""
        get_op(tokens, op_code)
        if signature(tokens, is_this(op_code)):
            return "{0:02x}000000".format(*tokens)
    return ret
def unary_reg(op_code):
    """1 operand instruction closure"""
    def ret(tokens):
        """Encode closed operation"""
        get_op(tokens, op_code)
        if signature(tokens, is_this(op_code), is_reg):
            get_reg(tokens, 1)
            return "{0:02x}0{1:01x}0000".format(*tokens)
        else:
            raise SignatureMismatch()
    return ret
def unary_nibble(op_code):
    """1 operand instruction closure"""
    def ret(tokens):
        """Encode closed operation"""
        get_op(tokens, op_code)
        if signature(tokens, is_this(op_code), is_nibble):
            get_nibble(tokens, 1)
            return "{0:02x}000{1:01x}00".format(*tokens)
        else:
            raise SignatureMismatch()
    return ret
def unary_word(op_code):
    """1 operand instruction closure"""
    def ret(tokens):
        """Encode closed operation"""
        get_op(tokens, op_code)
        if signature(tokens, is_this(op_code), is_word):
            get_word(tokens, 1)
            return "{0:02x}00{1:04x}".format(*tokens)
        else:
            raise SignatureMismatch()
    return ret
def binary_reg_reg(op_code):
    """2 operand instruction closure"""
    def ret(tokens):
        """Encode closed operation"""
        get_op(tokens, op_code)
        if signature(tokens, is_this(op_code), is_reg, is_reg):
            get_reg(tokens, 1)
            get_reg(tokens, 2)
            return "{0:02x}{2:01x}{1:01x}0000".format(*tokens)
        else:
            raise SignatureMismatch()
    return ret
def binary_reg_word(op_code):
    """2 operand instruction closure"""
    def ret(tokens):
        """Encode closed operation"""
        get_op(tokens, op_code)
        if signature(tokens, is_this(op_code), is_reg, is_word):
            get_reg(tokens, 1)
            get_word(tokens, 2)
            return "{0:02x}0{1:01x}{2:04x}".format(*tokens)
        else:
            raise SignatureMismatch()
    return ret
def binary_byte_word(op_code):
    """2 operand instruction closure"""
    def ret(tokens):
        """Encode closed operation"""
        get_op(tokens, op_code)
        if signature(tokens, is_this(op_code), is_byte, is_word):
            get_byte(tokens, 1)
            get_word(tokens, 2)
            return "{0:02x}{1:02x}{2:04x}".format(*tokens)
        else:
            raise SignatureMismatch()
    return ret
def binary_sp_word(op_code):
    """2 operand instruction closure"""
    def ret(tokens):
        """Encode closed operation"""
        get_op(tokens, op_code)
        if signature(tokens, is_this(op_code), is_sp, is_word):
            get_word(tokens, 2)
            return "{0:02x}00{2:04x}".format(*tokens)
        else:
            raise SignatureMismatch()
    return ret
def binary_bit_bit(op_code):
    """2 operand instruction closure"""
    def ret(tokens):
        """Encode closed operation"""
        get_op(tokens, op_code)
        if signature(tokens, is_this(op_code), is_bit, is_bit):
            tokens[1] = (int(tokens[1]) << 1) | int(tokens[2])
            return "{0:02x}00000{1:01d}".format(*tokens)
        else:
            raise SignatureMismatch()
    return ret
def trinary_reg_reg_reg(op_code):
    """3 operand instruction closure"""
    def ret(tokens):
        """Encode closed operation"""
        get_op(tokens, op_code)
        if signature(tokens, is_this(op_code), is_reg, is_reg, is_reg):
            get_reg(tokens, 1)
            get_reg(tokens, 2)
            get_reg(tokens, 3)
            return "{0:02x}{2:01x}{1:01x}0{3:01x}00".format(*tokens)
        else:
            raise SignatureMismatch()
    return ret
def trinary_reg_reg_word(op_code):
    """3 operand instruction closure"""
    def ret(tokens):
        """Encode closed operation"""
        get_op(tokens, op_code)
        if signature(tokens, is_this(op_code), is_reg, is_reg, is_word):
            get_reg(tokens, 1)
            get_reg(tokens, 2)
            get_word(tokens, 3)
            return "{0:02x}{2:01x}{1:01x}{3:04x}".format(*tokens)
        else:
            raise SignatureMismatch()
    return ret


INSTRUCTIONS = {
## 0x - Misc/Video/Audio
        'NOP': [nullary(0x00)],
        'CLS': [nullary(0x01)],
        'VBLNK': [nullary(0x02)],
        'BGC' : [unary_nibble(0x03)],
        'SPR': [unary_word(0x04)],
        'DRW': [trinary_reg_reg_reg(0x06), trinary_reg_reg_word(0x05)],
        'RND': [binary_reg_word(0x07)],
        'FLIP': [binary_bit_bit(0x08)],
        'SND0': [nullary(0x09)],
        'SND1': [unary_word(0x0a)],
        'SND2': [unary_word(0x0b)],
        'SND3': [unary_word(0x0c)],
        'SNP': [binary_reg_word(0x0D)],
        'SNG': [binary_byte_word(0x0E)],
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
#TODO:
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
    }
