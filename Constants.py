import os
import pygame as p

SCALING_FACTOR = 40
CARD_DIMENSIONS = SCALING_FACTOR * p.Vector2(2.5, 3.5)
CARD_ART_SIZE_RATIO = 0.7
CARD_TWEEN_DUR = 0.3

SLOT_DIMENSIONS = CARD_DIMENSIONS * 1.1

COLORS = {
    "slot": {"o_color": p.Color(255, 255, 255), "h_color": p.Color(255, 0, 0)},
    "card": {},
}

GRID_DIMENSIONS = (5, 9)

ART_PATH = os.path.join(os.getcwd(), "Assets", "sprites", "art")
CARD_BASE_PATH = os.path.join(ART_PATH, "PACardBase_old.png")
CARD_BACK_PATH = os.path.join(ART_PATH, "CardBack.png")

# Multiplayer
API_ADDR = "http://localhost:8000/"
WS_ADDR = "ws://localhost:8000/"
WS_JOIN_ROOM_BASE_ADDR = (
    WS_ADDR + "ws/matchmaking/join_room/"
)  # Then add player_name/room_id
WS_CREATE_ROOM_ADDR = WS_ADDR + "ws/matchmaking/create_room/"  # Then add player_name


def get_join_room_addr(p_name: str, room_id: str) -> str:
    return WS_JOIN_ROOM_BASE_ADDR + f"{p_name}/{room_id}"


def get_create_room_addr(p_name: str) -> str:
    return WS_CREATE_ROOM_ADDR + f"{p_name}"
