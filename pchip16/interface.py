"""
pchip16 interface - graphics audio and controls module
"""
#pylint: disable=R0902,E1121

import pygame
from threading import Thread, Event
from .utils import nibble_iter

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
    0xb:pygame.color.Color(0x252E38FF),
    0xc:pygame.color.Color(0x00467FFF),
    0xd:pygame.color.Color(0x68ABCCFF),
    0xe:pygame.color.Color(0xBCDEE4FF),
    0xf:pygame.color.Color(0xFFFFFFFF),
}

DIRMAP = {
    273:(0, -1), #Up
    274:(0, 1),  #Down
    275:(1, 0),  #Right
    276:(-1, 0), #Left
}

class NotInitializedError(Exception):
    """Indicate the interface must be initilized first"""
    pass

class Interface(Thread):
    """Interface to graphics audio and controls"""
    def __init__(self):
        Thread.__init__(self)
        self.frame = 0
        self.vblank = Event()
        self.running = False
        self._display_surf = None
        self.clock = pygame.time.Clock()
        self.palette = PALETTE
        self.size = 320, 240
        self.background = 0, 0, 0
        self.sprite_size = 0, 0
        self.sprite_flip = 0, 0
        self.sprite_cache = {}

    def init(self):
        """Create display"""
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size,
            pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.running = True

    @property
    def inputs(self):
        """List of inputs according to DIRMAP"""
        ret = []
        keys = pygame.key.get_pressed()
        for key in DIRMAP:
            if keys[key]:
                ret.append(DIRMAP[key])
        return ret

    def render_sprite(self, data):
        """Return a pygame sprite with data drawn on"""
        image = pygame.Surface(self.sprite_size)
        width, height = self.sprite_size
        for i, nibble in enumerate(nibble_iter(data)):
            image.set_at((i % width, i // width), self.palette[nibble])
        image.set_colorkey(self.palette[0x0])
        return image

    def draw(self, sprite_data, position):
        """Draw sprite_data on canvas at position = (x, y)"""
        if self._display_surf is None:
            raise NotInitializedError
        #Check the cache for preexisting sprite
        if sprite_data in self.sprite_cache:
            image = self.sprite_cache[sprite_data]
        else:
            image = self.render_sprite(sprite_data)
            self.sprite_cache[sprite_data] = image
        self._display_surf.blit(image, position)

    def event(self, event):
        """Handle input"""
        if event.type == pygame.QUIT:
            self.running = False

    def set_background(self, code):
        """Set background to color from palete"""
        self.background = self.palette[code]

    def flip(self):
        """Update display and wait for timing"""
        # self.clock.tick(30)
        pygame.display.update()
        self._display_surf.fill(self.background)
        self.vblank.set()
        self.vblank.clear()
        self.clock.tick(60)
        self.frame += 1

    def cease(self):
        """Stop running"""
        self.running = False

    def cleanup(self):
        """Destroy everything in use"""
        pygame.quit()

    def run(self):
        """Control events"""
        if not self.running:
            raise NotInitializedError
        while self.running:
            for event in pygame.event.get():
                self.event(event)
            self.flip()
        self.cleanup()
