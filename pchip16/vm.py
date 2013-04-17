"""
pchip16 VM class
"""

from array import array

CARRY = 0x1 << 1
ZERO = 0x1 << 2
OVERFLOW = 0x1 << 6
NEGATIVE = 0x1 << 7

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

    def add_16bit(self, *values):
        """16 bit signed addition operation"""
        value = sum(values)
        if value > 0x10000:
            self.flags |= CARRY
            if value & 0x8000:
                value -= 0x10000
                self.flags &= ~OVERFLOW
            else:
                #Sign overflow!!!
                value -= 0x10000
                self.flags |= OVERFLOW
                print('Sign overflow')
        else:
            self.flags &= ~CARRY
            if value & 0x8000:
                #Sign overflow!!!
                self.flags |= OVERFLOW
                print('Sign overflow')
            else:
                self.flags &= ~OVERFLOW
        return value

    def add(self, op_code):
        """Addition"""
        if op_code >> 20 == 0x400:
            #"""ADDI RX, HHLL"""
            x_reg = (op_code >> 16) - 0x4000
            hh_addr = op_code - ((op_code >> 8) << 8)
            ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

            addr = (hh_addr << 8) + ll_addr
            print(hex(self.register[x_reg] + self.mem[addr]))

            value = self.add_16bit(self.register[x_reg], self.mem[addr])
            self.register[x_reg] = value
        elif op_code >> 24 == 0x41:
            #"""ADD RX, RY"""
            if op_code - ((op_code >> 16) << 16):
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x410
            x_reg = (op_code >> 16) - 0x4100 - (y_reg << 4)

            value = self.add_16bit(self.register[x_reg], self.register[y_reg])
            self.register[x_reg] = value
        elif op_code >> 24 == 0x42:
            #"""ADD RX, RY, RZ"""
            if op_code & 0x1011:
                raise ValueError("Invalid op code")
            y_reg = (op_code >> 20) - 0x420
            x_reg = (op_code >> 16) - 0x4200 - (y_reg << 4)
            z_reg = (op_code >> 8) - ((op_code >> 12) << 4)
            print(hex(x_reg), hex(y_reg), hex(z_reg))

            self.register[x_reg] = self.add_16bit(self.register[x_reg],
                    self.register[y_reg], self.register[z_reg])
        else:
            raise ValueError("Invalid op code")
