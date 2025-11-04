from States.State import State
from UI.Bezier import CubicBezier, QuadraticBezier
import pygame as p


class BezierTestState(State):
    def __init__(self, game, data: object | None = None, layer="foreground"):
        super().__init__(game, msg, layer)

        self.bezier_curve = QuadraticBezier(
            p.Vector2(100, 100), p.Vector2(200, 200), p.Vector2(300, 100)
        )
        self.bezier_curve_cubic = CubicBezier(
            p.Vector2(100, 300),
            p.Vector2(200, 300),
            p.Vector2(200, 500),
            p.Vector2(300, 500),
        )

    def render(self, surface):
        super().render(surface)
        self.bezier_curve.render(surface)
        self.bezier_curve_cubic.render(surface)

    def update(self, delta_time):
        return super().update(delta_time)
