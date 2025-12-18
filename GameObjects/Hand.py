from Constants import CARD_DIMENSIONS
from Game import Game
from Collections.Stack import Stack
import pygame as p

from GameObjects.Card import Card, CardControllerBase, create_card_controller
from GameObjects.GameObject import GameObject
from PModels import PlayerType


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


class HandController(GameObject):
    def __init__(
        self,
        game: Game,
        parent=None,
        center=(0, 0),
        distance_between_cards=10,
        hand_model: HandModel | None = None,
    ):
        super().__init__(game, parent)
        self.hand_model = hand_model if hand_model else HandModel()
        self.capacity = self.hand_model.capacity
        self.center = p.Vector2(center)
        self.rect = p.Rect(0, 0, distance_between_cards, CARD_DIMENSIONS.y * 1.1)
        self.transform.move(p.Vector2(center))
        self.rect.center = center
        self.distance_between_cards = distance_between_cards
        self.owner: int = PlayerType.ME
        self.cards: list[CardControllerBase] = []

    def add_card(self, c: Card, bg_image="GreenBG1.png"):
        """Add a card to the hand. Automatically creates the correct controller type.

        Args:
            c: Card or SpellCard instance
            bg_image: Background image for spell cards (default: GreenBG1.png)
        """
        self.hand_model.add_card(c)
        c_go = create_card_controller(self.game, c, self, bg_image)
        self.cards.append(c_go)
        r = self.rect.copy()
        r.width += CARD_DIMENSIONS[0] + self.distance_between_cards
        r.center = self.rect.center
        self.rect = r
        self.reorder()

    def reorder(self):
        x0 = (
            self.rect.left + self.distance_between_cards + int(0.5 * CARD_DIMENSIONS[0])
        )
        y0 = self.transform.position.y
        for i, c in enumerate(self.cards):
            pos_x = x0 + i * (CARD_DIMENSIONS[0] + self.distance_between_cards)
            pos_y = y0
            # c.tween_pos((pos_x, pos_y))
            # TODO go back to tweening
            c.move((pos_x, pos_y))
            c.drop()
            if self.owner == PlayerType.OP and c.face_up:
                c.flip()

    def update(self, dt):
        for c in self.cards:
            c.update(dt)

    def render(self, surface):
        p.draw.rect(surface, (255, 255, 0), self.rect, 2, 2)
        self.cards.sort(key=lambda c: c.hovered)
        for c in self.cards:
            c.render(surface)
        # p.draw.circle(surface, (0, 255, 0), self.rect.center, 10)
        # p.draw.circle(surface, (255, 0, 0), self.transform.position, 10)
