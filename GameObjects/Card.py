from enum import StrEnum
import os
from typing import Callable, Dict, List, Optional, Set, TYPE_CHECKING
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
from PModels import PlayerType
from GameObjects.SpriteRenderer import SpriteRenderer
import math
import pygame as p

from PModels import PCardModel

if TYPE_CHECKING:
    from GameObjects.EffectContext import EffectContext


class CardTag(StrEnum):
    SCIENCE = "science"
    HUMAN = "human"
    ELEMENT = "element"
    NOBLE = "noble"


class Card:
    def __init__(
        self,
        name: str,
        base_power: int,
        art_path: str,
        tags: List[CardTag] = [],
        effects: Dict[str, List[Callable[["EffectContext"], None]]] = {},
        description: str = "",
    ):
        self.name = name
        self.current_power = self.base_power = base_power
        self.art_path = art_path
        self.tags: Set[CardTag] = set(tags)
        self.effects = effects
        self.description = description


class CardController(GameObject):
    def __init__(self, game, parent=None):
        super().__init__(game, parent)
        self.base_sprite: SpriteRenderer = SpriteRenderer(
            self, CARD_BASE_PATH, CARD_DIMENSIONS
        )
        self.art_sprite = SpriteRenderer(self)
        self.art_sprite.set_dim(CARD_ART_SIZE_RATIO * CARD_DIMENSIONS)

        self.power_text_surf = self.game.fonts["october_crow"]["small"].render(
            "0", False, p.Color(255, 255, 255)
        )
        self.power_text_sprite = SpriteRenderer(self, self.power_text_surf, (20, 20))

        # Store the initial offset from card center for scaling
        self.power_text_offset = -0.5 * CARD_DIMENSIONS + p.Vector2(5, 5)
        self.power_text_sprite.move(self.power_text_offset)

        for c in self.children:
            c.TWEEN_DUR = CARD_TWEEN_DUR
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

        self.owner: str = PlayerType.ME
        self.uid: str = str(uuid.uuid4())  # Generate unique ID for this card instance
        self.current_power: int = 0  # Will be set when from_card is called
        self.dead: bool = False
        self.banished: bool = False

    # Move is already inherited from GameObject

    def change_power(self, new_power: int):
        match True:
            case _ if new_power == self.base_power:
                color = p.Color(255, 255, 255)  # White
            case _ if new_power < self.base_power:
                color = p.Color(255, 0, 0)  # Red
            case _:
                color = p.Color(0, 255, 0)  # Green

        self.power_text_surf = self.game.fonts["october_crow"]["small"].render(
            str(new_power), False, color
        )
        self.card_model.current_power = new_power
        self.power_text_sprite.set_sprite(self.power_text_surf)

    def flip(self):
        self.face_up = not self.face_up
        self.back_sprite.set_visible(not self.face_up)
        self.art_sprite.set_visible(self.face_up)
        self.base_sprite.set_visible(self.face_up)

    def tween_pos(self, pos, drop=True):
        self.game.tweener_manager.add_tween(
            self.transform,
            "position",
            to_=p.Vector2(pos),
            on_finish=self.drop if drop else None,
            duration=CARD_TWEEN_DUR,
        )
        # print(self.last_saved_pos, self.transform.position)
        for c in self.children:
            # Skip power_text_sprite - its position is managed by tween_scale_to
            if c is self.power_text_sprite:
                continue
            c.tween_pos(c.transform.position + pos - self.transform.position)

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
        self.change_power(card.base_power)
        self.art_path = card.art_path
        self.art_sprite.set_sprite(p.image.load(self.art_path))

    def to_pydantic(self) -> PCardModel:
        """Convert this CardController to a PCardModel for serialization"""
        return PCardModel(
            uid=self.uid,
            name=self.name,
            base_power=self.base_power,
            current_power=self.current_power,
            description=self.card_model.description,
            tags=[str(tag) for tag in self.card_model.tags],
            owner=self.owner,
            dead=self.dead,
            banished=self.banished,
        )

    def tween_scale_to(self, new_scale, target_card_position=None):
        """Tweens the scale value from the current to the desired one

        Args:
            new_scale: The target scale factor
            target_card_position: Optional - the position the card will be at after scaling/moving
        """
        self.game.tweener_manager.add_tween(
            self.transform,
            "scale",
            to_=new_scale,
            duration=CARD_TWEEN_DUR,
        )
        self.art_sprite.tween_scale_to(new_scale)
        self.base_sprite.tween_scale_to(new_scale)

        # Calculate where the power text should end up
        # Use target position if provided, otherwise use current position
        if target_card_position is None:
            target_card_position = self.transform.position

        # Scale the offset and add to the target card position
        scaled_offset = self.power_text_offset * new_scale
        power_text_target = target_card_position + scaled_offset
        self.power_text_sprite.tween_pos(power_text_target)

    def update(self, delta):
        super().update(delta)
        # self.move(self.game.mousepos)
        # if self.game.clicked_sx == -1:
        #     if self.rect.collidepoint(self.game.mousepos):
        #         self.flip()
