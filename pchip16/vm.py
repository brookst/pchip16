"""
pchip16 VM class
"""

CARRY = 0x1 << 1
ZERO = 0x1 << 2
OVERFLOW = 0x1 << 6
NEGATIVE = 0x1 << 7

from .memory import Memory, Register
from .utils import is_neg, complement, to_dec, to_hex

def mask_code(op_code, mask):
    """Raise error for op_codes in mask"""
    if op_code & mask:
        raise ValueError("Invalid op code %s" %hex(op_code) )

class VM(object):
    """Object representing a single virtual machine instance"""
    program_counter = 0
    stack_pointer = 0xFDF0
    flags = 0
    mem = Memory()
    register = Register()

    def __init__(self):
        for reg in range(0xf):
            self.register[reg] = 0

    def step(self):
        """Execute instruction at self.program_counter and increment"""
        self.program_counter += 1

    def execute(self, op_code):
        """Carry out instruction specified by op_code"""
        instructions = [
            self.nop,
            self.jump,
            self.load, 
            self.store,
            self.add,
            self.sub,
            self.bit_and,
            self.bit_or,
            self.bit_xor,
            self.mul,
            self.div,
            self.shift,
            self.stack,
        ]
        try:
            instruction = instructions[op_code >> 28]
            instruction(op_code)
        except IndexError:
            raise ValueError("Invalid opcode %i" %(op_code >> 28))

    def nop(self, op_code):
        """Do nothig"""
        pass

    def jump(self, op_code):
        """Jumps"""
        if op_code >> 16 == 0x1000:
            #"""JMP HHLL"""
            hh_addr = op_code - (op_code >> 8 << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            self.program_counter = (hh_addr << 8) + ll_addr
        elif op_code >> 24 == 0x13:
            #"""JME RX, RY, HHLL"""
            y_reg = (op_code >> 20) - 0x130
            x_reg = ((op_code >> 16) - (y_reg << 4) - 0x1300)
            hh_addr = op_code - (op_code >> 8 << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            if self.register[x_reg] == self.register[y_reg]:
                self.program_counter = (hh_addr << 8) + ll_addr
        elif op_code >> 16 == 0x1400:
            #"""CALL HHLL"""
            hh_addr = op_code - (op_code >> 8 << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr
            self.mem[self.stack_pointer] = self.program_counter
            self.stack_pointer += 2
            self.program_counter = self.mem[addr]
        elif op_code == 0x15000000:
            #"""RET"""
            self.stack_pointer -= 2
            self.program_counter = self.mem[self.stack_pointer]
        elif op_code >> 20 == 0x160:
            #"""JMP_RX"""
            mask_code(op_code, 0xFFFF)
            x_reg = (op_code >> 16) & 0xF

            self.program_counter = self.register[x_reg]
        elif op_code >> 20 == 0x180:
            #"""CALL RX"""
            mask_code(op_code, 0xFFFF)
            x_reg = (op_code >> 16) & 0xF

            self.mem[self.stack_pointer] = self.program_counter
            self.stack_pointer += 2
            self.program_counter = self.register[x_reg]
        else:
            raise ValueError("Invalid op code")

    def load(self, op_code):
        """Loads"""
        if op_code >> 20 == 0x200:
            #"""LDI RX, HHLL"""
            x_reg = (op_code >> 16) - 0x2000
            hh_addr = op_code - (op_code >> 8 << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr
            self.register[x_reg] = self.mem[addr]
        elif op_code >> 16 == 0x2100:
            #"""LDI SP, HHLL"""
            hh_addr = op_code - (op_code >> 8 << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr
            self.stack_pointer = self.mem[addr]
        elif op_code >> 20 == 0x220:
            #"""LDM RX, HHLL"""
            x_reg = (op_code >> 16) - 0x2200
            hh_addr = op_code - (op_code >> 8 << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr
            self.register[x_reg] = self.mem[self.mem[addr]]
        elif op_code >> 24 == 0x23:
            #"""LDM RX, RY"""
            if op_code - ((op_code >> 16) << 16):
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x230
            x_reg = (op_code >> 16) - 0x2300 - (y_reg << 4)

            addr = self.register[y_reg]
            self.register[x_reg] = self.mem[addr]
        elif op_code >> 24 == 0x24:
            #"""MOV RX, RY"""
            if op_code - ((op_code >> 16) << 16):
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x240
            x_reg = (op_code >> 16) - 0x2400 - (y_reg << 4)

            self.register[x_reg] = self.register[y_reg]
        else:
            raise ValueError("Invalid op code")

    def store(self, op_code):
        """Stores"""
        if op_code >> 20 == 0x300:
            #"""STM RX, HHLL"""
            x_reg = (op_code >> 16) - 0x3000
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr
            self.mem[addr] = self.register[x_reg]
        elif op_code >> 24 == 0x31:
            #"""STM RX, HHLL"""
            if op_code - ((op_code >> 16) << 16):
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x310
            x_reg = (op_code >> 16) - (y_reg << 4) - 0x3100

            addr = self.register[y_reg]
            self.mem[addr] = self.register[x_reg]
        else:
            raise ValueError("Invalid op code")

    def _add(self, left, right):
        """16 bit signed addition operation"""
        value = left + right
        if value >= 0x10000:
            # Remove bit 16
            value -= 0x10000
            # Set the CARRY flag as bit 16 is set
            self.flags |= CARRY
        else:
            # Clear CARRY bit
            self.flags &= ~CARRY

        # Set OVERFLOW flag if signs mismatch
        if is_neg(left) and is_neg(right) and not is_neg(value):
            self.flags |= OVERFLOW
        elif not is_neg(left) and not is_neg(right) and is_neg(value):
            self.flags |= OVERFLOW
        else:
            # Clear OVERFLOW bit
            self.flags &= ~OVERFLOW
        return self.flag_set(value)
            
    def flag_set(self, value):
        """Set ZERO and NEGATIVE flags for value"""
        # Set/clear ZERO flag if value is zero/non-zero
        if value == 0x0:
            self.flags |= ZERO
        else:
            self.flags &= ~ZERO
        # Set/clear NEGATIVE flag if value is negative/non-negative
        if is_neg(value):
            self.flags |= NEGATIVE
        else:
            self.flags &= ~NEGATIVE
        return value

    def _sub(self, left, right):
        """16 bit signed subtraction operation"""
        right = complement(right)
        value = self._add(left, right)
        if right == 0x8000:
            self.flags ^= OVERFLOW
        self.flags ^= CARRY
        return value

    def _and(self, left, right):
        """Bitwise and operation"""
        value = left & right
        return self.flag_set(value)

    def _or(self, left, right):
        """Bitwise or operation"""
        value = left | right
        return self.flag_set(value)

    def _xor(self, left, right):
        """Bitwise xor operation"""
        value = left ^ right
        return self.flag_set(value)

    def _mul(self, left, right):
        """16 bit signed multiplication"""
        if is_neg(right):
            left = complement(left)
            right = complement(right)
        value = left * right
        if value >= 0x10000:
            # Remove bit 16
            value &= 0xFFFF
            # Set the CARRY flag as bit 16 is set
            self.flags |= CARRY
        else:
            # Clear CARRY bit
            self.flags &= ~CARRY
        return self.flag_set(value)

    def _div(self, left, right):
        """Division"""
        left = to_dec(left)
        right = to_dec(right)
        value = left // right
        value = to_hex(value)
        if left % right:
            self.flags |= CARRY
        else:
            self.flags &= ~CARRY
        return self.flag_set(value)

    def add(self, op_code):
        """Addition"""
        if op_code >> 20 == 0x400:
            #"""ADDI RX, HHLL"""
            mask_code(op_code, 0xF00000)
            x_reg = (op_code >> 16) - 0x4000
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            value = self._add(self.register[x_reg], self.mem[addr])
            self.register[x_reg] = value
        elif op_code >> 24 == 0x41:
            #"""ADD RX, RY"""
            mask_code(op_code, 0xFFFF)
            y_reg = (op_code >> 20) - 0x410
            x_reg = (op_code >> 16) - 0x4100 - (y_reg << 4)

            value = self._add(self.register[x_reg], self.register[y_reg])
            self.register[x_reg] = value
        elif op_code >> 24 == 0x42:
            #"""ADD RX, RY, RZ"""
            mask_code(op_code, 0xF0FF)
            y_reg = (op_code >> 20) - 0x420
            x_reg = (op_code >> 16) - 0x4200 - (y_reg << 4)
            z_reg = (op_code >> 8) - ((op_code >> 12) << 4)

            self.register[z_reg] = self._add(self.register[x_reg],
                    self.register[y_reg])
        else:
            raise ValueError("Invalid op code")

    def sub(self, op_code):
        """Subtraction"""
        if op_code >> 20 == 0x500:
            #"""SUBI RX, HHLL"""
            mask_code(op_code, 0xF00000)
            x_reg = (op_code >> 16) - 0x5000
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            value = self._sub(self.register[x_reg], self.mem[addr])
            self.register[x_reg] = value
        elif op_code >> 24 == 0x51:
            #"""SUB RX, RY"""
            mask_code(op_code, 0xFFFF)
            y_reg = (op_code >> 20) - 0x510
            x_reg = (op_code >> 16) - 0x5100 - (y_reg << 4)

            self.register[x_reg] = self._sub(self.register[x_reg],
                    self.register[y_reg])
        elif op_code >> 24 == 0x52:
            #"""SUB RX, RY, RZ"""
            mask_code(op_code, 0xF0FF)
            y_reg = (op_code >> 20) - 0x520
            x_reg = (op_code >> 16) - 0x5200 - (y_reg << 4)
            z_reg = (op_code >> 8) - ((op_code >> 12) << 4)

            self.register[z_reg] = self._sub(self.register[x_reg],
                    self.register[y_reg])
        elif op_code >> 20 == 0x530:
            #"""CMPI RX, HHLL"""
            mask_code(op_code, 0xF00000)
            x_reg = (op_code >> 16) - 0x5300
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            self._sub(self.register[x_reg], self.mem[addr])
        elif op_code >> 24 == 0x54:
            #"""CMP RX, RY"""
            mask_code(op_code, 0xFFFF)
            y_reg = (op_code >> 20) - 0x540
            x_reg = (op_code >> 16) - 0x5400 - (y_reg << 4)

            self._sub(self.register[x_reg], self.register[y_reg])
        else:
            raise ValueError("Invalid op code")

    def bit_and(self, op_code):
        """Bitwise and"""
        if op_code >> 20 == 0x600:
            #"""ANDI RX, HHLL"""
            mask_code(op_code, 0xF00000)
            x_reg = (op_code >> 16) - 0x6000
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            value = self._and(self.register[x_reg], self.mem[addr])
            self.register[x_reg] = value
        elif op_code >> 24 == 0x61:
            #"""AND RX, RY"""
            mask_code(op_code, 0xFFFF)
            y_reg = (op_code >> 20) - 0x610
            x_reg = (op_code >> 16) - 0x6100 - (y_reg << 4)

            self.register[x_reg] = self._and(self.register[x_reg],
                    self.register[y_reg])
        elif op_code >> 24 == 0x62:
            #"""AND RX, RY, RZ"""
            mask_code(op_code, 0xF0FF)
            y_reg = (op_code >> 20) - 0x620
            x_reg = (op_code >> 16) - 0x6200 - (y_reg << 4)
            z_reg = (op_code >> 8) - ((op_code >> 12) << 4)

            self.register[z_reg] = self._and(self.register[x_reg],
                    self.register[y_reg])
        elif op_code >> 20 == 0x630:
            #"""TSTI RX, HHLL"""
            mask_code(op_code, 0xF00000)
            x_reg = (op_code >> 16) - 0x6300
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            self._and(self.register[x_reg], self.mem[addr])
        elif op_code >> 24 == 0x64:
            #"""TST RX, RY"""
            mask_code(op_code, 0xFFFF)
            y_reg = (op_code >> 20) - 0x640
            x_reg = (op_code >> 16) - 0x6400 - (y_reg << 4)

            self._and(self.register[x_reg], self.register[y_reg])
        else:
            raise ValueError("Invalid op code")

    def bit_or(self, op_code):
        """Bitwise or"""
        if op_code >> 20 == 0x700:
            #"""ORI RX, HHLL"""
            mask_code(op_code, 0xF00000)
            x_reg = (op_code >> 16) - 0x7000
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            value = self._or(self.register[x_reg], self.mem[addr])
            self.register[x_reg] = value
        elif op_code >> 24 == 0x71:
            #"""OR RX, RY"""
            mask_code(op_code, 0xFFFF)
            y_reg = (op_code >> 20) - 0x710
            x_reg = (op_code >> 16) - 0x7100 - (y_reg << 4)

            self.register[x_reg] = self._or(self.register[x_reg],
                    self.register[y_reg])
        elif op_code >> 24 == 0x72:
            #"""OR RX, RY, RZ"""
            mask_code(op_code, 0xF0FF)
            y_reg = (op_code >> 20) - 0x720
            x_reg = (op_code >> 16) - 0x7200 - (y_reg << 4)
            z_reg = (op_code >> 8) - ((op_code >> 12) << 4)

            self.register[z_reg] = self._or(self.register[x_reg],
                    self.register[y_reg])
        else:
            raise ValueError("Invalid op code")

    def bit_xor(self, op_code):
        """Bitwise xor"""
        if op_code >> 20 == 0x800:
            #"""XORI RX, HHLL"""
            mask_code(op_code, 0xF00000)
            x_reg = (op_code >> 16) - 0x8000
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            value = self._xor(self.register[x_reg], self.mem[addr])
            self.register[x_reg] = value
        elif op_code >> 24 == 0x81:
            #"""XOR RX, RY"""
            mask_code(op_code, 0xFFFF)
            y_reg = (op_code >> 20) - 0x810
            x_reg = (op_code >> 16) - 0x8100 - (y_reg << 4)

            self.register[x_reg] = self._xor(self.register[x_reg],
                    self.register[y_reg])
        elif op_code >> 24 == 0x82:
            #"""XOR RX, RY, RZ"""
            mask_code(op_code, 0xF0FF)
            y_reg = (op_code >> 20) - 0x820
            x_reg = (op_code >> 16) - 0x8200 - (y_reg << 4)
            z_reg = (op_code >> 8) - ((op_code >> 12) << 4)

            self.register[z_reg] = self._xor(self.register[x_reg],
                    self.register[y_reg])
        else:
            raise ValueError("Invalid op code")

    def mul(self, op_code):
        """Multiplication"""
        if op_code >> 20 == 0x900:
            #"""MULI RX, HHLL"""
            mask_code(op_code, 0xF00000)
            x_reg = (op_code >> 16) - 0x9000
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            value = self._mul(self.register[x_reg], self.mem[addr])
            self.register[x_reg] = value
        elif op_code >> 24 == 0x91:
            #"""MUL RX, RY"""
            mask_code(op_code, 0xFFFF)
            y_reg = (op_code >> 20) - 0x910
            x_reg = (op_code >> 16) - 0x9100 - (y_reg << 4)

            self.register[x_reg] = self._mul(self.register[x_reg],
                    self.register[y_reg])
        elif op_code >> 24 == 0x92:
            #"""MUL RX, RY, RZ"""
            mask_code(op_code, 0xF0FF)
            y_reg = (op_code >> 20) - 0x920
            x_reg = (op_code >> 16) - 0x9200 - (y_reg << 4)
            z_reg = (op_code >> 8) - ((op_code >> 12) << 4)

            self.register[z_reg] = self._mul(self.register[x_reg],
                    self.register[y_reg])
        else:
            raise ValueError("Invalid op code")

    def div(self, op_code):
        """Division"""
        if op_code >> 20 == 0xA00:
            #"""DIVI RX, HHLL"""
            mask_code(op_code, 0xF00000)
            x_reg = (op_code >> 16) - 0xA000
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            value = self._div(self.register[x_reg], self.mem[addr])
            self.register[x_reg] = value
        elif op_code >> 24 == 0xA1:
            #"""DIV RX, RY"""
            mask_code(op_code, 0xFFFF)
            y_reg = (op_code >> 20) - 0xA10
            x_reg = (op_code >> 16) - 0xA100 - (y_reg << 4)

            self.register[x_reg] = self._div(self.register[x_reg],
                    self.register[y_reg])
        elif op_code >> 24 == 0xA2:
            #"""DIV RX, RY, RZ"""
            mask_code(op_code, 0xF0FF)
            y_reg = (op_code >> 20) - 0xA20
            x_reg = (op_code >> 16) - 0xA200 - (y_reg << 4)
            z_reg = (op_code >> 8) - ((op_code >> 12) << 4)

            self.register[z_reg] = self._div(self.register[x_reg],
                    self.register[y_reg])
        else:
            raise ValueError("Invalid op code")

    def shift(self, op_code):
        """Bitwise/Arithmetic shifts"""
        if op_code >> 20 == 0xB00:
            #"""SHL RX, N"""
            mask_code(op_code, 0xF0FF)
            x_reg = (op_code & 0xF0000) >> 16
            n_bits = (op_code & 0xF00) >> 8

            value = self.register[x_reg] << n_bits

            self.register[x_reg] = self.flag_set(value & 0xFFFF)
        elif op_code >> 20 == 0xB10:
            #"""SHR RX, N"""
            mask_code(op_code, 0xF0FF)
            x_reg = (op_code & 0xF0000) >> 16
            n_bits = (op_code & 0xF00) >> 8

            value = self.register[x_reg] >> n_bits

            self.register[x_reg] = self.flag_set(value & 0xFFFF)
        elif op_code >> 20 == 0xB20:
            #"""SAR RX, N"""
            mask_code(op_code, 0xF0FF)
            x_reg = (op_code & 0xF0000) >> 16
            n_bits = (op_code & 0xF00) >> 8
            lead_bit = self.register[x_reg] & 0x8000

            value = (self.register[x_reg] >> n_bits) | lead_bit

            self.register[x_reg] = self.flag_set(value & 0xFFFF)
        elif op_code >> 24 == 0xB3:
            #"""SHL RX, RY"""
            mask_code(op_code, 0xFFFF)
            x_reg = (op_code & 0xF0000) >> 16
            y_reg = (op_code & 0xF00000) >> 20

            value = self.register[x_reg] << self.register[y_reg]

            self.register[x_reg] = self.flag_set(value & 0xFFFF)
        elif op_code >> 24 == 0xB4:
            #"""SHR RX, RY"""
            mask_code(op_code, 0xFFFF)
            x_reg = (op_code & 0xF0000) >> 16
            y_reg = (op_code & 0xF00000) >> 20

            value = self.register[x_reg] >> self.register[y_reg]

            self.register[x_reg] = self.flag_set(value & 0xFFFF)
        elif op_code >> 24 == 0xB5:
            #"""SAR RX, RY"""
            mask_code(op_code, 0xFFFF)
            x_reg = (op_code & 0xF0000) >> 16
            y_reg = (op_code & 0xF00000) >> 20
            lead_bit = self.register[x_reg] & 0x8000

            value = self.register[x_reg] >> self.register[y_reg] | lead_bit

            self.register[x_reg] = self.flag_set(value & 0xFFFF)
        else:
            raise ValueError("Invalid opcode")

    def stack(self, op_code):
        """Stack push/pop instructions"""
        if op_code >> 20 == 0xC00:
            #"""PUSH RX"""
            mask_code(op_code, 0xFFFF)
            x_reg = (op_code & 0xF0000) >> 16

            self.mem[self.stack_pointer] = self.register[x_reg]
            self.stack_pointer += 2
        elif op_code >> 20 == 0xC10:
            #"""POP RX"""
            mask_code(op_code, 0xFFFF)
            x_reg = (op_code & 0xF0000) >> 16

            self.register[x_reg] = self.mem[self.stack_pointer]
            self.stack_pointer -= 2
        elif op_code >> 24 == 0xC2:
            #"""PUSHALL"""
            mask_code(op_code, 0xFFFFFF)

            for i, register in enumerate(self.register):
                self.mem[self.stack_pointer + 2 * i] = register

            self.stack_pointer += 32
        elif op_code >> 24 == 0xC3:
            #"""POPALL"""
            mask_code(op_code, 0xFFFFFF)

            self.stack_pointer -= 32
            for i in range(16):
                self.register[i] = self.mem[self.stack_pointer + 2 * i]
        elif op_code >> 20 == 0xC40:
            #"""PUSHF"""
            mask_code(op_code, 0xFFFFFF)

            self.mem[self.stack_pointer] = self.flags
            self.stack_pointer += 2
        elif op_code >> 20 == 0xC50:
            #"""POPF"""
            mask_code(op_code, 0xFFFFFF)

            self.stack_pointer -= 2
            self.flags = self.mem[self.stack_pointer]
        else:
            raise ValueError("Invalid opcode")
