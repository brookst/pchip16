"""
pchip16 interface - graphics audio and controls module
"""

import pygame

def nibble_iter(data):
    """Yield back data, one nibble at a time"""
    while data:
        yield data & 0xF
        data = data >> 4

# pylint: disable-msg=R0903
class Sprite(pygame.sprite.Sprite):
    """Class for a contiguous set of pixel values"""
    def __init__(self, data, width, height, postition):
        self.position = postition
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        for i, nibble in enumerate(nibble_iter(data) ):
            if nibble:
                self.image.set_at( (i % width, i // height), (255, 255, 255) )
 
class Interface:
    """Interface to graphics audio and controls"""
    def __init__(self):
        self.frame = 0
        self.vblank = True
        self._running = True
        self._display_surf = None
        self.clock = pygame.time.Clock()
        self.size = 320, 240
 
    def init(self):
        """Create display"""
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size,
            pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
 
    def event(self, event):
        """Handle input"""
        if event.type == pygame.QUIT:
            self._running = False

    def loop(self):
        """Interpret commands"""
        self._display_surf.fill( (0, 0, 0) )
        position = self.frame % 316, self.frame % 236
        sprite = Sprite(0xFFFFF00FF00FFFFF, 4, 4, position)
        self._display_surf.blit(sprite.image, sprite.position)
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
 
    def execute(self):
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
    INTERFACE = Interface()
    INTERFACE.execute()
