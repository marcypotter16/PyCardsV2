from enum import Enum, StrEnum
import math
import os

import pygame
from Constants import ART_PATH, CARD_TWEEN_DUR
from Game import Game
from GameObjects.GameObject import GameObject
from GameObjects.SpriteRenderer import SpriteRenderer


def is_prime(n: int):
    if n == 0 or n == 1:
        return False
    if n < 0:
        return is_prime(-n)
    if n <= 3:
        return True
    if n == 4:
        return False
    for i in range(2, int(n * 0.5)):
        if n % i == 0:
            return False
    return True


class AlgebraicStructure:
    # Operation symbols for display
    ADD_SYMBOL = "+"
    MUL_SYMBOL = "·"

    def __init__(self, name: str):
        self.name = name

    def has_addition(self) -> bool:
        return False

    def has_multiplication(self) -> bool:
        return False

    def get_operations(self) -> list[str]:
        """Returns list of operation symbols this structure supports"""
        ops = []
        if self.has_addition():
            ops.append(self.ADD_SYMBOL)
        if self.has_multiplication():
            ops.append(self.MUL_SYMBOL)
        return ops

    def get_display_string(self) -> str:
        """Returns formatted string: 'structure, op1, op2'"""
        ops = self.get_operations()
        if ops:
            return f"{self.name}, {', '.join(ops)}"
        return self.name

    def is_domain(self) -> bool:
        return False

    def __str__(self):
        return self.name


class AdditiveGroup(AlgebraicStructure):
    OPERATIONS = set("+")

    def has_addition(self) -> bool:
        return True

    def has_multiplication(self) -> bool:
        return False


class MultiplicativeGroup(AlgebraicStructure):
    OPERATIONS = set(".")

    def has_addition(self):
        return False

    def has_multiplication(self):
        return True


class Rings(StrEnum):
    Q = "QQ"
    Z = "ZZ"
    R = "RR"
    C = "CC"
    F = "FF"
    Fq = "FFq"


class Ring(AdditiveGroup):
    OPERATIONS = set(("+", "."))

    def __init__(self, ring: Rings):
        self.ring = ring

    def has_multiplication(self) -> bool:
        return True

    def is_domain(self) -> bool:
        return self.ring in (Rings.Z, Rings.Q)

    def is_field(self) -> bool:
        return self.name is Rings.Q

    @property
    def name(self):
        return RING_DISPLAY[self.ring]

    def __str__(self):
        return self.name


RING_DISPLAY = {
    Rings.Z: "ℤ",
    Rings.Q: "ℚ",
    Rings.R: "ℝ",
    Rings.C: "ℂ",
}


class Zn(Ring):
    def __init__(self, n: int):
        super().__init__(f"ℤ/{n}ℤ")
        self.n = n

    def is_domain(self) -> bool:
        return is_prime(self.n)

    def is_field(self) -> bool:
        return is_prime(self.n)

    def units(self) -> list[int]:
        return [i for i in range(self.n) if math.gcd(i, self.n) == 1]

    def __str__(self):
        return f"ℤ/{self.n}ℤ"


class UnitsGroup(MultiplicativeGroup):
    def __init__(self, ring: Ring):
        super().__init__(f"U({ring})")
        self.base_ring = ring
        self.elements = ring.units()


class AutomorphismGroup(MultiplicativeGroup):
    def __init__(self, structure: AlgebraicStructure):
        super().__init__(f"Aut({structure})")
        self.base_structure = structure

        if isinstance(structure, Zn):
            # Aut(Zn, +) ≅ U(Zn)
            self.elements = structure.units()
        else:
            self.elements = []


ring2sprite = {
    Rings.Q: pygame.image.load(os.path.join(ART_PATH, "Q.png")),
    Rings.Z: pygame.image.load(os.path.join(ART_PATH, "Z.png")),
    Rings.R: pygame.image.load(os.path.join(ART_PATH, "R.png")),
    Rings.F: pygame.image.load(os.path.join(ART_PATH, "F.png")),
}
quotring2sprite = {
    Rings.Q: pygame.image.load(os.path.join(ART_PATH, "Q[x]mod.png")),
    Rings.R: pygame.image.load(os.path.join(ART_PATH, "R[x]mod.png")),
    Rings.C: pygame.image.load(os.path.join(ART_PATH, "C[x]mod.png")),
    Rings.Z: pygame.image.load(os.path.join(ART_PATH, "Z[x]mod.png")),
    Rings.F: pygame.image.load(os.path.join(ART_PATH, "F[x]mod.png")),
    Rings.Fq: pygame.image.load(os.path.join(ART_PATH, "Fq[x]mod.png")),
}

poly_dict = {
    "x": pygame.image.load(os.path.join(ART_PATH, "x.png")),
    "+": pygame.image.load(os.path.join(ART_PATH, "plus.png")),
    "-": pygame.image.load(os.path.join(ART_PATH, "minus.png")),
}


