import random
from typing import TYPE_CHECKING

import pygame
from Constants import CARD_BACK_PATH, CARD_DIMENSIONS
from GameObjects.Card.Card import BaseCard, CardControllerBase
from GameObjects.GameObject import GameObject
from PModels import PlayerType
from GameObjects.SpriteRenderer import SpriteRenderer
from Utils.Text import draw_centered_text
from Utils.UCard import create_card_controller

if TYPE_CHECKING:
    from Game import Game


class DeckFullError(IndexError):
    def __init__(self, *args):
        super().__init__(*args)


class DeckEmptyError(IndexError):
    def __init__(self, *args):
        super().__init__(*args)


class DeckController(GameObject):
    """Controller for a deck of cards.

    Stores CardControllerBase instances to preserve runtime state (buffs, power changes).
    Cards in deck are not visible - only card backs are rendered.
    """

    def __init__(self, game: "Game", parent=None, capacity=30, pivot=...):
        super().__init__(game, parent, pivot)
        self.cards: list[CardControllerBase] = []
        self.sprites: list[SpriteRenderer] = [
            SpriteRenderer(self, CARD_BACK_PATH, CARD_DIMENSIONS) for _ in range(5)
        ]
        self.rect = self.sprites[0].sprite.get_rect(center=self.transform.position)
        self.capacity = capacity
        self.max_sprite_rotation = 8
        self._init_sprites()
        self.text_color = pygame.Color(255, 255, 255)
        self.owner: int = PlayerType.ME

    @property
    def card_count(self) -> int:
        return len(self.cards)

    def add_card_model(self, card_model: BaseCard, bg_image: str = "BG2.png"):
        """Add a card from its data model (creates a new controller).

        Use this when adding cards that don't have a controller yet (e.g., deck building).
        """
        if self.card_count >= self.capacity:
            raise DeckFullError("Trying to add a card to a full deck")
        controller = create_card_controller(self.game, card_model, parent=None, bg_image=bg_image)
        controller.owner = self.owner
        controller.is_visible = False  # Cards in deck are not rendered
        self.cards.append(controller)

    def add_card(self, card: CardControllerBase):
        """Add an existing card controller to the deck.

        Use this when moving a card from hand/board/graveyard to deck.
        """
        if self.card_count >= self.capacity:
            raise DeckFullError("Trying to add a card to a full deck")
        card.is_visible = False  # Cards in deck are not rendered
        self.cards.append(card)

    def draw_card(self) -> CardControllerBase:
        """Draw the top card from the deck.

        Returns the card controller with all its runtime state preserved.
        """
        if self.card_count == 0:
            raise DeckEmptyError("Trying to draw from an empty deck")
        card = self.cards.pop()
        card.is_visible = True  # Card becomes visible when drawn
        return card

    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.cards)

    def get_cards_by_tag(self, tag: str) -> list[CardControllerBase]:
        """Get all cards in deck with a specific tag."""
        return [c for c in self.cards if tag in c.card_model.tags]

    def _init_sprites(self):
        for sprite in self.sprites:
            sprite.rotate(
                random.random() * 2 * self.max_sprite_rotation
                - self.max_sprite_rotation
            )

    def render(self, surface):
        super().render(surface)
        font = self.game.fonts["javier_skull"]["big"]
        draw_centered_text(
            font, surface, str(self.card_count), self.text_color, self.sprites[0].rect
        )

    def move(self, new_position):
        super().move(new_position)
        self.rect.center = new_position
