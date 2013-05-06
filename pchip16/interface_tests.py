"""
pchip16 interface test runner
"""
#pylint: disable=I0011, R0904

import unittest
from pchip16.interface import Interface
import pygame

class TestInterface(unittest.TestCase):
    """Test interface functions"""
    def setUp(self):
        super(TestInterface, self).setUp()
        self.face = Interface()

    def test_init(self):
        self.assertEqual(self.face.frame, 0 )
        self.assertEqual(self.face.size, (320, 240) )
        self.assertEqual(self.face.bg, (0, 0, 0) )
        self.assertEqual(self.face.sprite_size, (0, 0) )
        self.assertEqual(self.face.sprite_flip, (0, 0) )

    def test_end(self):
        class Mock_Event(object):
            type = pygame.QUIT
        self.face.event(Mock_Event() )
        self.assertFalse(self.face._running)

    def test_colors(self):
        """Test BGC N"""
        self.face.set_bg(0xF)
        self.assertEqual(self.face.bg, (255, 255, 255, 255) )
        self.face.set_bg(0x0)
        self.assertEqual(self.face.bg, (0, 0, 0, 0) )

    def test_sprite_size(self):
        """Test SPR, HHLL"""
        self.face.sprite_size = (4,4)
        self.assertEqual(self.face.sprite_size, (4, 4) )

    def test_draw_sprite(self):
        """Test DRW RX, RY, HHLL"""
        self.face.sprite_size = (4,4)
        self.face.draw(0xFFFFF00FF00FFFFF, (0,0) )
        self.face.draw(0xFFFFF00FF00FFFFF, (5,5) )
        self.face.draw(0xFFFFF00FF00FFFFF, (10,10) )
        self.face.draw(0xFFFFF00FF00FFFFF, (15,15) )
