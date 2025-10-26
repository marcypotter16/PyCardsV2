import os
import pygame as p

SCALING_FACTOR = 50
CARD_DIMENSIONS = SCALING_FACTOR * p.Vector2(2.5, 3.5)
CARD_ART_SIZE_RATIO = 0.9

SLOT_DIMENSIONS = CARD_DIMENSIONS * 1.1

COLORS = {
    "slot": {"o_color": p.Color(255, 255, 255), "h_color": p.Color(255, 0, 0)},
    "card": {},
}

ART_PATH = os.path.join(os.getcwd(), "Assets", "sprites", "art")
CARD_BASE_PATH = os.path.join(ART_PATH, "PACardBase.png")
CARD_BACK_PATH = os.path.join(ART_PATH, "CardBack.png")
