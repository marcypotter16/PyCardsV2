import pygame
from GameObjects.Board import Board
from GameObjects.Slot import SlotController
from States.State import State


class BoardTestState(State):
    def __init__(self, game, data: object | None = None, layer="foreground"):
        super().__init__(game, msg, layer)
        self.board = Board(game, self)
        self.board.move_center(self.game.SCREEN_CENTER)
        # print(self.board)
        # for slot in self.board.grid.flatten():
        #     print(slot.transform.position)
        # self.test_slot = SlotController(self.game, self)
        # self.test_slot.move(self.game.SCREEN_CENTER)
        # print(self.board.children)

    def update(self, delta_time):
        super().update(delta_time)
        self.board.update(delta_time)
        for s in self.board.children:
            s.highlighted = False
            if s.rect.collidepoint(self.game.mousepos):
                s.highlighted = True
        # self.test_slot.update(delta_time)

    def render(self, surface):
        super().render(surface)
        self.board.render(surface)
        pygame.draw.circle(surface, (0, 255, 0), self.board.transform.position, 10)
        # self.test_slot.render(surface)
