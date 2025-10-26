import pygame as p

class Transform2:
    def __init__(self):
        self.position: p.Vector2 = p.Vector2(0, 0)
        self.rotation: float = 0.0
        self.scale: float = 1.0

    def set_rot(self, angle: float):
        self.rotation = angle

    def rotate_by(self, angle: float):
        self.rotation += angle

    def scale_by(self, factor: float):
        self.scale *= factor

    def move(self, new_position: p.Vector2):
        self.position = new_position