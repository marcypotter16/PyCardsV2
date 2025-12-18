from enum import StrEnum
import os

import pygame
from Constants import ART_PATH, CARD_TWEEN_DUR
from Game import Game
from GameObjects.GameObject import GameObject
from GameObjects.SpriteRenderer import SpriteRenderer
from Utils.Colors import WHITE
from Utils.Image import surf_from_svg


class Ring(StrEnum):
    Q = "QQ"
    Z = "ZZ"
    R = "RR"
    C = "CC"
    F = "FF"
    Fq = "FFq"
    Zxmod = "ZZ[x]/"


class PolyRingQuotient:
    def __init__(self, base_ring: Ring, quotient_poly: str):
        self.base_ring = base_ring
        self.quotient_poly = quotient_poly


class Zn:
    def __init__(self, n: int):
        self.n = n

    def __str__(self):
        return f"Z/{self.n}Z"


ring2sprite = {
    Ring.Q: pygame.image.load(os.path.join(ART_PATH, "Q.png")),
    Ring.Z: pygame.image.load(os.path.join(ART_PATH, "Z.png")),
    Ring.R: pygame.image.load(os.path.join(ART_PATH, "R.png")),
    Ring.F: pygame.image.load(os.path.join(ART_PATH, "F.png")),
    # Ring.Q: os.path.join(ART_PATH, "Q.png"),
    # Ring.Q: os.path.join(ART_PATH, "Q.png"),
}
quotring2sprite = {
    Ring.Q: pygame.image.load(os.path.join(ART_PATH, "Q[x]mod.png")),
    Ring.R: pygame.image.load(os.path.join(ART_PATH, "R[x]mod.png")),
    Ring.C: pygame.image.load(os.path.join(ART_PATH, "C[x]mod.png")),
    Ring.Z: pygame.image.load(os.path.join(ART_PATH, "Z[x]mod.png")),
    Ring.F: pygame.image.load(os.path.join(ART_PATH, "F[x]mod.png")),
    Ring.Fq: pygame.image.load(os.path.join(ART_PATH, "Fq[x]mod.png")),
}

poly_dict = {
    "x": pygame.image.load(os.path.join(ART_PATH, "x.png")),
    "+": pygame.image.load(os.path.join(ART_PATH, "plus.png")),
    "-": pygame.image.load(os.path.join(ART_PATH, "minus.png")),
}


