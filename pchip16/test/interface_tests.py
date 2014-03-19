"""
pchip16 interface test runner
"""
#pylint: disable=I0011, R0903, R0904, R0923, C0111

import unittest
from pchip16.interface import Interface
import pygame
import os

os.environ['SDL_VIDEODRIVER'] = 'dummy'

class TestInterface(unittest.TestCase):
    """Test interface functions"""
    def setUp(self):
        # super(TestInterface, self).setUp()
        self.face = Interface()
        self.face.init()

    def test_init(self):
        self.assertEqual(self.face.frame, 0)
        self.assertEqual(self.face.size, (320, 240))
        self.assertEqual(self.face.background, (0, 0, 0))
        self.assertEqual(self.face.sprite_size, (0, 0))
        self.assertEqual(self.face.sprite_flip, (0, 0))

    def test_end(self):
        class MockEvent(object):
            type = pygame.QUIT
        self.face.event(MockEvent())
        self.assertFalse(self.face.running)

    def test_colors(self):
        """Test BGC N"""
        self.face.set_background(0xF)
        self.assertEqual(self.face.background, (255, 255, 255, 255))
        self.face.set_background(0x0)
        self.assertEqual(self.face.background, (0, 0, 0, 0))

    def test_sprite_size(self):
        """Test SPR, HHLL"""
        self.face.sprite_size = (4, 4)
        self.assertEqual(self.face.sprite_size, (4, 4))

    def test_draw_sprite(self):
        """Test DRW RX, RY, HHLL"""
        self.face.sprite_size = (4, 4)
        self.face.draw("\xFF\xFF\xF0\x0F\xF0\x0F\xFF\xFF", (4, 4))
