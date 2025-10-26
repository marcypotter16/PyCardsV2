from Game import Game
from Models.Card import Card, CardController
from Models.Slot import SlotController
from Models.Card2 import Card2
from States.State import State
import pygame as p

from Utils.Timer import Timer


class CardTestState(State):
    def __init__(self, game: Game, msg=None, layer="foreground"):
        super().__init__(game, msg, layer)
        self.slot = SlotController(self.game)
        self.slot.move((1000, 200))
        # Timer(lambda: self.slot.add_card(self.card2), 2)

    def from_card(self, card: Card):
        self.card = CardController(self.game)
        self.card2 = Card2(self.game)
        self.card2.move(p.Vector2(100, 100))
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
