from Game import Game
from GameObjects.Board import Board
from GameObjects.Card import Card
from GameObjects.Hand import HandController


class Bot:
    def __init__(self, hand_controller: HandController):
        self.hand_controller = hand_controller

    def think(self, board: Board) -> tuple[Card, int, int]:
        # Get the card_model from the first CardController in hand
        if not self.hand_controller.cards:
            return None, None, None

        card_controller = self.hand_controller.cards[0]
        card = card_controller.card_model

        for row in range(board.n_rows):
            for col in range(board.n_cols):
                if board.can_play_card(card_controller, row, col):
                    return (card, row, col)  # TODO

        return None, None, None
