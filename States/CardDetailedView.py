from GameObjects.Card import CardController
from GameObjects.Database import CARD_DATABASE
from States.State import State
import pygame as p
import pygame.freetype

from UI.Button import TextButton
from UI.Label import Label


class CardDetailedView(State):
    def __init__(
        self,
        game,
        data: object | None = None,
        layer="foreground",
        card=CARD_DATABASE["goth_girl"],
    ):
        super().__init__(game, data, layer)
        self.card_data = card
        self.card = CardController(self.game, self)
        self.card.from_card(card)
        self.card.scale_by(0)
        self.card.move((self.game.GAME_W * 0.25, self.game.GAME_H * 0.5))
        self.font = self.game.fonts["october_crow"]["medium"]
        # self.text_surf = p.Surface(
        #     (self.game.GAME_W * 0.7, self.game.GAME_H * 0.9), p.SRCALPHA
        # )
        self.text_alpha = 0
        self.text_color = (255, 255, 255)
        self.anim_dur = 2
        # self.text_surf = self.text_surf.convert_alpha()
        self.game.tweener_manager.add_tween(
            self, "text_alpha", to_=255, duration=self.anim_dur
        )
        self.card.tween_scale_to(7.0)
        self.go_back_btn = TextButton(
            self.canvas,
            center=(self.game.GAME_W - 30, 15),
            width=15,
            height=15,
            text="<",
            corner_radius=2,
            command=self.game.pop_state,
        )
        r = p.Rect(self.game.GAME_W * 0.6, 30, self.game.GAME_W * 0.5, 60)
        self.lab_title = Label(
            self.canvas,
            center=r.center,
            width=r.w,
            height=r.h,
            fg_color=(255, 255, 255),
            text=self.card_data.name,
            font=self.game.fonts["october_crow"]["big"],
        )
        self.lab_desc = Label(
            self.canvas,
            center=p.Vector2(r.center) + p.Vector2(0, 100),
            width=r.w,
            height=r.height,
            fg_color=(255, 255, 255),
            text=self.card_data.description,
        )
        self.lab_tags = Label(
            self.canvas,
            center=p.Vector2(r.center) + p.Vector2(0, 400),
            width=r.w,
            height=r.h,
            fg_color=(255, 255, 255),
            text=str(self.card_data.tags),
        )
        # self.text_surf = self.font.render("AABBCCddeeff", True, self.text_color)
        # self.text_surf.set_alpha(0)

    def update(self, delta_time):
        super().update(delta_time)
        self.card.update(delta_time)

    def render(self, surface):
        super().render(surface)
        self.card.render(surface)
        # Separator
        p.draw.rect(
            surface,
            (100, 100, 100),
            p.Rect(self.game.GAME_W * 0.5, 100, self.game.GAME_W * 0.45, 4),
            border_radius=3,
        )
