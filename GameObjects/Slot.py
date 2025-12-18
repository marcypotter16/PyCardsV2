from Constants import COLORS, SLOT_DIMENSIONS
from Game import Game
from GameObjects.Card import CardController
from GameObjects.GameObject import GameObject
from GameObjects.Card import Card
import pygame as p


class SlotUnavailableError(Exception):
    pass


class SlotNotEmptyError(Exception):
    pass


class Slot:
    def __init__(self, content: Card | None = None):
        self.content = content


class SlotController(GameObject):
    def __init__(self, game: Game, parent=None, is_special: bool = False):
        super().__init__(game, parent)
        self.rect = p.Rect((0, 0), SLOT_DIMENSIONS)
        self.available = True
        self.is_special = is_special
        self.highlighted = False
        self.content = None
        self.color: p.Color = (
            COLORS["slot"]["o_color"]
            if not self.is_special
            else COLORS["slot"]["special_color"]
        )
        self.o_color: p.Color = COLORS["slot"]["o_color"]

    def move(self, new_position):
        super().move(new_position)
        self.rect.center = self.transform.position

    def can_add_card(self, c: CardController) -> bool:
        return self.available and self.content is None

    def add_card(self, c: CardController):
        if not self.available:
            raise SlotUnavailableError
        if self.content is not None:
            raise SlotNotEmptyError
        if self.content is None:
            self.content = c
            c.parent = self
            if c.transform.scale != 1:
                c.tween_pos_and_scale(self.rect.center, 1.0)
            else:
                c.tween_pos(self.rect.center)

    def set_available(self, available: bool):
        self.available = available
        self.color = self.o_color if available else p.Color(100, 0, 0)

    def set_special(self, special: bool):
        self.is_special = special
        self.color = (
            COLORS["slot"]["o_color"]
            if not self.is_special
            else COLORS["slot"]["special_color"]
        )

    def update(self, delta):
        if self.available:
            super().update(delta)

    def render(self, surface):
        super().render(surface)
        if self.highlighted or not self.available:
            p.draw.rect(
                surface,
                self.color.lerp((0, 0, 0), 0.8 if self.available else 0.2),
                self.rect,
                0,
                2,
            )
        p.draw.rect(surface, self.color, self.rect, 1, 2)

        if self.content is not None:
            self.content.render(surface)

    def is_empty(self):
        return self.content is None

    def __repr__(self):
        if self.is_empty():
            return "empty"
        return str(self.content)