def render_univariate_poly(
    poly: str,
    game: Game,
    font_group: str = "ant",
    add_parens: bool = False,
    target_height: int | None = None,
    scale_factor: float = 1.0,
):
    """Render a univariate polynomial string as a pygame surface

    Example: "x^2+3x-5" would render with images for x, +, -, and digits

    :param poly: The polynomial string to render
    :param game: The game object (used to access fonts)
    :param font_group: The font family to use for rendering numbers
    :param add_parens: If True, wraps the polynomial in parentheses (e.g., for ideals)
    :param target_height: Desired height of the polynomial in pixels (scales everything proportionally)
    :param scale_factor: Additional scale factor to apply (1.0 = normal, 0.5 = half size, etc.)
    :return: A pygame surface with the rendered polynomial
    """
    # Get reference height from the 'x' image to scale fonts appropriately
    base_image_height = poly_dict["x"].get_height()

    # If target_height is specified, calculate scale to achieve it
    if target_height is not None:
        # Target height refers to the overall polynomial height
        # We scale everything to achieve this
        scale_factor = target_height / (base_image_height * 1.25)

    ref_image_height = base_image_height * 1.25 * scale_factor

    # Normal font should match the image height
    normal_font_size = int(ref_image_height * 1)
    exponent_font_size = int(normal_font_size * 0.6)  # Exponents are 60% of normal size

    # Create fonts at appropriate sizes using game's font system
    normal_font = game.get_font(font_group, normal_font_size)
    exponent_font = game.get_font(font_group, exponent_font_size)

    surfaces = []
    x = 0
    height_padding = 0.2 * ref_image_height * 0.5
    baseline_y = (
        ref_image_height + height_padding * 0.5
    )  # Baseline for normal characters
    max_height = 0
    is_superscript = False

    # Add opening parenthesis if requested
    if add_parens:
        open_paren = normal_font.render("(", True, pygame.Color("black"))
        y_offset = baseline_y - open_paren.get_height()
        surfaces.append((open_paren, x, y_offset))
        x += open_paren.get_width()
        max_height = max(max_height, y_offset + open_paren.get_height())

    for char in poly:
        surf = None
        y_offset = 0

        if char in poly_dict:
            surf = poly_dict[char]
            # Scale the image if needed
            if scale_factor != 1.0:
                new_size = (
                    int(surf.get_width() * scale_factor),
                    int(surf.get_height() * scale_factor),
                )
                surf = pygame.transform.smoothscale(surf, new_size)
            # Align image to baseline
            y_offset = baseline_y - surf.get_height()
            surfaces.append((surf, x, y_offset))
            x += surf.get_width()
            is_superscript = False

        elif char == "^":
            # Next character will be superscript
            is_superscript = True
            continue  # Don't render the ^ itself

        elif char.isdigit():
            if is_superscript:
                surf = exponent_font.render(char, True, pygame.Color("black"))
                # Position exponent higher and to the right
                y_offset = height_padding * 0.5
            else:
                surf = normal_font.render(char, True, pygame.Color("black"))
                # Align to baseline
                y_offset = baseline_y - surf.get_height() * 0.8

            surfaces.append((surf, x, y_offset))
            x += surf.get_width()
            is_superscript = False

        elif char == " ":
            # Add spacing
            x += 10
            is_superscript = False

        # Track maximum height
        if surf:
            max_height = max(max_height, y_offset + surf.get_height())

    # Add closing parenthesis if requested
    if add_parens:
        close_paren = normal_font.render(")", True, pygame.Color("black"))
        y_offset = baseline_y - close_paren.get_height()
        surfaces.append((close_paren, x, y_offset))
        x += close_paren.get_width()
        max_height = max(max_height, y_offset + close_paren.get_height())

    if not surfaces:
        # Return empty surface if no valid characters
        return pygame.Surface((1, 1), pygame.SRCALPHA)

    # Calculate total dimensions with some padding
    total_width = x
    total_height = max(max_height, baseline_y) + ref_image_height * 0.2

    # Create the final surface
    surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))  # Transparent background

    # Blit all surfaces onto the final surface
    for surf, surf_x, surf_y in surfaces:
        surface.blit(surf, (surf_x, surf_y))

    return surface


