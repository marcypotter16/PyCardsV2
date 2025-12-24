from GameObjects.Card.Card import Card, CardTag
from GameObjects.Card.SpellCard import SpellCard
from GameObjects.Card.ChangeStructureCard import ChangeStructureCard
from GameObjects.EffectContext import EffectContext
from Constants import ART_PATH
import os

from GameObjects.MathRing import (
    ISOMORPHISMS,
    MODULI,
    AutomorphismGroup,
    Ring,
    Rings,
    Zn,
)
from PModels import PlayerType

# print(ART_PATH)


def mvn_on_play(ctx: EffectContext):
    """Maire von Neumann: Boosts nearby cards on play"""
    # Get all cards in adjacent slots
    neighbour_cards = ctx.get_neighbour_cards()

    # Boost each neighbouring card by 1
    for card in neighbour_cards:
        new_power = card.current_power + 1
        card.change_power(new_power)


def mvn_trigger(ctx: EffectContext):
    """Maire von Neumann: Boosts self by 1 when a HUMAN card is played adjacent to her"""
    # Check if a card was just played (target_card exists)
    if not ctx.target_card:
        return

    # Check if the newly played card is a HUMAN
    if CardTag.HUMAN not in ctx.target_card.card_model.tags:
        return

    # ctx.row, ctx.col represent the newly played card's position
    # Get neighbors of the newly played card
    neighbour_cards = ctx.get_neighbour_cards()

    # If MvN (source_card) is adjacent to the newly played HUMAN, boost MvN
    if ctx.source_card in neighbour_cards:
        new_power = ctx.source_card.current_power + 1
        ctx.source_card.change_power(new_power)
        ctx.source_card.current_power = (
            new_power  # Also update CardController's current_power
        )


def plus_1_on_play(ctx: EffectContext):
    # print(ctx.game_manager.structure, isinstance(ctx.game_manager.structure, Zn))
    if isinstance(ctx.game_manager.structure.structure, Zn):
        ctx.game_manager.structure.set_structure(
            Zn(ctx.game_manager.structure.structure.n + 1),
            color=ctx.game_manager.structure.color,
        )


def frobenius_on_play(ctx: EffectContext):
    if (
        ctx.game_manager.structure.is_finite_ring()
        and ctx.game_manager.structure.is_domain()
    ):
        ctx.source_card.change_power(ctx.source_card.current_power * 2)


def frobenius_trigger(ctx: EffectContext):
    pass


def galois_on_play(ctx: EffectContext):
    ctx.game_manager.structure.set_structure(
        AutomorphismGroup(ctx.game_manager.structure.structure),
        color=ctx.game_manager.structure.color,
    )


def iso_on_play(ctx: EffectContext):
    # print(
    #     ctx.game_manager.structure.structure,
    #     ISOMORPHISMS.keys(),
    #     ctx.game_manager.structure.structure in ISOMORPHISMS.keys(),
    # )
    if ctx.game_manager.structure.structure in ISOMORPHISMS.keys():
        ctx.game_manager.structure.set_structure(
            ISOMORPHISMS[ctx.game_manager.structure.structure],
            color=ctx.game_manager.structure.color,
        )


def frob_first_student_on_turn_end(ctx: EffectContext):
    if (
        ctx.game_manager.structure.is_finite_ring()
        and ctx.game_manager.structure.is_domain()
        and ctx.game_manager.active_player == PlayerType.ME
    ):
        ctx.source_card.change_power(ctx.source_card.current_power + 1)


def cantor_on_play(ctx: EffectContext):
    if ctx.game_manager.structure.is_infinite():
        ctx.game_manager.hand_me.add_controller(ctx.game_manager.deck_me.draw_card())


CARD_DATABASE = {
    "goth_girl": Card(
        "Maire von Neumann",
        os.path.join(ART_PATH, "GothGirl-removebg-preview.png"),
        [CardTag.HUMAN],
        effects={"on_play": [mvn_on_play], "trigger": [mvn_trigger]},
        description="Boosts self by 1 whenever a human is played in an adjacent tile, also boosts by 1 nearby cards on play",
        base_power=5,
    ),
    # "times_x": SpellCard(
    #     "times x",
    #     art_path="times_x.png",
    #     tags=[CardTag.SPELL, CardTag.SCIENCE],
    #     description="If present, multiplies quotienting polynomial by x",
    # ),
    "plus_1": SpellCard(
        "+1",
        art_path="plus_1.png",
        tags=[CardTag.SPELL, CardTag.SCIENCE],
        description="If present, adds 1 to the modulus (e.g. Z2 becomes Z3)",
        effects={"on_play": [plus_1_on_play]},
    ),
    "Z": ChangeStructureCard(Ring(Rings.Z)),
    "Q": ChangeStructureCard(Ring(Rings.Q)),
    "frobenius": Card(
        "Frobenius",
        os.path.join(ART_PATH, "Frobenius1.png"),
        tags=[CardTag.HUMAN, CardTag.SCIENCE],
        effects={"on_play": [frobenius_on_play], "trigger": [frobenius_trigger]},
        description="When played doubles its power, if the Current Active Structure is a Ring and its Frobenius endomorphism is injective. (TBI) If this card is in the field (TBC in any place) and the Active Structure is changed to a Domain, gain 1 power. If it gets changed to a non Domain lose 1.",
        base_power=6,
    ),
    "galois": Card(
        "Galois",
        os.path.join(ART_PATH, "Galois.png"),
        tags=[CardTag.HUMAN, CardTag.SCIENCE],
        effects={"on_play": [galois_on_play]},
        description="Change the Current Active Structure R to Aut(R), its group of group automorphisms (if R is a Ring or a Field we still consider Group morphism). (HANDLE WITH CARE)",
        base_power=1,
    ),
    "frobenius_first_student": Card(
        "Frobenius First Student",
        None,
        tags=[CardTag.HUMAN, CardTag.SCIENCE],
        effects={"on_turn_end": [frob_first_student_on_turn_end]},
        description="Gains 1 power at the end of your turn if the current active structure is a finite ring and its Frobenius endomorphism is injective",
        base_power=2,
    ),
    "cantor": Card(
        "Cantor",
        None,
        tags=[CardTag.HUMAN, CardTag.SCIENCE],
        effects={"on_play": [cantor_on_play]},
        description="If the current active structure is infinite, draw a card",
        base_power=3,
    ),
    "isomorphism": SpellCard(
        "≅",
        None,
        effects={"on_play": [iso_on_play]},
        description="If possible use a canonical isomorphism to change the current active structure",
    ),
}
for i in MODULI:
    CARD_DATABASE[f"Z{i}"] = ChangeStructureCard(Zn(i))


