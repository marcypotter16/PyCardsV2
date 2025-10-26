from Constants import (
    CARD_ART_SIZE_RATIO,
    CARD_BACK_PATH,
    CARD_BASE_PATH,
    CARD_DIMENSIONS,
)
from Models.CardDatabase import CARD_DATABASE
from Models.GameObject import GameObject
from Models.SpriteRenderer import SpriteRenderer
import math


class Card2(GameObject):
    def __init__(self, game):
        super().__init__(game)
        self.base_sprite: SpriteRenderer = SpriteRenderer(
            self, CARD_BASE_PATH, CARD_DIMENSIONS
        )
        self.art_sprite: SpriteRenderer = SpriteRenderer(
            self,
            CARD_DATABASE["goth_girl"].art_path,
            CARD_ART_SIZE_RATIO * CARD_DIMENSIONS,
        )
        # self.base_sprite.TWEEN_DUR = 5.0
        # self.base_sprite.tween_scale_by(2.0,
        # on_finish=lambda: self.base_sprite.tween_rot(60))
        self.back_sprite: SpriteRenderer = SpriteRenderer(
            self, CARD_BACK_PATH, CARD_DIMENSIONS
        )
        self.back_sprite.set_visible(False)
        self.base_sprite.setup_mb(True, 3)
        self.art_sprite.setup_mb(True, 3)

        self.face_up = True
        self.rect = self.base_sprite.rect

    # Move is already inherited from GameObject

    def flip(self):
        self.face_up = not self.face_up
        self.back_sprite.set_visible(self.face_up)
        self.art_sprite.set_visible(not self.face_up)
        self.base_sprite.set_visible(not self.face_up)

    def tween_pos(self, pos):
        for c in self.children:
            c.tween_pos(pos)

    def rotate(self, angle: float):
        super().rotate(angle)

    def face_mouse(self):
        vec = self.game.mousepos - self.base_sprite.position
        angle = -math.atan2(vec.y, vec.x)
        angle = math.degrees(angle)
        self.rotate(angle)

    def update(self, delta):
        super().update(delta)
        # self.move(self.game.mousepos)
        if self.game.clicked_sx == -1:
            if self.rect.collidepoint(self.game.mousepos):
                self.flip()
