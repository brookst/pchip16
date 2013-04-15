"""
pchip16 VM class
"""

class VM(object):
    """Object representing a single virtual machine instance"""
    program_counter = 0
    stack_ponter = 0
    flags = 0
    register = {}
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
