"""
pchip16 interface - graphics audio and controls module
"""

import pygame
from utils import nibble_iter

PALETTE = {
    0x0:pygame.color.Color(0x00000000),
    0x1:pygame.color.Color(0x000000FF),
    0x2:pygame.color.Color(0x888888FF),
    0x3:pygame.color.Color(0xBF3932FF),
    0x4:pygame.color.Color(0xDE7AAEFF),
    0x5:pygame.color.Color(0x4C3D21FF),
    0x6:pygame.color.Color(0x905F25FF),
    0x7:pygame.color.Color(0xE49452FF),
    0x8:pygame.color.Color(0xEAD979FF),
    0x9:pygame.color.Color(0x537A3BFF),
    0xa:pygame.color.Color(0xABD54AFF),
    0xa:pygame.color.Color(0x252E38FF),
    0xc:pygame.color.Color(0x00467FFF),
    0xd:pygame.color.Color(0x68ABCCFF),
    0xe:pygame.color.Color(0xBCDEE4FF),
    0xf:pygame.color.Color(0xFFFFFFFF),
}

# pylint: disable-msg=I0011,R0903
class Interface:
    """Interface to graphics audio and controls"""
    def __init__(self):
        self.frame = 0
        self.vblank = True
        self._running = False
        self._display_surf = None
        self.clock = pygame.time.Clock()
        self.palette = PALETTE
        self.size = 320, 240
        self.bg = 0, 0, 0
        self.sprite_size = 0, 0
        self.sprite_flip = 0, 0
 
    def init(self):
        """Create display"""
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size,
            pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

    def draw(self, sprite_data, position):
        """Draw sprite_data on canvas at position = (x, y)"""
        if not self._running:
            self.init()

        if self.sprite_size == (0, 0):
            return

        image = pygame.Surface(self.sprite_size)
        for i, nibble in enumerate(nibble_iter(sprite_data) ):
            if nibble:
                width, height = self.sprite_size
                image.set_at( (i % width, i // height), self.palette[nibble] )

        self._display_surf.blit(image, position)
 
    def event(self, event):
        """Handle input"""
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN and 272 < event.key < 277:
            self.sprite.velocity = DIRMAP[event.key]

    def set_bg(self, code):
        """Set bg to color from palete"""
        self.bg = self.palette[code]

    def flip(self):
        """Update display and wait for timing"""
        self.vblank = False
        self.clock.tick(60)
        pygame.display.update()
        self.frame += 1
        self.vblank = True

    def cleanup(self):
        """Destroy everything in use"""
        pygame.quit()
 
    def execute(self):
        """Control events"""
        if self.init() == False:
            self._running = False
 
        while( self._running ):
            for event in pygame.event.get():
                self.event(event)
            self.flip()
        self.cleanup()
