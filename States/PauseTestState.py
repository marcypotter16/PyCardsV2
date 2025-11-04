import os
import pygame
from Constants import ART_PATH
from States.State import State
from Utils.Draw import draw_rect_alpha


class PauseTestState(State):
    def __init__(self, game, data: object | None = None, layer="foreground"):
        super().__init__(game, msg, layer)
        self.paused = False
        self.img = pygame.image.load(os.path.join(ART_PATH, "SacAltar.png"))
        self.blur_rect = pygame.Rect(0, 0, self.game.SCREEN_W, self.game.SCREEN_H)

    def toggle_blur_rect(self):
        self.paused = not self.paused

    def update(self, delta_time):
        super().update(delta_time)
        if self.game.clicked_sx == -1:
            print(f"Paused: {self.paused}")
            self.toggle_blur_rect()

    def render(self, surface):
        super().render(surface)
        surface.blit(self.img, self.blur_rect)
        if self.paused:
            draw_rect_alpha(surface, (50, 50, 100, 120), self.blur_rect)
