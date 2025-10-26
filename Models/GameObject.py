from Game import Game
from Models.Transform import Transform2
from pygame import Vector2


class GameObject:
    def __init__(self, game: Game, parent=None, pivot: Vector2 = Vector2(0, 0)):
        self.parent = parent  # None is fine
        self.game = game
        self.transform = Transform2()
        self.parent = None
        self.children: list[GameObject] = []
        self.pivot = pivot

    def update(self, delta):
        for c in self.children:
            c.update(delta)

    def render(self, surface):
        for c in self.children:
            if c.is_visible:
                c.render(surface)

    def move(self, new_position):
        self.transform.move(new_position)
        for c in self.children:
            c.move(new_position)

    def rotate(self, angle):
        self.transform.set_rot(angle)
        for c in self.children:
            c.rotate(angle)

    def rotate_around_point(self, angle, center):
        pass
