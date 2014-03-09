"""
pchip16 assembler
"""
#pylint: disable=W0142
from pchip16.instructions import INSTRUCTIONS, SignatureMismatch
import re

class Assembler(object):
    """Assembler for a contigious code block"""
    ops = INSTRUCTIONS
    source = ""
    addr = 0

    def __init__(self):
        pass

    def list(self):
        """Print a list of instructions"""
        for opr in self.ops:
            print("%4s %02d" %(self.ops[opr], opr) )

    @staticmethod
    def parse_line(line):
        """Parse source line into tokens"""
        uncommented = re.search("([^;]*)", line.upper()).group()
        tokens = re.findall(r"[-\w]+", uncommented)
        if not tokens:
            return None # Ignore empty lines
        return tokens

    @staticmethod
    def select_operand(operand):
        """Pick out operand type"""
        if operand[0] == 'R':
            return 'reg'
        elif operand[:2] == '0x':
            return 'word'
        else:
            raise Exception("Operand %s type unknown" %operand)

    @staticmethod
    def assemble_line(line):
        """Generate assembly corresponding to one line of source"""
        tokens = Assembler.parse_line(line)
        if not tokens:
            return ""
        for instruction in INSTRUCTIONS[tokens[0]]:
            try:
                return instruction(tokens)
            except SignatureMismatch:
                pass
        raise SignatureMismatch(tokens)

    def assemble(self):
        """Generate assembly for the current source"""
        code = b""
        for line in self.source.splitlines():
            code += self.assemble_line(line)
        return code

def test():
    """Call list on a temporary Assembler"""
    asm = Assembler()
    asm.source = """ ldi r6, 3   ; reset score
        ldi r0, 0xFF13
        ;stm r0, ascii_score_val ; and in memory too!
        ldi r0, 40
        stm r0, 0xF300  ; timer mult. const. = 40
        ldi r0, 0x15
        stm r0, 0xF302  ; move cnt reset value = 0x15
    """
    print(asm.assemble())

if __name__ == '__main__':
    test()
