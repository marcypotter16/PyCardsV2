import pygame
from pygame import Rect

from Game import Game
from Collections.Stack import Stack
from GameObjects.GameObject import GameObject
from GameObjects.SpriteRenderer import SpriteRenderer
from UI.Abstract import UICanvas
from UI.Label import Label
from Utils.Text import draw_centered_text
from Utils.Colors import BLACK


class State:
    def __init__(
        self,
        game: Game,
        data: object | None = None,
        layer="foreground",
        bg_color=BLACK,
        previous_state=None,
    ):
        """@param data: gets passed by the parent State"""
        self.game = game
        self.canvas: UICanvas = UICanvas(game)
        self.debug_label = Label(
            self.canvas,
            self.game.GAME_W * 0.85,
            0,
            width=self.game.GAME_W * 0.15,
            height=self.game.GAME_H,
            fg_color=(255, 255, 255),
        )
        self.bg_color = bg_color
        self.render_stack = Stack()
        # self.prev_state = None
        self.data = data
        self.layer = layer
        self.keep_previous_state_updating = previous_state is not None
        if previous_state is not None:
            self.prev_state = previous_state
        # self.cursor_sprite = pygame.Surface(
        #     (21, 21), pygame.BLEND_RGBA_MULT
        # ).convert_alpha()
        # pygame.draw.circle(
        #     self.cursor_sprite,
        #     pygame.Color("white"),
        #     self.cursor_sprite.get_rect().center,
        #     10,
        # )
        # self.cursor_go = GameObject(game)
        # self.cursor_sr = SpriteRenderer(self.cursor_go, self.cursor_sprite)

    def render(self, surface: pygame.Surface):
        surface.fill(self.bg_color)
        self.canvas.render(surface)
        # if not self.game.settings.MOUSE_VISIBLE:
        #     self.cursor_sr.render(surface)
        # if self.data is not None:
        #     draw_centered_text(
        #         self.game.fonts["comfortaa"]["big"],
        #         surface,
        #         self.data,
        #         (255, 255, 255),
        #         rect=Rect(0, 0, self.game.GAME_W, self.game.GAME_H // 2),
        #     )

    def update(self, delta_time):
        self.canvas.update(delta_time)
        if self.keep_previous_state_updating:
            self.prev_state.update(delta_time)
        # if not self.game.settings.MOUSE_VISIBLE:
        #     self.cursor_go.move(self.game.cursorpos)

    def enter_state(self):
        """Aggiunge lo stato allo stack di stati del gioco"""
        if self.game.state_stack.size() > 1:
            self.prev_state = (
                self.game.state_stack.top()
            )  # ossia l'ultimo elemento dello stack di stati
        self.game.state_stack.push(self)
        self.game.render_stack[self.layer].append(self.render)

    def exit_state(self):
        """Rimuove lo stato dallo stack di stati del gioco"""
        self.game.state_stack.pop()

    def change_layer(self, layer):
        self.game.render_stack[self.layer].remove(self.render)
        self.layer = layer
        self.game.render_stack[self.layer].append(self.render)

    def change_render_index_in_layer(self, index):
        self.game.render_stack[self.layer].remove(self.render)
        self.game.render_stack[self.layer].insert(index, self.render)

    def set_above_all(self):
        self.game.render_stack[self.layer].remove(self.render)
        self.layer = "above_all"
        self.game.render_stack["above_all"].append(self.render)

    def debug_print(self, msg: str):
        self.debug_label.set_text(msg)
