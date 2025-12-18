import os
import pygame
from Constants import ART_PATH, CARD_DIMENSIONS
from GameObjects.Deck import DeckController
from GameObjects.SpriteRenderer import SpriteRenderer


class GraveyardController(DeckController):
    def __init__(self, game, parent=None, capacity=30, pivot=...):
        super().__init__(game, parent, capacity, pivot)
        self.sprites = [
            SpriteRenderer(
                self,
                pygame.image.load(os.path.join(ART_PATH, "gy.png")),
                dimensions=CARD_DIMENSIONS,
            )
        ]

    def render(self, surface):
        super().render(surface)
        pygame.draw.rect(surface, pygame.Color("red"), self.rect, width=1)
