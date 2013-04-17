"""
pchip16 utils - tools for debugging
"""

import inspect

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