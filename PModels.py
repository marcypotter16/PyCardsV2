from typing import List, Optional
from pydantic import BaseModel


class PCardModel(BaseModel):
    uid: str
    name: str
    base_power: int
    current_power: int
    description: Optional[str] = None
    owner: int  # 0 for ME, 1 for OP
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


class GameState(BaseModel):
    """Current state of an active game"""

    room_id: str
    players: List[Player]
    current_turn_player_id: str
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
    players: List[str]  # ids
