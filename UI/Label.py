import pygame

from UI.Abstract import UIElement, UICanvas
from Utils.Text import draw_centered_text


# TODO Refactor this entire file!
class Label(UIElement):
    def __init__(
        self,
        parent: UICanvas = None,
        x=0,
        y=0,
        center=None,
        width=None,
        height=None,
        font: pygame.font.Font = None,
        bg_color: tuple | str = "transparent",
        fg_color=(0, 0, 0),
        text: str = "",
        corner_radius=10,
        underline=False,
    ):
        super().__init__(
            parent,
            x,
            y,
            center,
            width if width is not None else 0,
            height if height is not None else 0,
            bg_color,
            fg_color,
            font,
            text,
            corner_radius,
        )
        self.underline = underline

        if font is None:
            self.font = self.game.fonts["comfortaa"]["small"]
        else:
            self.font = font

        # Auto-size the label based on text if width/height not provided
        if width is None:
            surf, rect = self.font.render(self.text if self.text else " ")
            self.width = self.rect.width = rect.width + 20
        else:
            self.width = self.rect.width = width

        if height is None:
            self.height = self.rect.height = self.font.get_sized_height() + 10
        else:
            self.height = self.rect.height = height

        # Update rect with new dimensions
        self.rect.update(self.x, self.y, self.width, self.height)

        if center is not None:
            self.rect.center = center
            self.x, self.y = self.rect.x, self.rect.y

    # def _wrap_text(self, text: str, max_width: int) -> list[str]:
    #     """
    #     Wraps text to fit within max_width, breaking at word boundaries.
    #     Returns a list of lines.
    #     """
    #     words = text.split(' ')
    #     lines = []
    #     current_line = []

    #     for word in words:
    #         # Try adding this word to the current line
    #         test_line = ' '.join(current_line + [word])
    #         text_width = self.font.get_rect(test_line).width

    #         if text_width <= max_width:
    #             # Word fits, add it to current line
    #             current_line.append(word)
    #         else:
    #             # Word doesn't fit
    #             if current_line:
    #                 # Save current line and start new one with this word
    #                 lines.append(' '.join(current_line))
    #                 current_line = [word]
    #             else:
    #                 # Single word is too long, add it anyway
    #                 lines.append(word)
    #                 current_line = []

    #     # Add remaining words
    #     if current_line:
    #         lines.append(' '.join(current_line))

    #     return lines if lines else ['']

    def render(self, surface: pygame.Surface):
        super().render(surface)

        # First split by explicit newlines
        paragraphs = self.text.split("\n")
        all_lines = paragraphs

        # Add some padding to prevent text from touching edges
        # max_width = self.rect.width - 10  # 5px padding on each side

        # # Process each paragraph with word wrap
        # for paragraph in paragraphs:
        #     if paragraph:  # Skip empty lines
        #         wrapped_lines = self._wrap_text(paragraph, max_width)
        #         all_lines.extend(wrapped_lines)
        #     else:
        #         all_lines.append('')  # Preserve empty lines from \n\n

        # If we have multiple lines, render them
        if len(all_lines) > 1 or "\n" in self.text:
            line_height = self.font.get_sized_height()
            total_height = line_height * len(all_lines)

            # Calculate starting Y position to center all lines vertically
            start_y = self.rect.centery - (total_height / 2)

            # Render each line
            for i, line in enumerate(all_lines):
                # Create a rect for this line
                line_rect = pygame.Rect(
                    self.rect.x,
                    start_y + (i * line_height),
                    self.rect.width,
                    line_height,
                )
                draw_centered_text(self.font, surface, line, self.fg_color, line_rect)
        else:
            # Single line text - check if it needs wrapping
            text_width = self.font.get_rect(self.text).width

            # if text_width > max_width:
            #     # Text is too long, wrap it
            #     wrapped_lines = self._wrap_text(self.text, max_width)
            #     line_height = self.font.get_sized_height()
            #     total_height = line_height * len(wrapped_lines)
            #     start_y = self.rect.centery - (total_height / 2)

            #     for i, line in enumerate(wrapped_lines):
            #         line_rect = pygame.Rect(
            #             self.rect.x,
            #             start_y + (i * line_height),
            #             self.rect.width,
            #             line_height,
            #         )
            #         draw_centered_text(
            #             self.font, surface, line, self.fg_color, line_rect
            #         )
            # else:
            #     # Text fits, render normally
            draw_centered_text(self.font, surface, self.text, self.fg_color, self.rect)

            if self.underline:
                pygame.draw.rect(
                    surface,
                    self.fg_color,
                    pygame.Rect(
                        self.rect.x - 10,
                        self.rect.bottom - 0.1 * self.rect.height + 6,
                        self.rect.w + 20,
                        self.rect.h * 0.1,
                    ),
                    border_radius=int(self.rect.h * 0.05),
                )
        pygame.draw.rect(surface, (255, 0, 0), self.rect, width=1)
