from enum import StrEnum
import os
from typing import Callable, Dict, List, Set, TYPE_CHECKING

# from GameObjects.EffectContext import EffectContext
import uuid
from Constants import (
    ART_PATH,
    CARD_BACK_PATH,
    CARD_DIMENSIONS,
    CARD_TWEEN_DUR,
)

# from GameObjects.Database import CARD_DATABASE
from GameObjects.GameObject import GameObject
from PModels import PlayerType
from GameObjects.SpriteRenderer import SpriteRenderer
import pygame as p

from PModels import PCardModel

if TYPE_CHECKING:
    from GameObjects.EffectContext import EffectContext
    from .SpellCard import SpellCard
    from .ChangeStructureCard import ChangeStructureCard


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


class Card(BaseCard):
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
        super().__init__(
            name, tags=tags, effects=effects, description=description, owner=owner
        )
        self.art_path = art_path
        self.base_power = base_power


class CardControllerBase(GameObject):
    """Base class for all card controllers (regular cards and spell cards)"""

    def __init__(
        self, game, parent=None, card_model: BaseCard | None = None, font_family="stix"
    ):
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
        self.font_family = font_family

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

    def __init__(
        self, game, parent=None, card_model: BaseCard | None = None, font_family="stix"
    ):
        super().__init__(game, parent, card_model, font_family)

        # Full art - same dimensions as card
        self.art_sprite = SpriteRenderer(self)
        self.art_sprite.set_dim(CARD_DIMENSIONS)

        # Diamond sprite for power background (bottom-right corner)
        diamond_size = int(CARD_DIMENSIONS.x * self.DIAMOND_SIZE_RATIO)
        self.diamond_offset = p.Vector2(
            -CARD_DIMENSIONS.x * 0.45, -CARD_DIMENSIONS.y * 0.45  # Top Left
        )
        diamond_path = os.path.join(ART_PATH, "diamond.png")
        self.diamond_sprite = SpriteRenderer(
            self, diamond_path, (diamond_size, diamond_size)
        )

        # Power text centered on diamond
        self.base_power_text_font_size = 20  # Base font size at scale 1.0
        self.power_text_font_size = self.base_power_text_font_size
        self.power_text_surf = self.game.get_font(
            self.font_family, self.power_text_font_size
        ).render("0", True, p.Color(255, 255, 255))
        self.power_text_offset = self.diamond_offset  # Same position as diamond
        self.power_text_sprite = SpriteRenderer(
            self, self.power_text_surf, scale_img_to_dim=False
        )
        self.power_text_sprite.move(self.power_text_offset)
        self.diamond_sprite.move(self.diamond_offset)
        self.last_power_text_scale = 1.0  # Track scale for re-rendering
        self._power_color = p.Color(255, 255, 255)  # Track current power color

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

        self._power_color = color
        self.power_text_surf = self.game.get_font(
            self.font_family, self.power_text_font_size
        ).render(str(new_power), True, color)
        self.current_power = new_power
        self.card_model.current_power = new_power
        self.power_text_sprite.set_sprite_no_scale(self.power_text_surf)

    def _render_power_text_at_scale(self, scale: float):
        """Re-render power text at target scale for crisp quality"""
        self.power_text_font_size = int(self.base_power_text_font_size * scale)
        # Ensure minimum font size
        if self.power_text_font_size < 8:
            self.power_text_font_size = 8

        self.power_text_surf = self.game.get_font(
            self.font_family, self.power_text_font_size
        ).render(str(self.current_power), True, self._power_color)
        self.power_text_sprite.set_sprite_no_scale(self.power_text_surf)
        self.last_power_text_scale = scale

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

        def on_tween_done():
            # Re-render power text at final scale for crisp quality
            self._render_power_text_at_scale(new_scale)
            if on_finish:
                on_finish()

        super().tween_pos_and_scale(new_pos, new_scale, drop, on_tween_done)
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

        def on_scale_done():
            # Re-render power text at final scale for crisp quality
            self._render_power_text_at_scale(new_scale)

        self.game.tweener_manager.add_tween(
            self.transform,
            "scale",
            to_=new_scale,
            duration=CARD_TWEEN_DUR,
            on_finish=on_scale_done,
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
