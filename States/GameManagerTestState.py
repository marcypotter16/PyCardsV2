from GameManager import GameManager
from States.State import State


class GameManagerTestState(State):
    def __init__(self, game, data: object | None = None, layer="foreground"):
        super().__init__(game, msg, layer)
        self.gm = GameManager(self.game)

    def update(self, delta_time):
        super().update(delta_time)
        self.gm.update(delta_time)

    def render(self, surf):
        super().render(surf)
        self.gm.render(surf)