def render_structure_with_ops(
    structure: AlgebraicStructure,
    game: Game,
    font_group: str = "stix",
    color: pygame.Color = pygame.Color("black"),
    font_size: int = 24,
    spacing: int = 8,
) -> pygame.Surface:
    """Render an algebraic structure with its operations.

    Renders in format: "structure, op1, op2" where ops are the available operations.
    For example: "U(Z/5Z), ·" or "ZZ, +, ·"

    Args:
        structure: The algebraic structure to render
        game: Game instance for font access
        font_group: Font family to use
        color: Text color
        font_size: Base font size
        spacing: Horizontal spacing between elements

    Returns:
        A pygame surface with the rendered structure and operations
    """
    font = game.get_font(font_group, font_size)

    # Get the display components
    structure_name = str(structure)
    operations = structure.get_operations()

    # Render structure name
    name_surf = font.render(structure_name, True, color)

    if not operations:
        return name_surf

    # Render comma and operations
    comma_surf = font.render(",", True, color)
    op_surfs = [font.render(op, True, color) for op in operations]

    # Calculate total width
    total_width = name_surf.get_width()
    total_width += comma_surf.get_width() + spacing  # First comma after name

    for i, op_surf in enumerate(op_surfs):
        total_width += op_surf.get_width()
        if i < len(op_surfs) - 1:
            total_width += comma_surf.get_width() + spacing  # Comma between ops

    # Get max height
    max_height = max(
        name_surf.get_height(),
        comma_surf.get_height(),
        max(s.get_height() for s in op_surfs) if op_surfs else 0,
    )

    # Create final surface
    surface = pygame.Surface((total_width, max_height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    # Blit elements
    x = 0

    # Structure name
    y = (max_height - name_surf.get_height()) // 2
    surface.blit(name_surf, (x, y))
    x += name_surf.get_width()

    # First comma
    y = (max_height - comma_surf.get_height()) // 2
    surface.blit(comma_surf, (x, y))
    x += comma_surf.get_width() + spacing

    # Operations with commas between them
    for i, op_surf in enumerate(op_surfs):
        y = (max_height - op_surf.get_height()) // 2
        surface.blit(op_surf, (x, y))
        x += op_surf.get_width()

        if i < len(op_surfs) - 1:
            y = (max_height - comma_surf.get_height()) // 2
            surface.blit(comma_surf, (x, y))
            x += comma_surf.get_width() + spacing

    return surface


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


class StructureController(GameObject):
    """Controller for rendering any AlgebraicStructure with its operations.

    Displays structure in format: "structure, op1, op2"
    For example: "U(Z/5Z), ·" or "ZZ, +, ·"
    """

    def __init__(self, game, parent=None, initial_scale=1.0):
        super().__init__(game, parent)
        self.structure: AlgebraicStructure = None
        self.used_font = "ant"
        self.color = pygame.Color("black")
        self.font_size = int(24 * initial_scale)

        # Main sprite for the entire structure display
        self.structure_sprite = SpriteRenderer(self)
        self.structure_sprite.TWEEN_DUR = CARD_TWEEN_DUR

        # Scale down to fit on cards
        if initial_scale != 1.0:
            self.transform.scale_by(initial_scale)

    def set_structure(
        self,
        structure: AlgebraicStructure,
        font_family: str = "stix",
        color: pygame.Color = pygame.Color("black"),
    ):
        """Set the algebraic structure to display.

        Args:
            structure: Any AlgebraicStructure (Ring, Zn, UnitsGroup, AutomorphismGroup, etc.)
            font_family: Font to use for rendering
            color: Text color
            font_size: Base font size
        """
        self.structure = structure
        self.used_font = font_family
        self.color = color

        # Render the structure with its operations
        surf = render_structure_with_ops(
            structure,
            self.game,
            font_group=font_family,
            color=color,
            font_size=self.font_size,
        )

        self.structure_sprite.set_sprite_no_scale(surf)
        self.structure_sprite.apply_scale()

    def is_domain(self) -> bool:
        return self.structure.is_domain()

    def set_color(self, new_color: pygame.Color):
        self.color = new_color
        if self.structure:
            self.set_structure(self.structure, self.used_font, new_color)

    def scale_by(self, factor):
        super().scale_by(factor)
        self.structure_sprite.scale_by(factor)

    def tween_pos(self, new_position):
        """Tween position of the structure"""
        super().tween_pos(new_position)
        self.structure_sprite.tween_pos(new_position)

    def tween_scale_to(self, new_scale, target_position=None):
        if target_position is None:
            target_position = self.structure_sprite.transform.position

        self.structure_sprite.tween_scale_to(new_scale)
        self.structure_sprite.tween_pos(target_position)

        self.game.tweener_manager.add_tween(
            self.transform,
            "scale",
            to_=new_scale,
            duration=self.structure_sprite.TWEEN_DUR,
        )


if __name__ == "__main__":
    # for i in range(20):
    #     print(f"{i}: {is_prime(i)}")
    z20 = Zn(20)
    print(z20.units())
    R = Ring(Rings.Z)

    print(R)  # ℤ
    print(R.is_domain())  # True
    print(R.is_field())  # False

    if R.ring is Rings.Z:
        print("Integers detected")
