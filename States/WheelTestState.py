from GameObjects.Wheel import Wheel
from States.State import State


class WheelTestState(State):
    def __init__(self, game, data: object | None = None, layer="foreground"):
        super().__init__(game, data, layer)
        self.wheel = Wheel(self.game, self)
        self.wheel.max_n = 20
        self.wheel.scale(4.0)
        self.wheel.move(self.game.GAME_CENTER)
        # self.wheel.is_spinning = True
        self.wheel.spin()

    def update(self, delta_time):
        super().update(delta_time)
        self.wheel.update(delta_time)

    def render(self, surface):
        super().render(surface)
        self.wheel.render(surface)
