#!/usr/bin/env python
"""
pchip16 interface - graphics audio and controls module
"""

from __future__ import print_function
from pchip16 import Interface

def test():
    """Quick demo of threaded pygame interface"""
    # from time import sleep
    interface = Interface()
    interface.init()
    interface.start()
    pos = (0, 0)
    with open('external/chip16/src/Samples/Herdle/title.bin') as handle:
        spr_title = handle.read()
    with open('external/chip16/src/Samples/Herdle/dog.bin') as handle:
        spr_dog1 = handle.read(128)
        spr_dog2 = handle.read(128)
    try:
        interface.sprite_size = 224, 140
        interface.draw(spr_title, (48, 20) )
        frame = 0
        while interface.running:
            interface.vblank.wait()
            # print(interface.frame - frame)
            frame = interface.frame

            for offset in interface.inputs:
                pos = [x + (5*y) for x, y in zip(pos, offset)]

            interface.sprite_size = 224, 140
            interface.draw(spr_title, (48, 20) )
            interface.sprite_size = 0x10, 0x10
            if frame % 20 < 10:
                interface.draw(spr_dog1, pos)
            else:
                interface.draw(spr_dog2, pos)

        print("Pygame terminated")
    except None:#KeyboardInterrupt:
        print("Interrupted via Keyboard")
    interface.cease()
    interface.join()

if __name__ == "__main__" :
    test()
