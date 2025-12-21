from enum import StrEnum
import os
from typing import Callable, Dict, List, Optional, Set, TYPE_CHECKING

# from GameObjects.EffectContext import EffectContext
import uuid
from Constants import (
    ART_PATH,
    CARD_ART_SIZE_RATIO,
    CARD_BACK_PATH,
    CARD_BASE_PATH_1,
    CARD_BASE_PATH_2,
    CARD_DIMENSIONS,
    CARD_TWEEN_DUR,
)

# from GameObjects.Database import CARD_DATABASE
from GameObjects.GameObject import GameObject
from GameObjects.MathRing import (
    AlgebraicStructure,
    AutomorphismGroup,
    Rings,
    StructureController,
    UnitsGroup,
    Zn,
)
from PModels import EventKind, PHistoryEvent, PlayerType
from GameObjects.SpriteRenderer import SpriteRenderer
import math
import pygame as p

from PModels import PCardModel

if TYPE_CHECKING:
    from GameObjects.EffectContext import EffectContext


class CardTag(StrEnum):
    SCIENCE = "science"
    HUMAN = "human"
    ELEMENT = "element"
    NOBLE = "noble"
    SPELL = "spell"
    CHANGE_RING = "change_ring"


class BaseCard:
    """Base class for all card data models"""

    def __init__(
        self,
        name: str,
        tags: List[CardTag] = [],
        effects: Dict[str, List[Callable[["EffectContext"], None]]] = {},
        description: str = "",
        owner: str = PlayerType.ME,
    ):
        self.name = name
        self.tags: Set[CardTag] = set(tags)
        self.effects = effects
        self.description = description
        self.owner = owner


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


def on_change_structure_card_play(ctx: "EffectContext"):
    ctx.game_state.active_structure = ctx.source_card.card_model.structure
    ctx.game_manager.structure.set_structure(
        ctx.source_card.card_model.structure, color=ctx.game_manager.structure.color
    )


class ChangeStructureCard(BaseCard):
    """A card that changes the active algebraic structure"""

    def __init__(self, structure: AlgebraicStructure, owner: str = PlayerType.ME):
        # Generate name based on structure type
        if isinstance(structure, Rings):
            name = structure.value.name
        elif isinstance(structure, Zn):
            name = f"Z{structure.n}"
        elif isinstance(structure, UnitsGroup):
            name = f"U({structure.base_ring})"
        elif isinstance(structure, AutomorphismGroup):
            name = f"Aut({structure.base_structure})"
        else:
            name = str(structure)

        # Generate description
        ops = structure.get_operations()
        ops_str = ", ".join(ops) if ops else "no operations"
        description = f"Changes active structure to {structure} ({ops_str})"

        super().__init__(
            name=name,
            tags=[CardTag.CHANGE_RING],
            effects={"on_play": [on_change_structure_card_play]},
            description=description,
            owner=owner,
        )
        self.structure = structure


class Card(SpellCard):
    """A unit card with art and a power value"""

    def __init__(
        self,
        name,
        art_path,
        tags=[],
        effects={},
        description="",
        base_power=0,
        owner: str = PlayerType.ME,
    ):
        super().__init__(name, art_path, tags, effects, description, owner)
        self.base_power = base_power


