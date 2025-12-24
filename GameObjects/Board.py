import math
from typing import List
from Constants import GRID_DIMENSIONS, SLOT_DIMENSIONS
from Collections.Grid import Grid
from GameObjects.Card.Card import CardControllerBase, UnitCardController
from GameObjects.GameObject import GameObject
from GameObjects.Slot import SlotController, SlotUnavailableError
import pygame as p


class Board(GameObject):
    def __init__(self, game, parent=None, pivot=...):
        super().__init__(game, parent, pivot)
        self.n_rows, self.n_cols = GRID_DIMENSIONS
        self.grid = Grid[SlotController](GRID_DIMENSIONS[0], GRID_DIMENSIONS[1])
        self.cards: list[UnitCardController] = []
        self.slot_padding = p.Vector2(10, 10)
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
                slot.move(
                    (
                        col * (SLOT_DIMENSIONS[0] + self.slot_padding.x),
                        row * (SLOT_DIMENSIONS[1] + self.slot_padding.y),
                    )
                )
                offset = p.Vector2(
                    (SLOT_DIMENSIONS[0] + self.slot_padding.x)
                    * math.floor(self.n_cols * 0.5),
                    (SLOT_DIMENSIONS[1] + self.slot_padding.y)
                    * math.floor(self.n_rows * 0.5),
                )
                slot.move(slot.transform.position - offset)
                self.grid.insert(slot, row, col)
        self.center_coords = (int(self.n_rows / 2), int(self.n_cols / 2))
        print(f"center coords: {self.center_coords}")
        self.center_slot = self.grid.get(self.center_coords[0], self.center_coords[1])
        print(self.center_slot)

    def set_slots_visible(self, visible: bool):
        for slot in self.grid.flatten():
            slot.is_visible = visible

    def can_play_card(self, card: CardControllerBase, row: int, col: int) -> bool:
        return (
            row <= self.n_rows
            and col <= self.n_cols
            and self.grid.get(row, col).can_add_card(card)
        )

    def play_card(self, card: CardControllerBase, row: int, col: int) -> bool:
        try:
            self.grid.get(row, col).add_card(card)
            self.cards.append(card)
            return True
        except SlotUnavailableError:
            print("Slot unavailable")
            return False
        except IndexError:
            print("Error in inserting the card in grid")
            return False

    def get_neighbours(self, row: int, col: int) -> List[SlotController]:
        """Returns the adjacent neighbors (up, down, left, right) of the slot at (row, col)."""
        neighbours = []
        # Define the 4 directions: up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            # Check if the neighbor is within bounds
            if 0 <= new_row < self.n_rows and 0 <= new_col < self.n_cols:
                neighbours.append(self.grid.get(new_row, new_col))

        return neighbours

    def update(self, delta):
        return super().update(delta)

    def render(self, surface):
        return super().render(surface)

    def __repr__(self):
        return str(self.grid)