class RingController(GameObject):
    def __init__(self, game, parent=None, initial_scale=0.5):
        super().__init__(game, parent)
        self.ring: Ring | PolyRingQuotient | Zn = None
        # Load Q.png at original size to avoid scaling artifacts
        q_img = pygame.image.load(os.path.join(ART_PATH, "Q.png"))
        original_size = q_img.get_size()
        self.ring_sprite = SpriteRenderer(
            self, os.path.join(ART_PATH, "Q.png"), original_size
        )
        self.ring_sprite.change_tint((255, 255, 255))
        self.ring_sprite.TWEEN_DUR = CARD_TWEEN_DUR
        # Create child sprite with a 1x1 transparent placeholder initially
        self.quotient_poly_sprite = SpriteRenderer(self.ring_sprite)
        self.quotient_poly_sprite.set_visible(False)
        self.quotient_poly_sprite.TWEEN_DUR = CARD_TWEEN_DUR
        self.n_sprite = SpriteRenderer(self.ring_sprite)
        self.n_sprite.set_visible(False)
        self.n_sprite.TWEEN_DUR = CARD_TWEEN_DUR
        self.used_font = None
        self.color = pygame.Color("black")

        # Scale down the ring to fit better on cards
        if initial_scale != 1.0:
            self.transform.scale_by(initial_scale)
            self.scale_by(initial_scale)

    def set_color(self, new_color: pygame.Color):
        self.color = new_color
        self.set_ring(self.ring, self.used_font, self.color)

    def set_ring(
        self,
        new_ring: Ring | PolyRingQuotient | Zn,
        font_family="ant",
        color: pygame.Color = pygame.Color("black"),
        scale: bool = False,
    ):
        self.ring = new_ring
        self.used_font = font_family
        if isinstance(new_ring, Ring):
            self.ring_sprite.set_sprite_no_scale(ring2sprite[new_ring])
            self.ring_sprite.change_tint(color)
            # Hide the quotient polynomial sprite for simple rings
            self.quotient_poly_sprite.set_visible(False)
            self.n_sprite.set_visible(False)

        elif isinstance(new_ring, PolyRingQuotient):
            self.ring_sprite.set_sprite_no_scale(quotring2sprite[new_ring.base_ring])

            # Calculate desired height for the polynomial (50% of ring sprite height)
            desired_poly_height = int(self.ring_sprite.dimensions[1] * 0.5)

            poly_surf = render_univariate_poly(
                new_ring.quotient_poly,
                self.game,
                font_family,
                add_parens=True,
                target_height=desired_poly_height,
            )
            self.quotient_poly_sprite.set_sprite_no_scale(poly_surf)
            self.quotient_poly_sprite.set_visible(True)
            self.quotient_poly_sprite.change_tint(color)

            # Position the polynomial to the right of the ring symbol
            ring_width = self.ring_sprite.dimensions[0]
            poly_width = poly_surf.get_width()

            # Calculate position relative to parent's current position
            # Place it to the right of the ring
            offset_x = ring_width / 2 + poly_width / 2 - 5
            absolute_pos = self.ring_sprite.transform.position + pygame.Vector2(
                offset_x, 20
            )

            self.quotient_poly_sprite.move(absolute_pos)
            self.n_sprite.set_visible(False)

        elif isinstance(new_ring, Zn):
            self.ring_sprite.set_sprite_no_scale(ring2sprite[Ring.Z])
            self.ring_sprite.apply_scale()  # Apply scale first so dimensions are correct
            self.quotient_poly_sprite.set_visible(False)
            self.n_sprite.set_visible(True)

            # Calculate subscript font size (about 60% of ring height)
            ring_height = self.ring_sprite.dimensions[1]
            subscript_font_size = int(max(10, ring_height * 0.5))

            # Render the subscript
            n_surf = self.game.get_font(font_family, subscript_font_size).render(
                str(new_ring.n), True, color
            )
            self.n_sprite.set_sprite_no_scale(n_surf)

            # Position subscript: bottom-right of the Z, slightly offset
            ring_width = self.ring_sprite.dimensions[0]
            n_width = n_surf.get_width()

            # Calculate position relative to ring sprite center
            # Use ratios so it works at any scale
            offset_x = ring_width * 0.5 + n_width / 2  # Position to the right
            offset_y = ring_height * 0.4  # Subscript position (below center)

            absolute_pos = self.ring_sprite.transform.position + pygame.Vector2(
                offset_x, offset_y
            )
            self.n_sprite.move(absolute_pos)
        # if color != self.color:
        self.ring_sprite.change_tint(color)
        # Reapply current scale after setting sprite
        self.ring_sprite.apply_scale()

    def scale_by(self, factor):
        super().scale_by(factor)
        self.set_ring(
            self.ring,
            self.used_font if self.used_font is not None else "ant",
            self.color,
        )

    def tween_scale_to(self, new_scale, target_position=None):
        """Tween the scale of the ring to match card scaling

        Args:
            new_scale: The target scale factor
            target_position: Optional target position for the ring. If None, uses current position.
        """
        if target_position is None:
            target_position = self.ring_sprite.transform.position

        # Tween the main ring sprite scale and position
        self.ring_sprite.tween_scale_to(new_scale)
        self.ring_sprite.tween_pos(target_position)

        # Calculate scale ratio to determine new child positions
        current_scale = self.transform.scale
        if current_scale == 0:
            current_scale = 0.001  # Avoid division by zero
        scale_ratio = new_scale / current_scale

        # Update transform scale (for future calculations)
        self.game.tweener_manager.add_tween(
            self.transform,
            "scale",
            to_=new_scale,
            duration=self.ring_sprite.TWEEN_DUR,
        )

        # Handle child sprites based on ring type
        if isinstance(self.ring, Zn) and self.n_sprite.is_visible:
            # Calculate new position for n_sprite relative to ring
            current_offset = self.n_sprite.transform.position - self.ring_sprite.transform.position
            new_offset = current_offset * scale_ratio
            new_n_pos = target_position + new_offset
            self.n_sprite.tween_pos(new_n_pos)
            # Scale the n_sprite font by tweening (we'll re-render at final scale)
            self.n_sprite.tween_scale_to(scale_ratio)

        elif isinstance(self.ring, PolyRingQuotient) and self.quotient_poly_sprite.is_visible:
            # Calculate new position for quotient poly sprite
            current_offset = self.quotient_poly_sprite.transform.position - self.ring_sprite.transform.position
            new_offset = current_offset * scale_ratio
            new_poly_pos = target_position + new_offset
            self.quotient_poly_sprite.tween_pos(new_poly_pos)
            self.quotient_poly_sprite.tween_scale_to(scale_ratio)
