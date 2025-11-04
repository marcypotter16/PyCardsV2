from GameObjects.Hand import HandModel
from GameObjects.PlayerType import PlayerType


class Player:
    def __init__(self):
        self.hand = HandModel()


if __name__ == "__main__":
    print(PlayerType.ME, PlayerType.OP)
