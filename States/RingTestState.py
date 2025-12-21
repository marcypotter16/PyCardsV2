import random

import pygame
from GameObjects.MathRing import (
    AutomorphismGroup,
    Ring,
    Rings,
    StructureController,
    StructureController,
    UnitsGroup,
    Zn,
)
from States.State import State
from Utils.Colors import BLACK
from Utils.Timer import SpacedCallback

rings = [Rings.Z.value, Rings.Q.value, AutomorphismGroup(Zn(2)), UnitsGroup(Zn(6))]


class RingTestState(State):
    def __init__(self, game, data=None, layer="foreground", bg_color=BLACK):
        super().__init__(game, data, layer, bg_color)
        self.ring = StructureController(game)
        self.ring.move(self.game.GAME_CENTER)
        # self.ring.set_ring(PolyRingQuotient(Ring.Z, "x^2+1"), font_family="comfortaa")
        self.ring.set_structure(Zn(4), font_family="stix")
        self.ring.set_color(pygame.Color("white"))
        # self.ring.scale_by(0.5)
        # self.ring.set_ring(Ring.Zxmod)
        # self.ring.ring_sprite.set_sprite_no_scale(
        #     render_univariate_poly("x^3-3x+12", self.game, font_group="comfortaa")
        # )
        # self.sc = SpacedCallback(
        #     lambda: self.ring.set_ring(PolyRingQuotient(random.choice(rings), "x^2+1")),
        #     2.0,
        # )
        a = "ℤ/5ℤ"
        self.i = 1

        def callback():
            self.ring.set_structure(rings[self.i])
            self.i += 1
            self.i %= len(rings)

        self.sc = SpacedCallback(callback, 2.0)
        self.sc.start()

    def update(self, delta_time):
        super().update(delta_time)
        self.ring.update(delta_time)
        self.sc.update()

    def render(self, surface):
        super().render(surface)
        self.ring.render(surface)
        # pygame.draw.rect(
        #     surface,
        #     pygame.Color("red"),
        #     self.ring.ring_sprite.sprite.get_rect(center=self.ring.transform.position),
        #     2,
        # )
