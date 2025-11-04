from GameObjects.Card import CardController
from GameObjects.Database import CARD_DATABASE
from States.State import State
import pygame as p
import pygame.freetype

from UI.Button import TextButton


class CardDetailedView(State):
    def __init__(
        self,
        game,
        data: object | None = None,
        layer="foreground",
        card=CARD_DATABASE["goth_girl"],
    ):
        super().__init__(game, msg, layer)
        self.card_data = card
        self.card = CardController(self.game, self)
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
        # self.text_surf = self.font.render("AABBCCddeeff", True, self.text_color)
        # self.text_surf.set_alpha(0)

    def update(self, delta_time):
        super().update(delta_time)
        self.card.update(delta_time)

    def render(self, surface):
        super().render(surface)
        self.font.render_to(
            surface,
            self.game.SCREEN_CENTER,
            str(self.card_data.uid),
            (255, 255, 255, self.text_alpha),
        )
        self.card.render(surface)
        # draw_centered_text(self.game.fonts["javier_skull"]["huge"], surface, self.card_data.name, self.text_color)
        r = p.Rect(self.game.GAME_W * 0.6, 30, self.game.GAME_W * 0.5, 60)
        # p.draw.rect(surface, self.text_color, r, 1)
        self.game.fonts["october_crow"]["big"].render_to(
            surface,
            r,
            self.card_data.name,
            self.text_color,
            style=pygame.freetype.STYLE_OBLIQUE | pygame.freetype.STYLE_WIDE,
        )
        # Separator
        p.draw.rect(
            surface,
            (100, 100, 100),
            p.Rect(self.game.GAME_W * 0.5, 100, self.game.GAME_W * 0.4, 6),
            border_radius=3,
        )
