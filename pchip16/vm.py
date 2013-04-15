"""
pchip16 VM class
"""

class VM(object):
    """Object representing a single virtual machine instance"""
    program_counter = 0
    stack_ponter = 0
    flags = 0
    register = {}
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
            if op_code >> 24 == 0x13:
                #"""JME RX, RY, HHLL"""
                #13 YX LL HH
                y_reg = (op_code >> 20) - 0x130
                x_reg = ((op_code >> 16) - (y_reg << 4) - 0x1300)
                hh_addr = op_code - (op_code >> 8 << 8)
                ll_addr = (op_code - hh_addr - (op_code >> 16 << 16) ) >> 8

                if self.register[x_reg] == self.register[y_reg]:
                    self.program_counter = (hh_addr << 8) + ll_addr
