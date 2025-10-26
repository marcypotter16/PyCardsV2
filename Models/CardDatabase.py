from Models.Card import Card
from Constants import ART_PATH
import os
# print(ART_PATH)

CARD_DATABASE = {
    "goth_girl": Card("Maire von Neumann", 5, os.path.join(ART_PATH, "PAGothGirl.png"))
}