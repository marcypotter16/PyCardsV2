from Game import Game

# from GameObjects.Card import Card, CardController
from GameObjects.Database import CARD_DATABASE
from GameObjects.Slot import SlotController
from GameObjects.Card import Card, CardController
from States.State import State
import pygame as p

from Utils.Timer import Timer


class CardTestState(State):
    def __init__(self, game: Game, data: object | None = None, layer="foreground"):
        super().__init__(game, data, layer)
        self.from_card(CARD_DATABASE["goth_girl"])
        self.slot = SlotController(self.game)
        self.slot.move((1000, 200))
        # Timer(lambda: self.slot.add_card(self.card2), 2)

    def from_card(self, card: Card):
        self.card = CardController(self.game)
        self.card2 = CardController(self.game)
        self.card2.move(p.Vector2(200, 200))
        self.card.move(self.game.SCREEN_CENTER)
        self.card2.from_card(card)
        self.card.from_card(card)

    def update(self, delta_time):
        super().update(delta_time)
        self.card.update(delta_time)
        self.card2.update(delta_time)
        if self.game.clicked_dx == -1:
            if self.card2.rect.collidepoint(self.game.mousepos):
                self.slot.add_card(self.card2)

    def render(self, surface):
        super().render(surface)
        self.card.render(surface)
        self.card2.render(surface)
        self.slot.render(surface)
