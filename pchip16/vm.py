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
