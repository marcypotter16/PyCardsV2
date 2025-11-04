import pygame.font
import pygame.freetype
from pygame import draw


def draw_text(font: pygame.font.Font | pygame.freetype.Font, surface: pygame.Surface, text: str,
              color: tuple = (255, 255, 255), x: int = 0, y: int = 0):
    """
    Draws text. Works with both pygame.font.Font and pygame.freetype.Font
    :param font: The font used (pygame.font.Font or pygame.freetype.Font).
    :param surface: The surface to write on (pygame surface)
    :param text: The text.
    :param color: The color
    :param x: X of the topleft corner of the text
    :param y: Y of the topleft corner of the text
    :return:
    """
    if isinstance(font, pygame.freetype.Font):
        # Use freetype rendering without antialiasing for crisp pixel fonts
        font.render_to(surface, (x, y), str(text), color, None, pygame.freetype.STYLE_DEFAULT)
    else:
        # Use standard pygame font rendering without antialiasing
        text_surface = font.render(str(text), False, color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x, y)
        surface.blit(text_surface, text_rect)


def draw_centered_text(font: pygame.font.Font | pygame.freetype.Font, surface: pygame.Surface, text: str, color: tuple, rect: pygame.Rect):
    """
    Draws text centered in a rect. Works with both pygame.font.Font and pygame.freetype.Font
    :param font: The font used (pygame.font.Font or pygame.freetype.Font).
    :param surface: The surface to write on (pygame surface)
    :param text: The text.
    :param color: The color
    :param rect: The rect to center text in
    :return:
    """
    if isinstance(font, pygame.freetype.Font):
        # Use freetype rendering without antialiasing for crisp pixel fonts
        text_rect = font.get_rect(text)
        text_rect.center = rect.center
        font.render_to(surface, text_rect.topleft, text, color, None, pygame.freetype.STYLE_DEFAULT)
    else:
        # Use standard pygame font rendering without antialiasing
        text_surface = font.render(text, False, color)
        text_rect = text_surface.get_rect()
        text_rect.center = rect.center
        surface.blit(text_surface, text_rect)


def draw_text_hq(font_path: str, size: int, surface: pygame.Surface, text: str,
                 color: tuple, x: int, y: int, centered: bool = False):
    """
    Draws high-quality text using pygame.freetype (better antialiasing).
    :param font_path: Path to the font file
    :param size: Font size
    :param surface: The surface to write on
    :param text: The text to render
    :param color: The color
    :param x: X position
    :param y: Y position
    :param centered: Whether to center the text at (x, y)
    :return:
    """
    ft_font = pygame.freetype.Font(font_path, size)
    if centered:
        text_rect = ft_font.get_rect(text)
        text_rect.center = (x, y)
        ft_font.render_to(surface, text_rect.topleft, text, color)
    else:
        ft_font.render_to(surface, (x, y), text, color)


def draw_number_with_circle_background(font: pygame.font.Font | pygame.freetype.Font, surface: pygame.Surface, number: str,
                                       bg_color: tuple, fg_color: tuple, x: int, y: int):
    """
    Draws a number with a circle background.
    :param font: The font used.
    :param surface: The surface to write on (pygame surface)
    :param number: The number.
    :param bg_color: The color of the background
    :param fg_color: The color of the number
    :param x: X of the center of the rectangle containing the text
    :param y: Y of the center of the rectangle containing the text
    :return:
    """
    if isinstance(font, pygame.freetype.Font):
        text_rect = font.get_rect(number)
        draw.circle(surface, bg_color, (x + text_rect.width * .5, y + text_rect.height * .5), 10)
    else:
        draw.circle(surface, bg_color, (x + font.size(number)[0] * .5, y + font.size(number)[1] * .5), 10)
    draw_text(font, surface, str(number), fg_color, x, y)