DECK_DATABASE = {"base_deck": [{"Maire von Neumann": 10}]}


if __name__ == "__main__":
    """
    Test the effect system with two adjacent Maire von Neumann cards.
    Expected behavior:
    - First MvN played at (1, 1): power = 5 (no neighbors)
    - Second MvN played at (1, 2):
      - Triggers on_play -> boosts first MvN by 1 -> first MvN = 6
      - Triggers first MvN's trigger -> first MvN sees adjacent HUMAN -> first MvN = 7
      - Second MvN stays at 5
    Final: First MvN = 7, Second MvN = 5
    """
    print("Testing Maire von Neumann effect system...\n")

    # Need to create a minimal Game mock for testing
    from unittest.mock import MagicMock
    from GameObjects.Board import Board
    from GameObjects.Card.Card import UnitCardController

    # Initialize pygame for font rendering
    import pygame

    pygame.init()

    # Create mock game object with real font
    mock_game = MagicMock()
    mock_game.SCREEN_CENTER = (400, 300)

    # Create a real font for rendering
    mock_font = pygame.font.Font(None, 24)
    mock_game.fonts = {"javier_skull": {"small": mock_font}}

    # Create board
    board = Board(mock_game)
    print(f"Board created: {board.n_rows}x{board.n_cols}")

    # Create two MvN card controllers
    mvn_card = CARD_DATABASE["goth_girl"]

    card1 = UnitCardController(mock_game)
    card1.from_card(mvn_card)
    print(
        f"Card 1 created: {card1.name}, base_power={card1.base_power}, current_power={card1.current_power}"
    )

    card2 = UnitCardController(mock_game)
    card2.from_card(mvn_card)
    print(
        f"Card 2 created: {card2.name}, base_power={card2.base_power}, current_power={card2.current_power}\n"
    )

    # Mock game state - can be None since our effects don't actually use it
    mock_game_state = None

    # Play first card at (1, 1)
    print("=== Playing Card 1 at (1, 1) ===")
    row1, col1 = 1, 1
    board.play_card(card1, row1, col1)

    # Trigger on_play effect for card1
    ctx1 = EffectContext(
        game_state=mock_game_state,
        source_card=card1,
        board=board,
        row=row1,
        col=col1,
        trigger="on_play",
    )

    if mvn_card.effects.get("on_play"):
        for effect in mvn_card.effects["on_play"]:
            effect(ctx1)

    print(
        f"Card 1 power after on_play: {card1.current_power} (expected: 5, no neighbors)\n"
    )

    # Play second card at (1, 2) - adjacent to first
    print("=== Playing Card 2 at (1, 2) - adjacent to Card 1 ===")
    row2, col2 = 1, 2
    board.play_card(card2, row2, col2)

    # Trigger on_play effect for card2 (should boost card1)
    ctx2 = EffectContext(
        game_state=mock_game_state,
        source_card=card2,
        board=board,
        row=row2,
        col=col2,
        trigger="on_play",
    )

    if mvn_card.effects.get("on_play"):
        for effect in mvn_card.effects["on_play"]:
            effect(ctx2)

    print(f"Card 1 power after Card 2 on_play: {card1.current_power} (expected: 6)")
    print(f"Card 2 power after on_play: {card2.current_power} (expected: 5)\n")

    # Trigger card1's trigger effect (card1 should see adjacent HUMAN)
    print("=== Triggering Card 1's trigger (seeing adjacent HUMAN) ===")
    for existing_card in board.cards:
        if existing_card != card2 and existing_card.card_model.effects.get("trigger"):
            trigger_ctx = EffectContext(
                game_state=mock_game_state,
                source_card=existing_card,
                board=board,
                row=row2,  # Position of newly played card
                col=col2,
                trigger="trigger",
                target_card=card2,
            )
            for effect in existing_card.card_model.effects["trigger"]:
                effect(trigger_ctx)

    print(f"Card 1 power after trigger: {card1.current_power} (expected: 7)")
    print(f"Card 2 power final: {card2.current_power} (expected: 5)\n")

    # Final results
    print("=== FINAL RESULTS ===")
    print(
        f"Card 1 (played first at {row1},{col1}): {card1.current_power} (expected: 7)"
    )
    print(
        f"Card 2 (played second at {row2},{col2}): {card2.current_power} (expected: 5)"
    )

    if card1.current_power == 7 and card2.current_power == 5:
        print("\n[PASS] TEST PASSED!")
    else:
        print("\n[FAIL] TEST FAILED!")
