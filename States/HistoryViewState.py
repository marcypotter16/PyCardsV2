import os
import pygame
from Constants import UI_PATH
from States.State import State
from UI.Button import ImageButton
from UI.Label import Label
from Utils.Draw import create_back_button


class HistoryViewState(State):
    def __init__(self, game, data=None, layer="foreground", bg_color=(0, 0, 0)):
        super().__init__(game, data, layer, bg_color)
        self.lab_title = Label(
            self.canvas,
            x=game.GAME_W * 0.25,
            y=20,
            width=game.GAME_W * 0.5,
            text="History",
            fg_color=pygame.Color("white"),
            font=self.game.get_font("ant", 100),
        )
        # Format history into human-readable text
        history = data.get("history", [])
        if history:
            formatted_history = "\n".join(
                event.to_readable_string() for event in history
            )
        else:
            formatted_history = "No events yet"

        self.label = Label(
            self.canvas,
            x=game.GAME_W * 0.25,
            y=150,
            width=game.GAME_W * 0.5,
            text=formatted_history,
            fg_color=pygame.Color("white"),
            font=self.game.get_font("ant", 20),
        )

        self.go_back_btn = create_back_button(
            game,
            self.canvas,
            (
                game.GAME_W * 0.85,
                20,
            ),
        )
