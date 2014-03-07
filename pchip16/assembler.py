"""
pchip16 assembler
"""
#pylint: disable=W0142
from pchip16.instructions import INSTRUCTIONS, NONE, XREG, YREG, ZREG, \
     AWORD, BWORD, SignatureMismatch
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
        uncommented = re.search("([^#]*)", line.upper()).group()
        tokens = re.findall(r"[\w]+", uncommented)
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
    def resolve_operands(tokens):
        """Organise operands from tokens"""
        ret = {'op': tokens[0]}
        sig = NONE
        regs = ['x', 'y', 'z']
        words = ['a', 'b']
        reg = 0
        word = 0
        for token in tokens[1:]:
            if token[0] == 'R' and len(token) == 2:
                ret[regs[reg]] = int(token[1], 16)
                reg += 1
            elif token[:2] == '0X':
                val = int(token[2:], 16)
                lla = val & 0xFF
                hha = val >> 8
                ret[words[word]] = (lla << 8) | hha
                word += 1
            else:
                raise Exception("Operand %s type unknown" %token)
        if 'x' in ret:
            sig |= XREG
        if 'y' in ret:
            sig |= YREG
        if 'z' in ret:
            sig |= ZREG
        if 'a' in ret:
            sig |= AWORD
        if 'b' in ret:
            sig |= BWORD
        return sig, ret

    @staticmethod
    def assemble_line(line):
        """Generate assembly corresponding to one line of source"""
        tokens = Assembler.parse_line(line)
        for instruction in INSTRUCTIONS[tokens[0]]:
            try:
                return instruction(tokens)
            except SignatureMismatch:
                pass
        raise SignatureMismatch()

def test():
    """Call list on a temporary Assembler"""
    asm = Assembler()

    asm.list()
    print(asm.assemble_line("NOP #NO-OP"))
    print(asm.assemble_line("CLS"))
    print(asm.assemble_line("JMP R1#Jump to addr in RX"))
    print(asm.assemble_line("MOV r1, rf #Move r1 to rf"))
    print(asm.assemble_line("addi r2, 0x1234"))
    print("should: 05215634")
    print(asm.assemble_line("DRW r1 r2 0x3456"))
    print("should: 06210300")
    print(asm.assemble_line("DRW r1 r2 r3"))
    print(asm.assemble_line("SNG 0xFF, 0x1234"))

if __name__ == '__main__':
    test()
