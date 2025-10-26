from Constants import CARD_DIMENSIONS
from Game import Game
from Models.Card import Card, CardController
from Generic.Stack import Stack
import pygame as p

class HandFullError(IndexError):
    def __init__(self, *args):
        super().__init__(*args)

class HandModel:
    def __init__(self, cards: Stack[Card] | None = None, capacity: int = 10):
        self.cards: Stack[Card] = cards if cards is not None else Stack()
        self.capacity = capacity

    def add_card(self, c: Card):
        if self.cards.size() == self.capacity:
            raise HandFullError
        self.cards.push(c)
    
class HandController:
    def __init__(self, game: Game, topleft = (0, 0), distance_between_cards = 10, hand_model: HandModel | None = None):
        self.hand_model = hand_model if hand_model else HandModel()
        self.capacity = self.hand_model.capacity
        self.game = game
        self.topleft = p.Vector2(topleft)
        self.rect = p.Rect(topleft, (0, 0))
        self.distance_between_cards = distance_between_cards
        self.cards: list[CardController] = []

    def add_card(self, c: Card):
        self.hand_model.add_card(c)
        self.cards.append(c)

    def reorder(self):
        pass

    def update(self, dt):
        for c in self.cards:
            c.update(dt)

    def render(self, surface):
        for c in self.cards:
            c.render(surface)

