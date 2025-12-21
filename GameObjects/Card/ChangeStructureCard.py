import os
import pygame as p
from Constants import ART_PATH, CARD_DIMENSIONS, CARD_TWEEN_DUR
from GameObjects.Card.Card import (
    BaseCard,
    CardControllerBase,
    CardTag,
)
from GameObjects.EffectContext import EffectContext
from GameObjects.MathRing import (
    AlgebraicStructure,
    AutomorphismGroup,
    Rings,
    StructureController,
    UnitsGroup,
    Zn,
)
from GameObjects.SpriteRenderer import SpriteRenderer
from PModels import PlayerType


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
        new_pos = p.Vector2(new_pos)
        self.base_sprite.tween_pos(new_pos)
        self.base_sprite.tween_scale_to(new_scale)

        # Calculate structure's target position based on card's target position
        scaled_structure_offset = self.structure_offset * new_scale
        structure_target_pos = new_pos + scaled_structure_offset
        self.structure_controller.tween_scale_to(
            new_scale * self.initial_structure_scale,
            target_position=structure_target_pos,
        )
