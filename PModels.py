from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel

from GameObjects.MathRing import Ring, Zn


class PCardModel(BaseModel):
    uid: str
    name: str
    base_power: Optional[int] = None  # Spell cards dont have that
    current_power: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    owner: str  # me or op
    dead: bool = False
    banished: bool = False


class Player(BaseModel):
    """Enhanced player model with game state"""

    player_id: str
    player_name: str
    hand: List[PCardModel] = []
    deck: List[PCardModel] = []
    gy: List[PCardModel] = []
    is_turn: bool = False


class PlayerType(StrEnum):
    ME = "me"
    OP = "op"


class EventKind(StrEnum):
    CARD_PLAYED_FROM_HAND = "card_played_from_hand"
    CARD_DRAWN_FROM_DECK = "card_drawn_from_deck"


class PHistoryEvent(BaseModel):
    kind: EventKind
    who_made_it: PlayerType
    card_id: str
    card_name: str
    turn_number: int = 0

    def to_readable_string(self) -> str:
        """Convert history event to human-readable format"""
        player = "You" if self.who_made_it == PlayerType.ME else "Opponent"

        match self.kind:
            case EventKind.CARD_PLAYED_FROM_HAND:
                return f"Turn {self.turn_number}: {player} played \"{self.card_name}\""
            case EventKind.CARD_DRAWN_FROM_DECK:
                # Don't reveal opponent's drawn cards
                if self.who_made_it == PlayerType.OP:
                    return f"Turn {self.turn_number}: {player} drew a card"
                return f"Turn {self.turn_number}: {player} drew \"{self.card_name}\""
            case _:
                return f"Turn {self.turn_number}: {player} - {self.kind}"


# Legacy alias for backward compatibility
PEvent = PHistoryEvent


class GameState(BaseModel):
    """Current state of an active game"""

    room_id: Optional[str] = None
    players: Optional[List[Player]] = None
    current_turn_player_id: str
    history: List[PHistoryEvent]
    game_started: bool = False
    game_finished: bool = False
    winner_id: Optional[str] = None
    turn_count: int
    cards_in_hand_me: list[PCardModel]
    cards_in_board: list[tuple[PCardModel, tuple[int, int]]]  # [(a card, coordinates)]
    cards_in_gy_me: list[PCardModel]
    cards_in_gy_op: list[PCardModel]
    cards_in_deck_me: list[PCardModel]
    active_ring: str


class OmniGameState(GameState):
    cards_in_hand_op: list[PCardModel]
    cards_in_deck_op: list[PCardModel]


class PRoom(BaseModel):
    """To manage lobbies"""

    room_id: str
    host_id: str
    players: List[str]  # ids
