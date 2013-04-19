"""
pchip16 utils - tools for debugging
"""

import inspect
from pchip16.vm import CARRY, ZERO, OVERFLOW, NEGATIVE

def print_local(*selection):
    """Print selected variables from enclosing scope"""
    form_string = "%s: %%(%s)s "
    frame = inspect.currentframe()
    _select_locals(frame, form_string, *selection)

def print_hex(*selection):
    """Print selected variables from enclosing scope"""
    form_string = "%s: 0x%%(%s)x "
    frame = inspect.currentframe()
    _select_locals(frame, form_string, *selection)

def _select_locals(frame, form_string, *selection):
    """Internal print function"""
    try:
        non_locals = frame.f_back.f_locals
        form = "Locals: "
        for var in selection:
            form += form_string % (var, var)
        form = form[:-1]
        print(form %non_locals)
    finally:
        del frame

def print_flags(flags):
    """Print small string of flag characters"""
    ret = "Z" if flags & ZERO else "z"
    ret += "C" if flags & CARRY else "c"
    ret += "O" if flags & OVERFLOW else "o"
    ret += "N" if flags & NEGATIVE else "n"
    print(ret)

def complement(value):
    """Compute twos complement of value"""
    return 0xFFFF - value + 1

def is_neg(value):
    """Check if the sign bit is set"""
    return value & 0x8000

def to_hex(deca):
    """Return twos compliment hex from signed integer"""
    if deca < 0:
        return 0xFFFF & deca
    return deca

def to_dec(hexa):
    """Return signed integer from twos compliment"""
    if hexa > 0x7FFF:
        return hexa - 0x10000
    return hexa
