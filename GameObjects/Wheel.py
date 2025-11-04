import math
import random
from GameObjects.GameObject import GameObject
import pygame as p

from Utils.Text import draw_centered_text, draw_text


class Wheel(GameObject):
    def __init__(self, game, parent=None, max_n=8, pivot=...):
        super().__init__(game, parent, pivot)
        self.color = p.Color(255, 255, 255)
        self.outer_radius = 60
        self.inner_radius = 50
        self.number_radius = 30
        self.stroke_width = 2
        self.max_n = max_n
        self.number_positions = []
        self.end_positions_for_caret = self.transform.position - p.Vector2(
            0, -self.outer_radius - 10
        )
        # self._o_end_pos_for_caret = self.end_positions_for_caret.copy()
        self._end_positions_for_separators = []
        self._angle_offset = 0
        self.angular_speed = 10
        self.angular_accel = 0
        self.is_spinning = False
        self.calculate_number_positions()

    def calculate_number_positions(self):
        self.number_positions.clear()
        self._end_positions_for_separators.clear()
        vec_up_numbers = p.Vector2(0, -1) * self.number_radius
        vec_up_separators = p.Vector2(0, -1) * self.inner_radius
        for i in range(self.max_n):
            self.number_positions.append(
                self.transform.position
                + vec_up_numbers.rotate(
                    self._angle_offset + float(360 * i) / self.max_n
                )
            )
            self._end_positions_for_separators.append(
                self.transform.position
                + vec_up_separators.rotate(
                    self._angle_offset + float(360 * (i - 0.5)) / self.max_n
                )
            )

    def calculate_end_position_for_caret(self):
        self.end_positions_for_caret = self.transform.position + p.Vector2(
            0, -self.outer_radius - 10
        ).rotate(self._angle_offset)

    def return_current_value(self):
        angle_per_segment = 360 / self.max_n
        adjusted_angle = self._angle_offset + 0.5 * angle_per_segment
        value = math.floor(adjusted_angle / angle_per_segment)
        value %= self.max_n
        print(
            f"Debug: aps={angle_per_segment}, offset={self._angle_offset:.2f}, adjusted={adjusted_angle:.2f}, value={value}"
        )
        return value

    def move(self, new_position):
        super().move(new_position)
        self.calculate_number_positions()

    def spin(self):
        self.is_spinning = True
        self.angular_speed = random.randrange(500, 1000)
        self.angular_accel = random.randrange(-200, -100)

    def update(self, delta):
        super().update(delta)
        if self.is_spinning:
            # print(delta, self.angular_speed * delta)
            self._angle_offset += self.angular_speed * delta
            self.angular_speed += self.angular_accel * delta
            self.calculate_end_position_for_caret()
            # Stop spinning when speed becomes very small or negative
            if self.angular_speed <= 1.0:
                self.is_spinning = False
                self.angular_speed = 0
                print(f"Wheel stopped at value: {self.return_current_value()}")

    def scale(self, factor):
        self.outer_radius *= factor
        self.inner_radius *= factor
        self.number_radius *= factor
        self.calculate_end_position_for_caret()
        self.calculate_number_positions()

    def render(self, surface):
        super().render(surface)
        p.draw.circle(
            surface,
            self.color,
            self.transform.position,
            self.outer_radius,
            self.stroke_width,
        )
        p.draw.circle(
            surface,
            self.color,
            self.transform.position,
            self.inner_radius,
            self.stroke_width,
        )
        p.draw.aaline(
            surface, self.color, self.transform.position, self.end_positions_for_caret
        )
        for i, pos in enumerate(self.number_positions):
            rect = p.Rect(0, 0, 10, 10)
            rect.center = pos
            draw_centered_text(self.game.font_tiny, surface, str(i), self.color, rect)
        for pos in self._end_positions_for_separators:
            p.draw.aaline(surface, self.color, self.transform.position, pos)
