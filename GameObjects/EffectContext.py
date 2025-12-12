from dataclasses import dataclass
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from GameObjects.Card import CardController
    from GameObjects.Board import Board
    from GameObjects.Slot import SlotController
    from PModels import GameState


@dataclass
class EffectContext:
    """
    Context object passed to card effects containing all information they might need.
    Effects can use whichever fields are relevant to them.
    """

    game_state: "GameState"
    source_card: "CardController"
    board: "Board"

    # Position-related (for on_play, positional effects)
    row: Optional[int] = None
    col: Optional[int] = None
    slot: Optional["SlotController"] = None

    # Neighbors (computed on demand or passed in)
    neighbours: Optional[List["SlotController"]] = None

    # Target-related (for targeted effects, combat)
    target_card: Optional["CardController"] = None
    target_cards: Optional[List["CardController"]] = None

    # Additional context
    trigger: Optional[str] = None  # e.g., "on_play", "on_death", "on_turn_start"

    def get_neighbours(self) -> List["SlotController"]:
        """Lazily compute neighbours if row/col are set."""
        if self.neighbours is not None:
            return self.neighbours

        if self.row is not None and self.col is not None and self.board is not None:
            self.neighbours = self.board.get_neighbours(self.row, self.col)
            return self.neighbours

        return []

    def get_neighbour_cards(self) -> List["CardController"]:
        """Get all cards in neighbouring slots."""
        neighbour_cards = []
        for slot in self.get_neighbours():
            if slot.content is not None:
                neighbour_cards.append(slot.content)
        return neighbour_cards
