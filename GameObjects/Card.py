import os
from typing import Optional
from pydantic import BaseModel
import uuid
from Constants import (
    ART_PATH,
    CARD_ART_SIZE_RATIO,
    CARD_BACK_PATH,
    CARD_BASE_PATH,
    CARD_DIMENSIONS,
    CARD_TWEEN_DUR,
)

# from GameObjects.Database import CARD_DATABASE
from GameObjects.GameObject import GameObject
from GameObjects.PlayerType import PlayerType
from GameObjects.SpriteRenderer import SpriteRenderer
import math
import pygame as p

from PModels import PCardModel


class Card:
    def __init__(self, name: str, base_power: int, art_path: str):
        self.name = name
        self.base_power = base_power
        self.art_path = art_path


class CardController(GameObject):
    def __init__(self, game, parent=None):
        super().__init__(game, parent)
        self.base_sprite: SpriteRenderer = SpriteRenderer(
            self, CARD_BASE_PATH, CARD_DIMENSIONS
        )
        # self.art_sprite: SpriteRenderer = SpriteRenderer(
        #     self,
        #     CARD_DATABASE["goth_girl"].art_path,
        #     CARD_ART_SIZE_RATIO * CARD_DIMENSIONS,
        # )
        self.art_sprite = SpriteRenderer(self)
        self.art_sprite.set_dim(CARD_ART_SIZE_RATIO * CARD_DIMENSIONS)
        self.from_card(
            Card("Maire von Neumann", 5, os.path.join(ART_PATH, "PAGothGirl.png"))
        )
        for c in self.children:
            c.TWEEN_DUR = CARD_TWEEN_DUR
        # self.base_sprite.TWEEN_DUR = 5.0
        # self.base_sprite.tween_scale_by(2.0,
        # on_finish=lambda: self.base_sprite.tween_rot(60))
        self.back_sprite: SpriteRenderer = SpriteRenderer(
            self, CARD_BACK_PATH, CARD_DIMENSIONS
        )
        self.back_sprite.set_visible(False)
        self.base_sprite.setup_mb(True, 3)
        self.art_sprite.setup_mb(True, 3)

        self.last_saved_pos = self.transform.position.copy()
        self.face_up = True
        self.hovered = False
        self.rect = self.base_sprite.rect

        self.owner: int = PlayerType.ME
        self.uid: str = str(uuid.uuid4())  # Generate unique ID for this card instance
        self.current_power: int = 0  # Will be set when from_card is called
        self.dead: bool = False
        self.banished: bool = False

    # Move is already inherited from GameObject

    def flip(self):
        self.face_up = not self.face_up
        self.back_sprite.set_visible(self.face_up)
        self.art_sprite.set_visible(not self.face_up)
        self.base_sprite.set_visible(not self.face_up)

    def tween_pos(self, pos, drop=True):
        self.game.tweener_manager.add_tween(
            self.transform,
            "position",
            to_=p.Vector2(pos),
            on_finish=self.drop if drop else None,
            duration=CARD_TWEEN_DUR,
        )
        print(self.last_saved_pos, self.transform.position)
        for c in self.children:
            c.tween_pos(pos)

    def snap_back(self):
        self.tween_pos(self.last_saved_pos)

    def drop(self):
        self.last_saved_pos = p.Vector2(self.transform.position)

    def rotate(self, angle: float):
        super().rotate(angle)

    def face_mouse(self):
        vec = self.game.mousepos - self.base_sprite.position
        angle = -math.atan2(vec.y, vec.x)
        angle = math.degrees(angle)
        self.rotate(angle)

    def from_card(self, card: Card):
        self.card_model = card
        self.name = card.name
        self.base_power = card.base_power
        self.current_power = card.base_power  # Initialize current_power to base_power
        self.art_path = card.art_path
        self.art_sprite.set_sprite(p.image.load(self.art_path))

    def to_pydantic(self) -> PCardModel:
        """Convert this CardController to a PCardModel for serialization"""
        return PCardModel(
            uid=self.uid,
            name=self.name,
            base_power=self.base_power,
            current_power=self.current_power,
            description=None,  # TODO: Add description support
            owner=self.owner,
            dead=self.dead,
            banished=self.banished,
        )

    def tween_scale_to(self, new_scale):
        """Tweens the scale value from the current to the desired one"""
        self.game.tweener_manager.add_tween(
            self.transform,
            "scale",
            to_=new_scale,
            duration=CARD_TWEEN_DUR,
        )
        self.art_sprite.tween_scale_to(new_scale)
        self.base_sprite.tween_scale_to(new_scale)

    def update(self, delta):
        super().update(delta)
        # self.move(self.game.mousepos)
        # if self.game.clicked_sx == -1:
        #     if self.rect.collidepoint(self.game.mousepos):
        #         self.flip()
