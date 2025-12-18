from Game import Game
from GameObjects.Transform import Transform2
from pygame import Vector2


class GameObject:
    def __init__(self, game: Game, parent=None, pivot: Vector2 = Vector2(0, 0)):
        self.parent = parent  # None is fine
        self.game = game
        self.transform = Transform2()
        self.children: list[GameObject] = []
        if self.parent is not None and hasattr(self.parent, "children"):
            self.parent.children.append(self)
        self.pivot = pivot
        self.is_visible = True

    def update(self, delta):
        for c in self.children:
            c.update(delta)

    def render(self, surface):
        for c in self.children:
            if c.is_visible:
                c.render(surface)

    def move(self, new_position: Vector2 | tuple[int, int]):
        for c in self.children:
            c.move(
                c.transform.position + Vector2(new_position) - self.transform.position
            )  # Take into account the offset between parent and child
        self.transform.move(new_position)  # This HAS to be done after the for loop

    def move_percent(self, x_percent: float, y_percent: float):
        """
        Moves to the coordinates corresponding to the specified percentage of screen dimensions, for example if the screen width is 1000 and x_percent is 0.2 the x coordinate of the new position will be 0.2*1000 = 200
        """
        new_position = Vector2(
            x_percent * self.game.GAME_W, y_percent * self.game.GAME_H
        )
        self.move(new_position)

    def tween_pos(self, new_position: Vector2 | tuple[int, int]):
        for c in self.children:
            c.tween_pos(c.transform.position + new_position - self.transform.position)
        self.game.tweener_manager.add_tween(
            self.transform, "position", to_=new_position
        )

    def scale_by(self, factor):
        self.transform.scale_by(factor)
        for c in self.children:
            if c.is_visible:
                c.scale_by(factor)

    def rotate(self, angle):
        self.transform.set_rot(angle)
        for c in self.children:
            c.rotate(angle)

    def rotate_around_point(self, angle, center):
        pass
