import pygame
from pygame import Rect

from Game import Game
from Collections.Stack import Stack
from UI.Abstract import UICanvas
from Utils.Text import draw_centered_text
from Utils.Colors import BLACK


class State:
    def __init__(self, game: Game, data: object | None = None, layer="foreground"):
        """@param data: gets passed by the parent State"""
        self.game = game
        self.canvas: UICanvas = UICanvas(game)
        self.bg_color = BLACK
        self.render_stack = Stack()
        self.prev_state = None
        self.data = data
        self.layer = layer

    def render(self, surface: pygame.Surface):
        surface.fill(self.bg_color)
        self.canvas.render(surface)
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
