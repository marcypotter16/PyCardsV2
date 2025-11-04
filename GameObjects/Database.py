from GameObjects.Card import Card
from Constants import ART_PATH
import os

# print(ART_PATH)

CARD_DATABASE = {
    "goth_girl": Card("Maire von Neumann", 5, os.path.join(ART_PATH, "PAGothGirl.png"))
}

DECK_DATABASE = {"base_deck": [{"Maire von Neumann": 10}]}
