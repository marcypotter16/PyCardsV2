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

    def move(self, new_position):
        for c in self.children:
            c.move(
                c.transform.position + new_position - self.transform.position
            )  # Take into account the offset between parent and child
        self.transform.move(new_position)  # This HAS to be done after the for loop

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
