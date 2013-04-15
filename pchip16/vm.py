"""
pchip16 VM class
"""

class VM(object):
    """Object representing a single virtual machine instance"""
    program_counter = 0
    stack_ponter = 0
    flags = 0
    mem = bytearray(0 for i in range(2**16) )
    register = bytearray(0 for i in range(16) )
    def __init__(self):
        for reg in range(0xf):
            self.register[reg] = 0
    def step(self):
        """Execute instruction at self.program_counter and increment"""
        self.program_counter += 1
    def execute(self, op_code):
        """Carry out instruction sepcified by op_code"""
        if op_code >> 28 == 0x1:
            #"""Jumps"""
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

        elif op_code >> 28 == 0x3:
            if op_code >> 20 == 0x300:
                #"""STM RX, HHLL"""
                x_reg = (op_code >> 16) - 0x3000
                hh_addr = op_code - ((op_code >> 8) << 8)
                ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

                addr = (hh_addr << 8) + ll_addr
                self.mem[addr] = self.register[x_reg]
