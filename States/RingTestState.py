import random

import pygame
from GameObjects.MathRing import (
    PolyRingQuotient,
    Ring,
    RingController,
    Zn,
    render_univariate_poly,
)
from States.State import State
from Utils.Colors import BLACK
from Utils.Timer import SpacedCallback

rings = [Ring.Q, Ring.F, Ring.R, Ring.Z, Ring.C, Ring.F, Ring.Fq]


class RingTestState(State):
    def __init__(self, game, data=None, layer="foreground", bg_color=BLACK):
        super().__init__(game, data, layer, bg_color)
        self.ring = RingController(game)
        self.ring.move(self.game.GAME_CENTER)
        # self.ring.set_ring(PolyRingQuotient(Ring.Z, "x^2+1"), font_family="comfortaa")
        self.ring.set_ring(Zn(4), font_family="ant")
        self.ring.set_color(pygame.Color("white"))
        self.ring.scale_by(0.5)
        # self.ring.set_ring(Ring.Zxmod)
        # self.ring.ring_sprite.set_sprite_no_scale(
        #     render_univariate_poly("x^3-3x+12", self.game, font_group="comfortaa")
        # )
        # self.sc = SpacedCallback(
        #     lambda: self.ring.set_ring(PolyRingQuotient(random.choice(rings), "x^2+1")),
        #     2.0,
        # )
        self.i = 1

        def callback():
            self.ring.scale_by(self.i)
            self.i += 1

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
