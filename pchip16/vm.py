"""
pchip16 VM class
"""

CARRY = 0x1 << 1
ZERO = 0x1 << 2
OVERFLOW = 0x1 << 6
NEGATIVE = 0x1 << 7

from array import array
from .utils import is_neg, complement

class VM(object):
    """Object representing a single virtual machine instance"""
    program_counter = 0
    stack_pointer = 0
    flags = 0
    mem = array('H', (0 for i in range(2**16) ) )
    register = array('H', (0 for i in range(16) ) )

    def __init__(self):
        for reg in range(0xf):
            self.register[reg] = 0

    def step(self):
        """Execute instruction at self.program_counter and increment"""
        self.program_counter += 1

    def execute(self, op_code):
        """Carry out instruction specified by op_code"""
        if op_code >> 28 == 0x1:
            self.jump(op_code)

        elif op_code >> 28 == 0x2:
            self.load(op_code)

        elif op_code >> 28 == 0x3:
            self.store(op_code)

        elif op_code >> 28 == 0x4:
            self.add(op_code)

        elif op_code >> 28 == 0x5:
            self.sub(op_code)

        elif op_code >> 28 == 0x6:
            self.bit_and(op_code)

        elif op_code >> 28 == 0x7:
            self.bit_or(op_code)

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

    def add_op(self, left, right):
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

    def sub_op(self, left, right):
        """16 bit signed subtraction operation"""
        right = complement(right)
        value = self.add_op(left, right)
        if right == 0x8000:
            self.flags ^= OVERFLOW
        self.flags ^= CARRY
        return value

    def and_op(self, left, right):
        """Bitwise and operation"""
        value = left & right
        return self.flag_set(value)

    def or_op(self, left, right):
        """Bitwise or operation"""
        value = left | right
        return self.flag_set(value)

    def xor_op(self, left, right):
        """Bitwise xor operation"""
        value = left ^ right
        return self.flag_set(value)

    def add(self, op_code):
        """Addition"""
        if op_code >> 20 == 0x400:
            #"""ADDI RX, HHLL"""
            if op_code & 0xF00000:
                raise ValueError("Invalid op code")
            x_reg = (op_code >> 16) - 0x4000
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            value = self.add_op(self.register[x_reg], self.mem[addr])
            self.register[x_reg] = value
        elif op_code >> 24 == 0x41:
            #"""ADD RX, RY"""
            if op_code - ((op_code >> 16) << 16):
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x410
            x_reg = (op_code >> 16) - 0x4100 - (y_reg << 4)

            value = self.add_op(self.register[x_reg], self.register[y_reg])
            self.register[x_reg] = value
        elif op_code >> 24 == 0x42:
            #"""ADD RX, RY, RZ"""
            if op_code & 0xF0FF:
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x420
            x_reg = (op_code >> 16) - 0x4200 - (y_reg << 4)
            z_reg = (op_code >> 8) - ((op_code >> 12) << 4)

            self.register[z_reg] = self.add_op(self.register[x_reg],
                    self.register[y_reg])
        else:
            raise ValueError("Invalid op code")

    def sub(self, op_code):
        """Subtraction"""
        if op_code >> 20 == 0x500:
            #"""SUBI RX, HHLL"""
            if op_code & 0xF00000:
                raise ValueError("Invalid op code")
            x_reg = (op_code >> 16) - 0x5000
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            value = self.sub_op(self.register[x_reg], self.mem[addr])
            self.register[x_reg] = value
        elif op_code >> 24 == 0x51:
            #"""SUB RX, RY"""
            if op_code - ((op_code >> 16) << 16):
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x510
            x_reg = (op_code >> 16) - 0x5100 - (y_reg << 4)

            self.register[x_reg] = self.sub_op(self.register[x_reg],
                    self.register[y_reg])
        elif op_code >> 24 == 0x52:
            #"""SUB RX, RY, RZ"""
            if op_code & 0xF0FF:
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x520
            x_reg = (op_code >> 16) - 0x5200 - (y_reg << 4)
            z_reg = (op_code >> 8) - ((op_code >> 12) << 4)

            self.register[z_reg] = self.sub_op(self.register[x_reg],
                    self.register[y_reg])
        elif op_code >> 20 == 0x530:
            #"""CMPI RX, HHLL"""
            if op_code & 0xF00000:
                raise ValueError("Invalid op code")
            x_reg = (op_code >> 16) - 0x5300
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            self.sub_op(self.register[x_reg], self.mem[addr])
        elif op_code >> 24 == 0x54:
            #"""CMP RX, RY"""
            if op_code - ((op_code >> 16) << 16):
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x540
            x_reg = (op_code >> 16) - 0x5400 - (y_reg << 4)

            self.sub_op(self.register[x_reg], self.register[y_reg])
        else:
            raise ValueError("Invalid op code")

    def bit_and(self, op_code):
        """Bitwise and"""
        if op_code >> 20 == 0x600:
            #"""ANDI RX, HHLL"""
            if op_code & 0xF00000:
                raise ValueError("Invalid op code")
            x_reg = (op_code >> 16) - 0x6000
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            value = self.and_op(self.register[x_reg], self.mem[addr])
            self.register[x_reg] = value
        elif op_code >> 24 == 0x61:
            #"""AND RX, RY"""
            if op_code - ((op_code >> 16) << 16):
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x610
            x_reg = (op_code >> 16) - 0x6100 - (y_reg << 4)

            self.register[x_reg] = self.and_op(self.register[x_reg],
                    self.register[y_reg])
        elif op_code >> 24 == 0x62:
            #"""AND RX, RY, RZ"""
            if op_code & 0xF0FF:
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x620
            x_reg = (op_code >> 16) - 0x6200 - (y_reg << 4)
            z_reg = (op_code >> 8) - ((op_code >> 12) << 4)

            self.register[z_reg] = self.and_op(self.register[x_reg],
                    self.register[y_reg])
        elif op_code >> 20 == 0x630:
            #"""TSTI RX, HHLL"""
            if op_code & 0xF00000:
                raise ValueError("Invalid op code")
            x_reg = (op_code >> 16) - 0x6300
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            self.and_op(self.register[x_reg], self.mem[addr])
        elif op_code >> 24 == 0x64:
            #"""TST RX, RY"""
            if op_code - ((op_code >> 16) << 16):
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x640
            x_reg = (op_code >> 16) - 0x6400 - (y_reg << 4)

            self.and_op(self.register[x_reg], self.register[y_reg])
        else:
            raise ValueError("Invalid op code")

    def bit_or(self, op_code):
        """Bitwise or"""
        if op_code >> 20 == 0x700:
            #"""ORI RX, HHLL"""
            if op_code & 0xF00000:
                raise ValueError("Invalid op code")
            x_reg = (op_code >> 16) - 0x7000
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr

            value = self.or_op(self.register[x_reg], self.mem[addr])
            self.register[x_reg] = value
        elif op_code >> 24 == 0x71:
            #"""OR RX, RY"""
            if op_code - ((op_code >> 16) << 16):
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x710
            x_reg = (op_code >> 16) - 0x7100 - (y_reg << 4)

            self.register[x_reg] = self.or_op(self.register[x_reg],
                    self.register[y_reg])
        elif op_code >> 24 == 0x72:
            #"""OR RX, RY, RZ"""
            if op_code & 0xF0FF:
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x720
            x_reg = (op_code >> 16) - 0x7200 - (y_reg << 4)
            z_reg = (op_code >> 8) - ((op_code >> 12) << 4)

            self.register[z_reg] = self.or_op(self.register[x_reg],
                    self.register[y_reg])
        else:
            raise ValueError("Invalid op code")
