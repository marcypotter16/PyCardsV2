import pygame
from Constants import CARD_DIMENSIONS
from Utils.UCard import create_card_controller
from PModels import PlayerType
from States.State import State
from UI.Label import Label
from Utils.Draw import create_back_button


class GraveyardViewState(State):
    """State for viewing dead cards in a grid layout"""

    COLUMNS = 4
    CARD_SCALE = 1.0
    CARD_PADDING = 15

    def __init__(
        self,
        game,
        data=None,
        layer="foreground",
        bg_color=(30, 30, 30),
        previous_state=None,
    ):
        super().__init__(game, data, layer, bg_color, previous_state)

        # Get dead cards from data
        self.cards = data.get("cards", []) if data else []
        self.cards_go = [
            create_card_controller(self.game, card, self, bg_image="BG2.png")
            for card in self.cards
        ]

        # Title label
        self.title_label = Label(
            self.canvas,
            x=game.GAME_W * 0.25,
            y=20,
            width=game.GAME_W * 0.5,
            text="Graveyard",
            fg_color=pygame.Color("white"),
            font=self.game.get_font("ant", 60),
        )

        # Back button
        self.go_back_btn = create_back_button(
            game,
            self.canvas,
            (game.GAME_W * 0.9, 30),
        )

        # Calculate scaled card dimensions
        self.scaled_card_size = CARD_DIMENSIONS * self.CARD_SCALE

        # Position cards in grid
        self._position_cards()

    def _position_cards(self):
        """Position all cards in a grid layout"""
        # Calculate grid starting position (centered)
        grid_width = (
            self.COLUMNS * self.scaled_card_size.x
            + (self.COLUMNS - 1) * self.CARD_PADDING
        )
        start_x = (self.game.GAME_W - grid_width) / 2 + self.scaled_card_size.x / 2
        start_y = 120 + self.scaled_card_size.y / 2

        for i, card in enumerate(self.cards_go):
            col = i % self.COLUMNS
            row = i // self.COLUMNS

            x = start_x + col * (self.scaled_card_size.x + self.CARD_PADDING)
            y = start_y + row * (self.scaled_card_size.y + self.CARD_PADDING)

            # Scale card down
            if hasattr(card, "base_sprite"):
                current_scale = card.base_sprite.transform.scale
                if current_scale != self.CARD_SCALE:
                    card.base_sprite.scale_by(self.CARD_SCALE / current_scale)
                    if hasattr(card, "art_sprite"):
                        card.art_sprite.scale_by(self.CARD_SCALE / current_scale)

            card.move(pygame.Vector2(x, y))

    def render(self, surface):
        super().render(surface)

        # Render cards
        for card in self.cards_go:
            card.render(surface)

            # Draw red border around enemy cards
            if (
                hasattr(card, "card_model")
                and card.card_model
                and card.card_model.owner == PlayerType.OP
            ):
                if hasattr(card, "base_sprite") and card.base_sprite:
                    enemy_rect = card.base_sprite.rect.inflate(8, 8)
                    pygame.draw.rect(
                        surface, (255, 50, 50), enemy_rect, 3, border_radius=5
                    )

    def update(self, delta):
        super().update(delta)
        for card in self.cards_go:
            card.update(delta)
