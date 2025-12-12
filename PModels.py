from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel


class PCardModel(BaseModel):
    uid: str
    name: str
    base_power: int
    current_power: int
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


class PEvent(BaseModel):
    kind: EventKind
    who_made_it: PlayerType
    card: PCardModel


class GameState(BaseModel):
    """Current state of an active game"""

    room_id: Optional[str] = None
    players: Optional[List[Player]] = None
    current_turn_player_id: str
    history: List[PEvent]
    game_started: bool = False
    game_finished: bool = False
    winner_id: Optional[str] = None
    turn_count: int
    cards_in_hand_me: list[PCardModel]
    cards_in_board: list[tuple[PCardModel, tuple[int, int]]]  # [(a card, coordinates)]
    cards_in_gy_me: list[PCardModel]
    cards_in_gy_op: list[PCardModel]
    cards_in_deck_me: list[PCardModel]


class OmniGameState(GameState):
    cards_in_hand_op: list[PCardModel]
    cards_in_deck_op: list[PCardModel]


class PRoom(BaseModel):
    """To manage lobbies"""

    room_id: str
    host_id: str
    players: List[str]  # ids
