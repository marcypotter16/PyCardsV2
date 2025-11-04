import math
from Constants import GRID_DIMENSIONS, SLOT_DIMENSIONS
from Collections.Grid import Grid
from GameObjects.Card import CardController
from GameObjects.GameObject import GameObject
from GameObjects.Slot import SlotController
import pygame as p


class Board(GameObject):
    def __init__(self, game, parent=None, pivot=...):
        super().__init__(game, parent, pivot)
        self.n_rows, self.n_cols = GRID_DIMENSIONS
        self.grid = Grid[SlotController](GRID_DIMENSIONS[0], GRID_DIMENSIONS[1])
        self.cards: list[CardController] = []
        self._init_grid()

    def move_center(self, new_center: p.Vector2):
        for slot in self.grid.flatten():
            new_pos = slot.transform.position + (new_center - self.transform.position)
            slot.move(new_pos)
        self.transform.position = new_center

    def _init_grid(self):
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                slot = SlotController(self.game, self)
                slot.move((col * SLOT_DIMENSIONS[0], row * SLOT_DIMENSIONS[1]))
                # slot.move(
                #     slot.transform.position
                #     - 0.5
                #     * p.Vector2(
                #         SLOT_DIMENSIONS[0] * self.n_rows,
                #         SLOT_DIMENSIONS[1] * self.n_cols,
                #     )
                # )
                # Centering
                # print(math.floor(self.n_cols * 0.5), math.floor(self.n_rows * 0.5))
                offset = p.Vector2(
                    SLOT_DIMENSIONS[0] * math.floor(self.n_cols * 0.5),
                    SLOT_DIMENSIONS[1] * math.floor(self.n_rows * 0.5),
                )
                slot.move(slot.transform.position - offset)
                self.grid.insert(slot, row, col)
                # self.grid.insert(row + col, row, col)

    def play_card(self, card: CardController, row: int, col: int):
        try:
            self.grid.get(row, col).add_card(card)
            self.cards.append(card)
        except IndexError:
            print("Error in inserting the card in grid")

    def update(self, delta):
        return super().update(delta)

    def render(self, surface):
        return super().render(surface)

    def __repr__(self):
        return str(self.grid)
