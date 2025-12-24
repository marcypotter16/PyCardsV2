import os
from typing import TYPE_CHECKING

import pygame
from Constants import ART_PATH, CARD_DIMENSIONS
from GameObjects.Card.Card import BaseCard, CardControllerBase
from GameObjects.Deck import DeckController
from GameObjects.SpriteRenderer import SpriteRenderer
from Utils.UCard import create_card_controller

if TYPE_CHECKING:
    from Game import Game


class GraveyardController(DeckController):
    """Controller for the graveyard.

    Stores CardControllerBase instances to preserve runtime state.
    Unlike deck, graveyard contents are typically visible/queryable.
    """

    def __init__(self, game: "Game", parent=None, capacity=30, pivot=...):
        super().__init__(game, parent, capacity, pivot)
        self.sprites = [
            SpriteRenderer(
                self,
                pygame.image.load(os.path.join(ART_PATH, "gy.png")),
                dimensions=CARD_DIMENSIONS,
            )
        ]
        self.rect = self.sprites[0].sprite.get_rect(center=self.transform.position)

    def add_card_model(self, card_model: BaseCard, bg_image: str = "BG2.png"):
        """Add a card from its data model (creates a new controller).

        Use this for cards that were destroyed without a controller reference.
        """
        controller = create_card_controller(self.game, card_model, parent=None, bg_image=bg_image)
        controller.is_visible = False
        self.cards.append(controller)

    def add_card(self, card: CardControllerBase):
        """Add an existing card controller to the graveyard.

        Use this when a card dies/is discarded from play.
        Preserves all runtime state (power changes, buffs, etc.)
        """
        card.is_visible = False
        self.cards.append(card)

    def get_top_card(self) -> CardControllerBase | None:
        """View the top card of the graveyard without removing it."""
        if self.card_count == 0:
            return None
        return self.cards[-1]

    def remove_card(self, card: CardControllerBase) -> bool:
        """Remove a specific card from the graveyard (e.g., for resurrection effects).

        Returns True if the card was found and removed.
        """
        if card in self.cards:
            self.cards.remove(card)
            card.is_visible = True
            return True
        return False

    def get_cards_by_tag(self, tag: str) -> list[CardControllerBase]:
        """Get all cards in graveyard with a specific tag."""
        return [c for c in self.cards if tag in c.card_model.tags]

    def render(self, surface):
        super().render(surface)
        pygame.draw.rect(surface, pygame.Color("red"), self.rect, width=1)