class CardControllerBase(GameObject):
    """Base class for all card controllers (regular cards and spell cards)"""

    def __init__(self, game, parent=None, card_model: BaseCard | None = None):
        super().__init__(game, parent)
        self.last_saved_pos = self.transform.position.copy()
        self.hovered = False
        self.owner: str = PlayerType.ME
        self.uid: str = str(uuid.uuid4())
        self.dead: bool = False
        self.banished: bool = False
        self.card_model: BaseCard = card_model
        self.name = ""
        self.base_sprite = None
        self.rect = None

    def from_card(self, card):
        """Override in subclasses"""
        raise NotImplementedError("from_card must be implemented by subclass")

    def tween_pos(self, pos, drop=True, on_finish=None):
        # print(f"[tween_pos] {self.name}: to {pos}, drop={drop}, on_finish={on_finish}")

        for c in self.children:
            # Skip children that manage their own position (e.g., power_text_sprite)
            if self._should_skip_child_tween(c):
                continue
            c.tween_pos(c.transform.position + pos - self.transform.position)

        def _on_finish_wrapper():
            # print(f"[tween_pos] {self.name}: _on_finish_wrapper called!")
            if drop:
                self.drop()
            if on_finish:
                # print(f"[tween_pos] {self.name}: calling user on_finish")
                on_finish()

        self.game.tweener_manager.add_tween(
            self.transform,
            "position",
            to_=p.Vector2(pos),
            on_finish=_on_finish_wrapper,
            duration=CARD_TWEEN_DUR,
        )

    def _should_skip_child_tween(self, child):
        """Override in subclasses to skip specific children during position tweening"""
        return False

    def snap_back(self):
        self.tween_pos(self.last_saved_pos)

    def to_pydantic(self) -> PCardModel:
        """Convert this CardController to a PCardModel for serialization"""
        return PCardModel(
            uid=self.uid,
            name=self.name,
            description=self.card_model.description,
            tags=[str(tag) for tag in self.card_model.tags],
            owner=self.owner,
            dead=self.dead,
            banished=self.banished,
        )

    def drop(self):
        self.last_saved_pos = p.Vector2(self.transform.position)

    def tween_scale_to(self, new_scale, target_card_position=None):
        """Override in subclasses for custom scaling behavior"""
        raise NotImplementedError("tween_scale_to must be implemented by subclass")

    def tween_pos_and_scale(self, new_pos, new_scale, drop=True, on_finish=None):
        """Override in subclasses for custom scaling behavior"""
        new_pos = p.Vector2(new_pos)

        def _on_finish_wrapper():
            if drop:
                self.drop()
            if on_finish:
                on_finish()

        self.game.tweener_manager.add_tween(
            self.transform,
            "position",
            to_=new_pos,
            duration=CARD_TWEEN_DUR,
            on_finish=_on_finish_wrapper,
        )
        self.game.tweener_manager.add_tween(
            self.transform,
            "scale",
            to_=new_scale,
            duration=CARD_TWEEN_DUR,
        )


