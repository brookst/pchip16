#!/usr/bin/env python
"""
pchip16 interface - graphics audio and controls module
"""

import pygame
from threading import Thread

DIRMAP = {
    273:(0, -1), #Up
    274:(0, 1),  #Down
    275:(1, 0),  #Right
    276:(-1, 0), #Left
}

def nibble_iter(data):
    """Yield back data, one nibble at a time"""
    while data:
        yield data & 0xF
        data = data >> 4

# pylint: disable-msg=I0011,R0903
class Sprite(pygame.sprite.Sprite):
    """Class for a contiguous set of pixel values"""
    def __init__(self, data, width, height, postition):
        self.position = postition
        self.velocity = 0, 1
        pygame.sprite.Sprite.__init__(self)
        # pylint: disable-msg=I0011,E1121
        self.image = pygame.Surface([width, height])
        for i, nibble in enumerate(nibble_iter(data) ):
            if nibble:
                self.image.set_at( (i % width, i // height), (255, 255, 255) )

class Interface(Thread):
    """Interface to graphics audio and controls"""
    def __init__(self):
        Thread.__init__(self)
        self.frame = 0
        self.vblank = True
        self._running = True
        self._display_surf = None
        self.clock = pygame.time.Clock()
        self.size = 320, 240
        self.sprite = Sprite(0xFFFFF00FF00FFFFF, 4, 4, (0, 0) )

    def init(self):
        """Create display"""
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size,
            pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

    def stop(self):
        """Stop running"""
        self._running = False

    def event(self, event):
        """Handle input"""
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN and 272 < event.key < 277:
            self.sprite.velocity = DIRMAP[event.key]

    def loop(self):
        """Interpret commands"""
        #self._display_surf.fill( (0, 0, 0) )
        d_x, d_y = self.sprite.position
        v_x, v_y = self.sprite.velocity
        self.sprite.position = (d_x + v_x) % 320, (d_y + v_y) % 240
        self._display_surf.blit(self.sprite.image, self.sprite.position)
        self.frame += 1

    def render(self):
        """Update display and wait for timing"""
        self.vblank = False
        self.clock.tick(60)
        pygame.display.update()
        self.vblank = True

    def cleanup(self):
        """Destroy everything in use"""
        pygame.quit()

    def run(self):
        """Control events"""
        if self.init() == False:
            self._running = False

        while( self._running ):
            for event in pygame.event.get():
                self.event(event)
            self.loop()
            self.render()
        self.cleanup()

if __name__ == "__main__" :
    from time import sleep
    INTERFACE = Interface()
    INTERFACE.start()
    sleep(2)
    INTERFACE.stop()
    INTERFACE.join()
