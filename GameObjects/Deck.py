import os
import random

import pygame
from Constants import ART_PATH, CARD_BACK_PATH, CARD_DIMENSIONS
from GameObjects.Card.Card import BaseCard, Card
from GameObjects.GameObject import GameObject
from PModels import PlayerType
from GameObjects.SpriteRenderer import SpriteRenderer
from Utils.Text import draw_centered_text


class DeckFullError(IndexError):
    def __init__(self, *args):
        super().__init__(*args)


class DeckController(GameObject):
    def __init__(self, game, parent=None, capacity=30, pivot=...):
        super().__init__(game, parent, pivot)
        self.cards: list[BaseCard] = []
        self.sprites: list[SpriteRenderer] = [
            SpriteRenderer(self, CARD_BACK_PATH, CARD_DIMENSIONS) for _ in range(5)
        ]
        self.rect = self.sprites[0].sprite.get_rect(center=self.transform.position)
        self.capacity = capacity
        self.max_sprite_rotation = 8
        self._init_sprites()
        # print([sprite.transform.rotation for sprite in self.sprites])
        self.card_count = 0
        self.text_color = pygame.Color(255, 255, 255)
        self.owner: int = PlayerType.ME

    def add_card(self, card: BaseCard):
        if self.card_count >= self.capacity:
            raise DeckFullError("Trying to add a card to a full deck")
        self.cards.append(card)
        self.card_count += 1

    def get_and_remove_top_card(self) -> BaseCard:
        card = self.cards.pop()
        self.card_count -= 1
        return card

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