class CardController(CardControllerBase):
    # Diamond size as ratio of card width
    DIAMOND_SIZE_RATIO = 0.35

    def __init__(self, game, parent=None, card_model: BaseCard | None = None):
        super().__init__(game, parent, card_model)

        # Full art - same dimensions as card
        self.art_sprite = SpriteRenderer(self)
        self.art_sprite.set_dim(CARD_DIMENSIONS)

        # Diamond sprite for power background (bottom-right corner)
        diamond_size = int(CARD_DIMENSIONS.x * self.DIAMOND_SIZE_RATIO)
        self.diamond_offset = p.Vector2(
            CARD_DIMENSIONS.x * 0.35, CARD_DIMENSIONS.y * 0.35  # Right side  # Bottom
        )
        diamond_path = os.path.join(ART_PATH, "diamond.png")
        self.diamond_sprite = SpriteRenderer(
            self, diamond_path, (diamond_size, diamond_size)
        )

        # Power text centered on diamond
        self.power_text_font_size = 20
        self.power_text_surf = self.game.get_font(
            "ant", self.power_text_font_size
        ).render("0", False, p.Color(255, 255, 255))
        self.power_text_offset = self.diamond_offset  # Same position as diamond
        self.power_text_sprite = SpriteRenderer(
            self, self.power_text_surf, scale_img_to_dim=False
        )
        self.power_text_sprite.move(self.power_text_offset)
        self.diamond_sprite.move(self.diamond_offset)

        for c in self.children:
            c.TWEEN_DUR = CARD_TWEEN_DUR

        self.back_sprite: SpriteRenderer = SpriteRenderer(
            self, CARD_BACK_PATH, CARD_DIMENSIONS
        )
        self.back_sprite.set_visible(False)
        self.art_sprite.setup_mb(True, 3)

        self.face_up = True
        self.rect = p.Rect((0, 0), CARD_DIMENSIONS)
        self.rect.center = self.transform.position
        self.current_power: int = 0  # Will be set when from_card is called
        self.base_power: int = 0

    # Move is already inherited from GameObject

    def to_pydantic(self) -> PCardModel:
        """Convert this CardController to a PCardModel for serialization"""
        return PCardModel(
            uid=self.uid,
            name=self.name,
            base_power=self.base_power,
            current_power=self.current_power,
            description=self.card_model.description,
            tags=[str(tag) for tag in self.card_model.tags],
            owner=self.owner,
            dead=self.dead,
            banished=self.banished,
        )

    def _should_skip_child_tween(self, child):
        """Skip sprites with custom offsets during position tweening - their positions are managed separately"""
        return child in (self.power_text_sprite, self.diamond_sprite)

    def change_power(self, new_power: int):
        match True:
            case _ if new_power == self.base_power:
                color = p.Color(255, 255, 255)  # White
            case _ if new_power < self.base_power:
                color = p.Color(255, 0, 0)  # Red
            case _:
                color = p.Color(0, 255, 0)  # Green

        self.power_text_surf = self.game.get_font(
            "ant", self.power_text_font_size
        ).render(str(new_power), False, color)
        self.current_power = new_power
        self.card_model.current_power = new_power
        self.power_text_sprite.set_sprite_no_scale(self.power_text_surf)

    def flip(self):
        self.face_up = not self.face_up
        self.back_sprite.set_visible(not self.face_up)
        self.art_sprite.set_visible(self.face_up)
        # self.base_sprite.set_visible(self.face_up)

    def rotate(self, angle: float):
        super().rotate(angle)

    # def face_mouse(self):
    #     vec = self.game.cursorpos - self.base_sprite.position
    #     angle = -math.atan2(vec.y, vec.x)
    #     angle = math.degrees(angle)
    #     self.rotate(angle)

    def from_card(self, card: Card):
        """Initialize card from Card data model

        Args:
            card: The Card data to render
        """
        self.card_model = card
        self.name = card.name
        self.base_power = card.base_power
        self.current_power = card.base_power  # Initialize current_power to base_power

        # Set up full art sprite
        self.art_path = card.art_path
        if card.art_path is not None:
            self.art_sprite.set_sprite(p.image.load(self.art_path))
        else:
            placeholder = p.Surface((int(CARD_DIMENSIONS.x), int(CARD_DIMENSIONS.y)))
            placeholder_color = p.Color("pink")
            placeholder.fill(placeholder_color)
            self.art_sprite.set_sprite(placeholder)

        # Position diamond and power text
        self.diamond_sprite.move(self.transform.position + self.diamond_offset)
        self.change_power(card.base_power)
        self.power_text_sprite.move(self.transform.position + self.power_text_offset)

    def tween_pos(self, pos, drop=True, on_finish=None):
        super().tween_pos(pos, drop, on_finish)
        self.power_text_sprite.tween_pos(pos + self.power_text_offset)
        self.diamond_sprite.tween_pos(pos + self.diamond_offset)

    def tween_pos_and_scale(self, new_pos, new_scale: float, drop=True, on_finish=None):
        """Tween both position and scale together"""
        super().tween_pos_and_scale(new_pos, new_scale, drop, on_finish)
        new_pos = p.Vector2(new_pos)

        # Art sprite (full card, no offset)
        self.art_sprite.tween_pos(new_pos)
        self.art_sprite.tween_scale_to(new_scale)

        # Diamond with scaled offset
        scaled_diamond_offset = self.diamond_offset * new_scale
        self.diamond_sprite.tween_pos(new_pos + scaled_diamond_offset)
        self.diamond_sprite.tween_scale_to(new_scale)

        # Power text with scaled offset (same as diamond)
        scaled_power_offset = self.power_text_offset * new_scale
        self.power_text_sprite.tween_pos(new_pos + scaled_power_offset)

    def tween_scale_to(self, new_scale):
        """Tweens the scale value from the current to the desired one

        Args:
            new_scale: The target scale factor
        """
        self.game.tweener_manager.add_tween(
            self.transform,
            "scale",
            to_=new_scale,
            duration=CARD_TWEEN_DUR,
        )
        self.art_sprite.tween_scale_to(new_scale)

        # Diamond with scaled offset
        scaled_diamond_offset = self.diamond_offset * new_scale
        self.diamond_sprite.tween_pos(self.transform.position + scaled_diamond_offset)
        self.diamond_sprite.tween_scale_to(new_scale)

        # Power text with scaled offset
        scaled_power_offset = self.power_text_offset * new_scale
        self.power_text_sprite.tween_pos(self.transform.position + scaled_power_offset)

    def render(self, surface):
        p.draw.rect(surface, p.Color("white"), self.rect, width=1, border_radius=4)
        super().render(surface)
        # p.draw.circle(
        #     surface,
        #     p.Color("white"),
        #     self.power_text_sprite.rect.center,
        #     self.power_circle_radius,
        #     width=1,
        # )

    def update(self, delta):
        super().update(delta)
        self.rect.center = self.transform.position


