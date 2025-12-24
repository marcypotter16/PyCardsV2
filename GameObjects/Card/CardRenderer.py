import os
import moderngl
from numpy import array
from pygame import Surface, image
import pygame as p
from Game import Game
from GameObjects.Card.Card import CardControllerBase


# Vertex shader that supports positioning via uniforms
CARD_VERT_SRC = """
#version 330

in vec2 in_pos;
in vec2 in_uv;

uniform vec2 scale;
uniform vec2 translate;

out vec2 v_uv;

void main() {
    v_uv = in_uv;
    vec2 pos = in_pos * scale + translate;
    gl_Position = vec4(pos, 0.0, 1.0);
}
"""

# Buff shader with sheen effect
file = open(os.path.join(os.getcwd(), "buff_frag.glsl"), "r")
BUFF_FRAG_SRC = file.read()
file.close()


class CardRenderer:
    """Renders cards with optional GPU effects like buff sheen.

    Two-phase rendering:
    1. draw_all() - renders normal cards to pygame surface, collects buff cards
    2. render_gpu_effects() - renders buff effects via OpenGL (call after main canvas render)
    """

    def __init__(self, game: Game):
        self.game = game
        self.queue: list[tuple[int, CardControllerBase]] = []  # (z, card)
        self._buff_queue: list[CardControllerBase] = []  # Cards needing GPU effects

        # Create buff shader program with positioning support
        self.buff_program = game.glctx.program(
            vertex_shader=CARD_VERT_SRC,
            fragment_shader=BUFF_FRAG_SRC,
        )

        # Create quad VBO and VAO for card rendering
        self.card_vbo = self._create_quad_vbo()
        self.card_vao = game.glctx.simple_vertex_array(
            self.buff_program, self.card_vbo, "in_pos", "in_uv"
        )

        # Reusable texture for card rendering (will be resized as needed)
        self._card_texture = None
        self._card_surface = None

    def _create_quad_vbo(self):
        """Create a unit quad centered at origin."""
        vertices = array(
            [
                # x,    y,   u,   v
                -0.5,
                -0.5,
                0.0,
                0.0,
                0.5,
                -0.5,
                1.0,
                0.0,
                -0.5,
                0.5,
                0.0,
                1.0,
                0.5,
                0.5,
                1.0,
                1.0,
            ],
            dtype="f4",
        )
        return self.game.glctx.buffer(vertices.tobytes())

    def _get_card_texture(self, width: int, height: int):
        """Get or create a texture of the required size."""
        if self._card_texture is None or self._card_texture.size != (width, height):
            if self._card_texture is not None:
                self._card_texture.release()
            self._card_texture = self.game.glctx.texture((width, height), 4)
            self._card_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            self._card_surface = p.Surface((width, height), p.SRCALPHA)
        return self._card_texture, self._card_surface

    def submit_list(self, card_list: list[CardControllerBase]):
        self.queue.extend([(c.z_index, c) for c in card_list])

    def submit(self, card: CardControllerBase, force_top: bool = False):
        """Add a card to the render queue."""
        z = card.z_index
        if force_top:
            z = 10_000
        self.queue.append((z, card))

    def draw_all(self, dest_surface: Surface):
        """Draw all queued cards to pygame surface, queue buff cards for GPU rendering.

        Normal cards are rendered immediately to dest_surface.
        Buff cards are rendered to dest_surface AND queued for GPU effects
        (call render_gpu_effects() after main canvas is uploaded to GPU).
        """
        self._buff_queue.clear()

        for _, card in sorted(self.queue, key=lambda x: x[0]):
            # Always render to pygame surface first
            card.render(dest_surface)

            # Queue buff cards for GPU effect overlay
            if card.buff_in_progress:
                self._buff_queue.append(card)

        self.queue.clear()

    def render_gpu_effects(self):
        """Render GPU effects (buff sheen) for queued cards.

        Call this AFTER the main game canvas has been uploaded and rendered,
        but BEFORE pygame.display.flip().
        """
        for card in self._buff_queue:
            self._render_buff_effect(card)
        self._buff_queue.clear()

    def _render_buff_effect(self, card: CardControllerBase):
        """Render the buff sheen effect for a single card via OpenGL."""
        if card.rect is None:
            return

        w, h = int(card.rect.width), int(card.rect.height)
        if w <= 0 or h <= 0:
            return

        # Get/create appropriately sized texture and surface
        tex, temp_surface = self._get_card_texture(w, h)
        temp_surface.fill((0, 0, 0, 0))  # Clear with transparency

        # Create a larger surface to render the card at its actual position
        # then extract just the card's region
        card_rect = card.rect.copy()

        # We need to render the card with an offset so it appears in our temp surface
        # Blit the card to temp_surface by rendering to a translation surface
        # TODO we are creating a surface as big as the game canvas just to draw the card, but for now this is not meaningful for performance
        render_surface = p.Surface((self.game.GAME_W, self.game.GAME_H), p.SRCALPHA)
        render_surface.fill((0, 0, 0, 0))

        # Render card at its actual position
        card.render(render_surface)

        # Extract just the card's rect region
        temp_surface.blit(render_surface, (0, 0), area=card_rect)

        # Upload to texture (flip Y for OpenGL)
        tex.write(image.tobytes(temp_surface, "RGBA", True))

        # Calculate NDC position and scale
        x, y = card_rect.center
        sx = w / self.game.GAME_W * 2
        sy = h / self.game.GAME_H * 2
        px = (x / self.game.GAME_W) * 2 - 1
        py = 1 - (y / self.game.GAME_H) * 2

        # Set shader uniforms (normalize time to 0-1 range)
        normalized_time = (
            card.buff_time / card.buff_duration if card.buff_duration > 0 else 0
        )
        self.buff_program["time"].value = normalized_time
        self.buff_program["intensity"].value = 1.0
        self.buff_program["scale"].value = (sx, sy)
        self.buff_program["translate"].value = (px, py)

        # Draw with buff effect
        tex.use(0)
        self.card_vao.render(moderngl.TRIANGLE_STRIP)

    def cleanup(self):
        """Release GPU resources."""
        if self._card_texture is not None:
            self._card_texture.release()
            self._card_texture = None
