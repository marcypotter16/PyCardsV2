from Generic.LinkedList import MB_LL
from Models.Transform import Transform2
from Models.GameObject import GameObject
import pygame as p

from Utils.Text import draw_centered_text


class SpriteRenderer(GameObject):
    def __init__(
        self,
        parent: GameObject,
        image_path: str,
        dimensions: tuple[int, int] | p.Vector2,
    ):
        # super().__init__(game, parent)
        self.parent = parent
        self.parent.children.append(self)
        self.position = p.Vector2(0, 0)
        self.__last_frame_position = p.Vector2(0, 0)
        self.transform = Transform2()
        self.TWEEN_DUR = 0.2
        self.__o_dimensions = self.dimensions = dimensions
        self.__o_sprite = self.sprite = p.image.load(image_path)
        self.sprite = self.__o_sprite = p.transform.smoothscale(
            self.sprite, self.dimensions
        )
        self.rect = p.Rect(0, 0, dimensions[0], dimensions[1])
        self.is_visible = True
        self.debug = False
        self.mb = {
            "active": False,
            "n_frames": 3,
            "threshold": 0.5,  # Distance threshold for motion detection
        }
        self.__mb_do_it = False
        self.__is_rotating = self.__is_scaling = self.__is_moving = False
        self.__stop_rotating = lambda: setattr(
            self, "_SpriteRenderer__is_rotating", False
        )
        self.__stop_moving = lambda: setattr(self, "_SpriteRenderer__is_moving", False)

    def __stop_scaling(self, on_finish):
        self.__is_scaling = False
        on_finish.__call__()

    def set_dim(self, new_dimensions: tuple[int, int]):
        self.dimensions = new_dimensions
        self.sprite = p.transform.smoothscale(self.__o_sprite, self.dimensions)
        self.rect.w, self.rect.h = new_dimensions

    def scale_by(self, factor: float):
        self.transform.scale_by(factor)
        self.rect.scale_by(factor)
        self.dimensions = p.Vector2(self.dimensions) * factor
        self.sprite = p.transform.smoothscale_by(self.__o_sprite, self.transform.scale)

    def move(self, new_position: tuple[int, int] | p.Vector2):
        self.transform.move(p.Vector2(new_position))
        self.rect.center = p.Vector2(new_position)

    def rotate(self, angle: float):
        self.transform.set_rot(angle)
        self.sprite = p.transform.rotozoom(
            self.__o_sprite, self.transform.rotation, self.transform.scale
        )

    def rotate_around_point(self, angle: float, center: p.Vector2):
        vec = self.transform.position - center
        rot_vec = vec.rotate(angle)
        new_pos = center + rot_vec
        self.rotate(angle)
        self.move(new_pos)

    def tween_pos(self, new_position: tuple[int, int] | p.Vector2):
        self.__is_moving = True
        self.parent.game.tweener.add_tween(
            self.transform,
            "position",
            to_=p.Vector2(new_position),
            duration=self.TWEEN_DUR,
            on_finish=self.__stop_moving,
        )

    def tween_rot(self, angle: float):
        self.__is_rotating = True
        self.parent.game.tweener.add_tween(
            self.transform,
            "rotation",
            to_=angle,
            duration=self.TWEEN_DUR,
            on_finish=self.__stop_rotating,
        )

    def tween_scale_by(self, factor: float, on_finish=None):
        self.__is_scaling = True
        self.parent.game.tweener.add_tween(
            self.transform,
            "scale",
            to_=factor,
            duration=self.TWEEN_DUR,
            on_finish=lambda: self.__stop_scaling(on_finish),
        )

    def setup_mb(self, active, n_frames):
        self.mb["active"] = active
        self.mb["n_frames"] = n_frames
        self.__init_mb()

    def __init_mb(self):
        self.mb_sprites = MB_LL(self.mb["n_frames"])
        self.mb_rects = MB_LL(self.mb["n_frames"])
        # self.__mb_frame_count = self.mb["n_frames"]

    def set_visible(self, visible):
        self.is_visible = visible

    def update(self, delta: float):
        if self.__is_rotating or self.__is_scaling:
            self.sprite = p.transform.rotozoom(
                self.__o_sprite, self.transform.rotation, self.transform.scale
            )
            self.rect.size = p.Vector2(self.__o_dimensions) * self.transform.scale
        if self.__is_moving:
            self.rect.center = self.transform.position
        self.position = p.Vector2(self.rect.center)

        # MB - Check if sprite has moved enough to warrant motion blur
        if self.mb["active"]:
            # Calculate distance moved since last frame
            distance_moved = self.position.distance_to(self.__last_frame_position)

            # Only do motion blur if sprite has moved beyond threshold
            if distance_moved > self.mb["threshold"]:
                self.__mb_do_it = True
                mb_sprite = self.sprite.copy()
                mb_sprite.set_alpha(180)  # Semi-transparent for blur effect
                self.mb_sprites.push_front((mb_sprite, self.rect.copy()))
            else:
                # Sprite is stationary or barely moving - clear motion blur
                self.__mb_do_it = False
                if hasattr(self, "mb_sprites"):
                    # Clear the linked list by reinitializing it
                    self.mb_sprites = MB_LL(self.mb["n_frames"])

        # Store position for next frame comparison
        self.__last_frame_position = self.position.copy()

        # self.move(self.transform.position + p.Vector2(0.1, 0))

    def render(self, surf: p.surface.Surface):
        if not self.mb["active"]:
            surf.blit(self.sprite, self.sprite.get_rect(center=self.rect.center))
        else:
            # Render motion blur frames with fading alpha
            mb_frames = self.mb_sprites.to_list()
            for i, (sprite, rect) in enumerate(mb_frames):
                alpha = int(255 * (1 - i / self.mb["n_frames"]))  # Fade older frames
                sprite.set_alpha(alpha)
                surf.blit(sprite, sprite.get_rect(center=rect.center))
            # Render current frame on top
            surf.blit(self.sprite, self.sprite.get_rect(center=self.rect.center))
        if self.debug:
            p.draw.rect(surf, p.Color(255, 0, 0), self.rect, 2)
            p.draw.rect(
                surf,
                p.Color(0, 100, 200),
                self.sprite.get_rect(center=self.rect.center),
                2,
            )
            draw_centered_text(
                self.parent.game.font_tiny,
                surf,
                f"mb_is_on: {self.__mb_do_it}",
                (255, 255, 255),
                p.Rect(20, 20, 100, 10),
            )
