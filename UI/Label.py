import pygame

from UI.Abstract import UIElement, UICanvas
from Utils.Text import draw_centered_text


class Label(UIElement):
    def __init__(self, parent: UICanvas = None, x=0, y=0, center=None, width=None, height=None,
                 font: pygame.font.Font = None, bg_color: tuple | str = "transparent",
                 fg_color=(0, 0, 0), text: str = "", corner_radius=10):
        super().__init__(parent, x, y, center, width if width is not None else 0, height if height is not None else 0,
                         bg_color, fg_color, font, text, corner_radius)

        if font is None:
            self.font = self.game.fonts["comfortaa"]["small"]
        else:
            self.font = font

        if width is None:
            self.width = self.rect.width = self.font.size(self.text)[0] + 20
        else:
            self.width = self.rect.width = width
        if height is None:
            self.height = self.rect.height = self.font.size(self.text)[1] + 20
        else:    
            self.height = self.rect.height = height

        

    def render(self, surface: pygame.Surface):
        super().render(surface)
        draw_centered_text(self.font, surface,
                           self.text, self.fg_color, self.rect)
