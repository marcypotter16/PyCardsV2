from Constants import CARD_DIMENSIONS
from Game import Game

# from GameObjects.Card import Card, CardController
from GameObjects.Database import CARD_DATABASE
from GameObjects.MathRing import Rings, Zn
from GameObjects.Slot import SlotController
from GameObjects.Card.Card import (
    Card,
    UnitCardController,
)
from GameObjects.Card.SpellCard import SpellCardController
from GameObjects.Card.ChangeStructureCard import ChangeStructureCardController
from States.CardDetailedView import CardDetailedView
from States.State import State
import pygame as p

from Utils.Timer import Timer


class CardTestState(State):
    def __init__(self, game: Game, data: object | None = None, layer="foreground"):
        super().__init__(game, data, layer)
        self.from_card(CARD_DATABASE["goth_girl"])
        self.slot = SlotController(self.game)
        self.slot.move((1300, 200))
        # Timer(lambda: self.slot.add_card(self.card2), 2)

    def from_card(self, card: Card):
        self.card = UnitCardController(self.game)
        self.card2 = SpellCardController(self.game)
        self.card.move(p.Vector2(200, 200))
        self.card2.move(self.game.GAME_CENTER)
        self.card2.from_card(CARD_DATABASE["plus_1"])
        # self.card2.tween_scale_to(1.0)
        self.card.from_card(card)
        self.card3 = ChangeStructureCardController(self.game, ring=Zn(27))
        self.card3.move(
            self.card2.transform.position + p.Vector2(0, CARD_DIMENSIONS[1])
        )
        self.card4 = ChangeStructureCardController(self.game, ring=Rings.Z)
        self.card4.move(
            self.card2.transform.position + p.Vector2(CARD_DIMENSIONS[0], 0)
        )

    def update(self, delta_time):
        super().update(delta_time)
        self.card.update(delta_time)
        self.card2.update(delta_time)
        self.card3.update(delta_time)
        self.card4.update(delta_time)
        if self.game.clicked_dx == -1:
            if self.card2.rect.collidepoint(self.game.cursorpos):
                # self.slot.add_card(self.card2)
                self.game.push_state(
                    CardDetailedView(self.game, card=self.card2.card_model)
                )
            if self.card.rect.collidepoint(self.game.cursorpos):
                self.game.push_state(
                    CardDetailedView(self.game, card=self.card.card_model)
                )
            if self.card3.rect.collidepoint(self.game.cursorpos):
                self.game.push_state(
                    CardDetailedView(self.game, card=self.card3.card_model)
                )
            if self.card4.rect.collidepoint(self.game.cursorpos):
                self.game.push_state(
                    CardDetailedView(self.game, card=self.card4.card_model)
                )

    def render(self, surface):
        super().render(surface)
        self.card.render(surface)
        self.card2.render(surface)
        self.card3.render(surface)
        self.card4.render(surface)
        self.slot.render(surface)
