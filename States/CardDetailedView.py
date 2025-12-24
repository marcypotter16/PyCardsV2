from Constants import SPECIAL_CHARACTERS
from GameObjects.Card.Card import BaseCard
from Utils.UCard import create_card_controller
from GameObjects.Database import CARD_DATABASE
from States.State import State
import pygame as p
import pygame.freetype

from UI.Button import TextButton
from UI.Label import Label
from Utils.Draw import create_back_button


class CardDetailedView(State):
    def __init__(
        self,
        game,
        data: object | None = None,
        layer="foreground",
        card: BaseCard = CARD_DATABASE["goth_girl"],
    ):
        super().__init__(game, data, layer)
        self.card_data = card
        # Use factory function to create the appropriate card controller
        bg_img = "BG2.png" if not hasattr(card, "bg_image") else card.bg_image
        self.card = create_card_controller(
            self.game,
            card,
            parent=self,
            bg_image=bg_img,
        )
        # self.card.scale_by(0)
        self.target_scale = 2.0
        print(
            card.name,
            SPECIAL_CHARACTERS.values(),
            card.name in SPECIAL_CHARACTERS.values(),
        )
        self.name_font = (
            self.game.fonts["october_crow"]["big"]
            if card.name not in SPECIAL_CHARACTERS.values()
            else self.game.get_font("stix", 60)
        )
        self.card.tween_pos_and_scale(
            (self.game.GAME_W * 0.25, self.game.GAME_H * 0.5), self.target_scale
        )
        # self.go_back_btn = TextButton(
        #     self.canvas,
        #     center=(self.game.GAME_W - 30, 15),
        #     width=15,
        #     height=15,
        #     text="<",
        #     corner_radius=2,
        #     command=self.game.pop_state,
        # )
        self.go_back_btn = create_back_button(
            game,
            self.canvas,
            (
                game.GAME_W * 0.95,
                20,
            ),
        )
        self.go_back_label = Label(
            self.canvas,
            x=game.GAME_W * 0.95 - 5,
            y=40,
            text="back",
            font=self.game.get_font("ant", 15),
            fg_color=pygame.Color("white"),
        )
        r = p.Rect(self.game.GAME_W * 0.55, 30, self.game.GAME_W * 0.4, 60)
        # Card title (name)
        self.lab_title = Label(
            self.canvas,
            center=r.center,
            width=r.w,
            height=r.h,
            fg_color=(255, 255, 255),
            text=self.card_data.name,
            font=self.name_font,
        )

        # Card description - rendered with ant font, half of GAME_W width
        desc_width = int(self.game.GAME_W * 0.4)
        self.lab_desc = Label(
            self.canvas,
            center=p.Vector2(r.center) + p.Vector2(0, 150),
            width=desc_width,
            height=200,
            fg_color=(255, 255, 255),
            text=self.card_data.description,
            font=self.game.fonts["ant"]["medium"],
        )

        # Separator after description
        desc_separator_y = self.lab_desc.rect.bottom + 20

        # Card power (only for regular Cards, not SpellCards)
        # power_text = ""
        if hasattr(self.card_data, "base_power"):
            power_text = f"Power: {self.card_data.base_power}"
            self.lab_power = Label(
                self.canvas,
                center=p.Vector2(r.center) + p.Vector2(0, 300),
                width=r.w,
                height=r.h,
                fg_color=(255, 255, 255),
                text=power_text,
                font=self.game.fonts["ant"]["medium"],
            )

        # Card tags - format as human-readable text
        if hasattr(self.card_data, "tags") and self.card_data.tags:
            # Convert tags to nice format: "Science, Human, Element"
            tags_text = ", ".join(
                tag.replace("_", " ").title() for tag in self.card_data.tags
            )
        else:
            tags_text = "No tags"

        tags_y_pos = desc_separator_y + 80
        self.lab_tags = Label(
            self.canvas,
            center=p.Vector2(r.center[0], tags_y_pos),
            width=r.w,
            height=r.h,
            fg_color=(255, 255, 255),
            text=tags_text,
            font=self.game.fonts["ant"]["medium"],
        )

        # Store separator position for rendering
        self.desc_separator_rect = p.Rect(
            self.game.GAME_W * 0.6,
            desc_separator_y,
            self.game.GAME_W * 0.35,
            2,
        )
        # self.text_surf = self.font.render("AABBCCddeeff", True, self.text_color)
        # self.text_surf.set_alpha(0)

    def update(self, delta_time):
        super().update(delta_time)
        self.card.update(delta_time)

    def render(self, surface):
        super().render(surface)
        self.card.render(surface)
        # Separator between title and description
        p.draw.rect(
            surface,
            (100, 100, 100),
            p.Rect(
                self.game.GAME_W * 0.5,
                100,
                self.game.GAME_W * 0.45,
                4,
            ),
            border_radius=3,
        )
        # Separator between description and tags
        p.draw.rect(
            surface,
            (100, 100, 100),
            self.desc_separator_rect,
            border_radius=3,
        )