class SpellCardController(CardControllerBase):
    def __init__(self, game, parent=None, bg_image="BG2.png"):
        super().__init__(game, parent)

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
            font_name="ant",
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
            font_name="ant",
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


class ChangeStructureCardController(CardControllerBase):
    def __init__(
        self,
        game,
        parent=None,
        bg_image="BG2.png",
        structure: AlgebraicStructure = None,
    ):
        """Controller for cards that change the active algebraic structure"""
        super().__init__(game, parent)
        # Load the background image for the card
        bg_path = os.path.join(ART_PATH, bg_image)
        self.base_sprite: SpriteRenderer = SpriteRenderer(
            self, bg_path, CARD_DIMENSIONS
        )
        self.initial_structure_scale = 1.0
        self.structure_controller = StructureController(
            game, self, initial_scale=self.initial_structure_scale
        )
        self.structure_offset = p.Vector2(0, -0.18 * CARD_DIMENSIONS[1])

        # Initialize with provided structure or default
        if structure is not None:
            self.from_card(ChangeStructureCard(structure))
        self.structure_controller.move(
            self.structure_controller.transform.position + self.structure_offset
        )

        self.base_sprite.setup_mb(True, 3)
        self.base_sprite.TWEEN_DUR = CARD_TWEEN_DUR
        self.rect = self.base_sprite.rect

    def from_card(self, card: ChangeStructureCard):
        """Initialize card from ChangeStructureCard data model"""
        self.card_model = card
        self.name = card.name
        self.description = card.description
        self.structure_controller.set_structure(card.structure)

    def tween_scale_to(self, new_scale, target_card_position=None):
        """Tweens the scale value from the current to the desired one

        Args:
            new_scale: The target scale factor
            target_card_position: The position the card will be at after scaling/moving
        """
        if target_card_position is None:
            target_card_position = self.transform.position

        self.game.tweener_manager.add_tween(
            self.transform,
            "scale",
            to_=new_scale,
            duration=CARD_TWEEN_DUR,
        )
        self.base_sprite.tween_scale_to(new_scale)

        # Calculate structure's target position based on card's target position
        scaled_structure_offset = self.structure_offset * new_scale
        structure_target_pos = target_card_position + scaled_structure_offset
        self.structure_controller.tween_scale_to(
            new_scale * self.initial_structure_scale,
            target_position=structure_target_pos,
        )

    def tween_pos_and_scale(self, new_pos, new_scale, drop=True, on_finish=None):
        super().tween_pos_and_scale(new_pos, new_scale, drop, on_finish)
        self.base_sprite.tween_pos(new_pos)
        self.base_sprite.tween_scale_to(new_scale)
        self.structure_controller.tween_pos(new_pos)
        self.structure_controller.tween_scale_to(new_scale)


def create_card_controller(
    game, card, parent=None, bg_image="GreenBG1.png"
) -> CardControllerBase:
    """Factory function to create the appropriate card controller based on card type

    Args:
        game: The game instance
        card: Card, SpellCard, or ChangeStructureCard data model
        parent: Optional parent GameObject
        bg_image: Background image for spell cards (default: GreenBG1.png)

    Returns:
        Appropriate CardController subclass for the card type
    """
    if isinstance(card, Card):
        controller = CardController(game, parent)
    elif isinstance(card, ChangeStructureCard):
        controller = ChangeStructureCardController(game, parent, bg_image)
    elif isinstance(card, SpellCard):
        controller = SpellCardController(game, parent, bg_image)
    else:
        raise ValueError(f"Unknown card type: {type(card)}")
    controller.from_card(card)
    return controller
