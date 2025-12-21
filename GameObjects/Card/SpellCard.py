import os
from typing import Callable, Dict, List
import pygame as p
from Constants import ART_PATH, CARD_DIMENSIONS, CARD_TWEEN_DUR
from GameObjects.Card.Card import BaseCard, CardControllerBase, CardTag
from GameObjects.EffectContext import EffectContext
from GameObjects.SpriteRenderer import SpriteRenderer
from PModels import PlayerType


class SpellCard(BaseCard):
    """A spell card with art but no power value"""

    def __init__(
        self,
        name: str,
        art_path: str,
        tags: List[CardTag] = [],
        effects: Dict[str, List[Callable[["EffectContext"], None]]] = {},
        description: str = "",
        owner: str = PlayerType.ME,
    ):
        super().__init__(name, tags, effects, description, owner)
        self.art_path = art_path


class SpellCardController(CardControllerBase):
    def __init__(
        self, game, parent=None, bg_image="BG2.png", card_model=None, font_family="stix"
    ):
        super().__init__(game, parent, card_model, font_family)

        # Load the background image for the spell card
        bg_path = os.path.join(ART_PATH, bg_image)
        self.base_sprite: SpriteRenderer = SpriteRenderer(
            self, bg_path, CARD_DIMENSIONS
        )

        # Text rendering surfaces and sprites
        self.name_text_surf = None
        self.name_text_sprite = None
        self.description_text_surf = None
        self.description_text_sprite = None

        # Track last rendered scale to detect changes
        self.last_text_scale = 1.0
        # Flag to prevent update() from re-rendering during active tweens
        self._is_tweening = False

        self.base_sprite.setup_mb(True, 3)
        self.base_sprite.TWEEN_DUR = CARD_TWEEN_DUR
        self.rect = self.base_sprite.rect
        self.sep_rect = None

    def from_card(self, card: SpellCard):
        """Initialize spell card from SpellCard data model"""
        self.card_model = card
        self.name = card.name
        self.description = card.description

        # Initial text rendering at scale 1.0
        self._render_text_at_scale(1.0)

    def _render_text_at_scale(self, scale: float):
        """Render or re-render text at a specific scale for crisp quality

        Args:
            scale: The scale factor to render text at
        """
        # Target width for name (75% of card width at this scale)
        target_name_width = CARD_DIMENSIONS.x * 0.75 * scale

        # Use centralized render_text method for perfect sizing
        self.name_text_surf = self.game.render_text(
            self.name,
            font_name=self.font_family,
            color=(0, 0, 0),
            target_width=int(target_name_width),
            base_font_size=int(30 * scale),
        )

        name_sprite_dimensions = self.name_text_surf.get_size()

        # Create or update name sprite
        if self.name_text_sprite is None:
            self.name_text_sprite = SpriteRenderer(
                self,
                self.name_text_surf,
                dimensions=name_sprite_dimensions,
            )
            self.name_text_sprite.TWEEN_DUR = CARD_TWEEN_DUR
        else:
            # Update existing sprite
            self.name_text_sprite.set_sprite(self.name_text_surf)
            self.name_text_sprite.set_dim(name_sprite_dimensions)

        # Position name at top of card (both for initial creation and updates)
        name_offset = p.Vector2(0, -CARD_DIMENSIONS.y * 0.3 * scale)
        self.name_text_sprite.move(self.transform.position + name_offset)

        # Target width for description (70% of card width at this scale)
        target_desc_width = CARD_DIMENSIONS.x * 0.7 * scale

        # Use centralized render_multiline_text method
        self.description_text_surf = self.game.render_multiline_text(
            self.description,
            font_name=self.font_family,
            color=(0, 0, 0),
            max_width=int(target_desc_width),
            base_font_size=int(5 * scale),
        )

        # Use actual surface size - no rescaling needed!
        desc_sprite_dimensions = self.description_text_surf.get_size()

        # Create or update description sprite
        if self.description_text_sprite is None:
            self.description_text_sprite = SpriteRenderer(
                self,
                self.description_text_surf,
                dimensions=desc_sprite_dimensions,
            )
            self.description_text_sprite.TWEEN_DUR = CARD_TWEEN_DUR
        else:
            # Update existing sprite
            self.description_text_sprite.set_sprite(self.description_text_surf)
            self.description_text_sprite.set_dim(desc_sprite_dimensions)

        # Position description below the name (both for initial creation and updates)
        self.sep_rect = p.Rect(
            self.name_text_sprite.rect.bottomleft,
            (self.name_text_sprite.dimensions[0], 2),
        )
        desc_offset = p.Vector2(0, self.name_text_sprite.dimensions[1] * 0.5)
        self.description_text_sprite.move(self.sep_rect.center + desc_offset)

        # Update last rendered scale
        self.last_text_scale = scale

    def update(self, delta):
        super().update(delta)

        # Don't re-render during active tweens
        if self._is_tweening:
            # Check if tween is done by seeing if scale has reached target
            # (tween manager may have killed our tween)
            return

        # Check if scale has changed significantly - if so, re-render text for quality
        current_scale = self.transform.scale
        scale_diff = abs(current_scale - self.last_text_scale)

        # Re-render if scale changed by more than 0.1 (prevents constant re-rendering)
        if scale_diff > 0.1:
            self._render_text_at_scale(current_scale)

    # TODO: unstable method!
    def tween_scale_to(self, new_scale, target_card_position=None):
        """Tweens the scale value from the current to the desired one

        Args:
            new_scale: The target scale factor
            target_card_position: The position the card will be at after scaling/moving
        """
        if target_card_position is None:
            target_card_position = self.transform.position

        # Mark as tweening, will be cleared when scale stabilizes
        self._is_tweening = True
        self._target_scale = new_scale

        def on_tween_done():
            self._is_tweening = False
            # Re-render text at final scale for crisp quality
            self._render_text_at_scale(self.transform.scale)

        self.game.tweener_manager.add_tween(
            self.transform,
            "scale",
            to_=new_scale,
            duration=CARD_TWEEN_DUR,
            on_finish=on_tween_done,
        )
        self.base_sprite.tween_scale_to(new_scale)

        # Calculate scale ratio for sprite scaling
        scale_ratio = (
            new_scale / self.last_text_scale if self.last_text_scale != 0 else new_scale
        )

        # Calculate and tween text sprite positions
        if self.name_text_sprite is not None:
            # Calculate target position for name text
            name_offset = p.Vector2(0, -CARD_DIMENSIONS.y * 0.3 * new_scale)
            name_target = target_card_position + name_offset
            self.name_text_sprite.tween_pos(name_target)
            self.name_text_sprite.tween_scale_to(scale_ratio)

        if (
            self.description_text_sprite is not None
            and self.name_text_sprite is not None
        ):
            # Calculate target position for description (below name)
            name_offset = p.Vector2(0, -CARD_DIMENSIONS.y * 0.3 * new_scale)
            name_target = target_card_position + name_offset
            # Estimate description position based on scaled name dimensions
            scaled_name_height = self.name_text_sprite.dimensions[1] * scale_ratio
            desc_offset = p.Vector2(0, scaled_name_height * 1.5)
            desc_target = name_target + desc_offset
            self.description_text_sprite.tween_pos(desc_target)
            self.description_text_sprite.tween_scale_to(scale_ratio)

    def render(self, surface):
        super().render(surface)
        if self.sep_rect:
            p.draw.rect(
                surface=surface,
                rect=self.sep_rect,
                color=(0, 0, 0),
                border_radius=1,
            )
