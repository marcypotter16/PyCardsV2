from Constants import COLORS, SLOT_DIMENSIONS
from Game import Game
from Models.Card2 import Card2
from Models.GameObject import GameObject
from Models.Card import Card
import pygame as p


class Slot:
    def __init__(self, content: Card | None = None):
        self.content = content


class SlotController(GameObject):
    def __init__(self, game: Game):
        super().__init__(game)
        self.rect = p.Rect((0, 0), SLOT_DIMENSIONS)
        self.color: p.Color = COLORS["slot"]["o_color"]
        self.o_color: p.Color = COLORS["slot"]["o_color"]
        self.highlighted = False
        self.content = None

    def move(self, new_position):
        super().move(new_position)
        self.rect.center = self.transform.position

    def add_card(self, c: Card2):
        if self.content is None:
            self.content = c
            c.tween_pos(self.rect.center)

    def update(self, delta):
        super().update(delta)

    def render(self, surface):
        super().render(surface)
        if self.highlighted:
            p.draw.rect(surface, self.color.lerp((0, 0, 0), 0.8), self.rect, 0, 2)
        p.draw.rect(surface, self.color, self.rect, 1, 2)
        if self.content is not None:
            self.content.render(surface)
