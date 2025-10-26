import pygame

from UI.Abstract import UIElement, UICanvas
from Utils.Text import draw_centered_text


class TextButton(UIElement):
    def __init__(
        self,
        parent: UICanvas = None,
        x=0,
        y=0,
        center=None,
        width=100,
        height=100,
        bg_color: tuple | str = (50, 50, 50),
        fg_color=(0, 0, 0),
        text: str = "",
        font: pygame.font.Font | None = None,
        corner_radius=10,
        command=lambda: print("Clicked"),
        hover_color=(150, 150, 150),
    ):
        super().__init__(
            parent, x, y, center, width, height, bg_color, fg_color, font, text, corner_radius
        )
        self.font = self.game.fonts["comfortaa"]["medium"] if font is None else font
        self.hover_color = hover_color
        self.height = self.font.get_height() + 10
        self.command = None
        if callable(command):
            self.command = command

    def update(self, dt):
        if self.visible:
            if self.rect.collidepoint(self.game.mousepos):
                self.hover(dt)
                # == -1 perchè voglio che il bottone sia cliccato quando rilasci il bottone del mouse
                if self.game.clicked_sx == -1:
                    self.clicked()
            else:
                self.unhover()

    def hover(self, dt):
        self.bg_color = self.hover_color

    def unhover(self):
        self.bg_color = self.original_bg_color

    def clicked(self):
        if self.command is not None:
            self.command.__call__()

    def render(self, surface: pygame.Surface):
        if self.visible:
            super().render(surface)
            # x = int(self.x + .5 * self.width)
            # y = int(self.y + self.height * .5)
            # x, y = self.x, self.y
            if self.text != "":
                draw_centered_text(
                    self.font, surface, self.text, self.fg_color, self.rect
                )


class ImageButton(TextButton):
    def __init__(
        self,
        parent: UICanvas = None,
        x=0,
        y=0,
        center=None,
        width=100,
        height=100,
        bg_color: tuple | str = "transparent",
        fg_color=(0, 0, 0),
        text: str = "",
        font: pygame.font.Font | None = None,
        corner_radius=10,
        command=lambda: print("Clicked"),
        hover_color=(150, 150, 150),
        hover_animation: list[pygame.Surface] = None,
        mouse_pressed_image: pygame.Surface = None,
        animation_fps: int = 60,
    ):

        super().__init__(
            parent,
            x,
            y,
            center,
            width,
            height,
            bg_color,
            fg_color,
            text,
            font,
            corner_radius,
            command,
            hover_color,
        )
        # self.animation = [pygame.transform.scale(image, self.rect.size) for image in hover_animation]
        self.animation = hover_animation

        if mouse_pressed_image is not None:
            self.mouse_pressed_image = pygame.transform.scale(
                mouse_pressed_image, self.rect.size
            )
        else:
            self.mouse_pressed_image = self.animation[0]

        self.current_image_index: int = 0
        self.current_image: pygame.image = self.animation[0]
        self.animation_list_length: int = len(hover_animation)
        self.prev_timestamp: float = 0
        self._MS_BETWEEN_ANIMATION_FRAMES: float = self.game.fps / animation_fps
        # dt = 1 / fps => se voglio avere 5 frames al secondo, supponendo di avere 60 fps => dt = 0.016, allora
        # 5 frames al secondo vuol dire far passare 60/5 * dt = 12 * dt secondi.
        # Quindi _S_BETWEEN_ANIMATION_FRAMES = self.game.fps / animation_fps.

    def update(self, dt):
        # print(self.current_image_index)
        if self.rect.collidepoint(self.game.mousepos):
            if self.game.actions["mouse_sx"]:
                self.current_image = self.mouse_pressed_image
            elif self.game.clicked_sx == -1:
                self.command.__call__()
            else:
                self.hover(dt)
        else:
            self.unhover()
        if self.game.clicked_sx == -1 and not self.rect.collidepoint(
            self.game.mousepos
        ):
            self.current_image = self.animation[0]
            self.current_image_index = 0

    def hover(self, dt):
        self.prev_timestamp += dt
        if self.prev_timestamp >= self._MS_BETWEEN_ANIMATION_FRAMES * dt:
            self.current_image_index = (
                self.current_image_index + 1
            ) % self.animation_list_length
            self.current_image = self.animation[self.current_image_index]
            self.prev_timestamp = 0
        self.bg_color = self.hover_color
        # if self.game.clicked_sx == -1:
        #     self.command.__call__()

    def unhover(self):
        """
        Resets the animation
        :return:
        """
        self.current_image_index = 0
        self.bg_color = self.original_bg_color

    def render(self, surface: pygame.Surface):
        if self.visible:
            super().render(surface)
            surface.blit(self.current_image, self.rect)
