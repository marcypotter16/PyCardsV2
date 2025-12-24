from Collections.LinkedList import MB_LL
from GameObjects.Transform import Transform2
from GameObjects.GameObject import GameObject
import pygame as p
import io

# from Constants import CARD_DIMENSIONS, CARD_BASE_PATH
from Utils.Text import draw_centered_text


class SpriteRenderer(GameObject):
    def __init__(
        self,
        parent: GameObject = None,
        image: p.Surface | str = None,
        dimensions: tuple[int, int] | p.Vector2 = None,
        scale_img_to_dim: bool = True,
    ):
        """
        :param parent: The parent GameObject
        :type parent: GameObject
        :param image: The sprite you want to render or the full path to an image.
        :type image: p.Surface | str
        :param dimensions: The desired dimensions of the rendered sprite.
        :type dimensions: tuple[int, int] | p.Vector2
        """
        # super().__init__(game, parent)
        self.children: list[GameObject] = []
        self.position = p.Vector2(0, 0)
        self.__last_frame_position = p.Vector2(0, 0)
        self.transform = Transform2()
        self.TWEEN_DUR = 0.2
        self.__o_dimensions = self.dimensions = (
            dimensions if dimensions is not None else (10, 10)
        )
        if isinstance(image, str):
            self.__o_sprite = self.sprite = p.image.load(image).convert_alpha()
        elif isinstance(image, p.Surface):
            self.__o_sprite = self.sprite = image.convert_alpha()
        else:
            self.__o_sprite = self.sprite = None
        if self.sprite is not None:
            # Use smoothscale for better quality when resizing
            try:
                if scale_img_to_dim:
                    self.sprite = self.__o_sprite = p.transform.smoothscale(
                        self.sprite, self.dimensions
                    )
                else:
                    self.dimensions = self.sprite.get_rect().size
            except ValueError:
                # Fallback to regular scale if smoothscale fails
                self.sprite = self.__o_sprite = p.transform.scale(
                    self.sprite, self.dimensions
                )
        self.rect = p.Rect(0, 0, self.dimensions[0], self.dimensions[1])
        self.parent = parent
        if parent is not None:
            self.game = parent.game
            self.parent.children.append(self)
            self.move(self.parent.transform.position)
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

    def __stop_scaling(self, on_finish):
        self.__is_scaling = False
        if on_finish:
            on_finish.__call__()

    def __stop_moving(self, on_finish):
        self.__is_moving = False
        if on_finish:
            on_finish.__call__()

    def set_dim(self, new_dimensions: tuple[int, int]):
        self.dimensions = new_dimensions
        if self.__o_sprite is not None:
            self.sprite = p.transform.scale(self.__o_sprite, self.dimensions)
        self.rect.w, self.rect.h = new_dimensions

    def set_sprite(self, new_sprite: p.Surface):
        # self.__o_sprite = new_sprite
        # Convert to a format that supports smoothscale (24-bit or 32-bit)
        if new_sprite.get_bitsize() not in (24, 32):
            # Convert to RGBA format for compatibility
            new_sprite = new_sprite.convert_alpha()

        try:
            self.__o_sprite = self.sprite = p.transform.smoothscale(
                new_sprite, self.dimensions
            )
        except ValueError:
            # Fallback to regular scale if smoothscale fails
            self.__o_sprite = self.sprite = p.transform.scale(
                new_sprite, self.dimensions
            )

    def set_sprite_no_scale(self, new_sprite: p.Surface):
        self.__o_sprite = self.sprite = new_sprite
        self.__o_dimensions = new_sprite.get_size()
        self.dimensions = self.__o_dimensions
        self.rect.size = self.dimensions
        # Keep the rect centered at current position
        self.rect.center = self.transform.position

    def apply_scale(self):
        """Apply the current transform.scale to the sprite without changing the scale value.
        Useful after set_sprite_no_scale when you need to reapply existing scale."""
        if self.transform.scale != 1.0:
            self.sprite = p.transform.smoothscale_by(
                self.__o_sprite, self.transform.scale
            )
            self.dimensions = p.Vector2(self.__o_dimensions) * self.transform.scale
            self.rect.size = self.dimensions
            self.rect.center = self.transform.position

    def scale_by(self, factor: float):
        self.transform.scale_by(factor)
        self.rect.scale_by(factor)
        self.dimensions = p.Vector2(self.dimensions) * factor
        self.sprite = p.transform.smoothscale_by(self.__o_sprite, self.transform.scale)

    def move(self, new_position: tuple[int, int] | p.Vector2):
        """Move the center of the sprite (coordinates relative to the parent, so for example (0, 0) would be the parents center) to a new position"""
        if self.children:
            for c in self.children:
                c.move(
                    c.transform.position
                    + p.Vector2(new_position)
                    - self.transform.position
                )
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

    def tween_pos(self, new_position: tuple[int, int] | p.Vector2, on_finish=None):
        # Propagate to children first (like move() does)
        if self.children:
            for c in self.children:
                c.tween_pos(
                    c.transform.position
                    + p.Vector2(new_position)
                    - self.transform.position
                )
        self.__is_moving = True
        self.parent.game.tweener_manager.add_tween(
            self.transform,
            "position",
            to_=p.Vector2(new_position),
            duration=self.TWEEN_DUR,
            on_finish=lambda: self.__stop_moving(on_finish),
        )

    def tween_rot(self, angle: float):
        self.__is_rotating = True
        self.parent.game.tweener_manager.add_tween(
            self.transform,
            "rotation",
            to_=angle,
            duration=self.TWEEN_DUR,
            on_finish=self.__stop_rotating,
        )

    def tween_scale_to(self, factor: float, on_finish=None):
        self.__is_scaling = True
        self.parent.game.tweener_manager.add_tween(
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

    def change_tint(self, new_color: p.Color):
        """Change the tint by replacing non-transparent pixels with the new color while preserving alpha"""
        # Make a copy with the original alpha channel
        tex = self.__o_sprite.copy().convert_alpha()

        # Create a mask from the alpha channel
        alpha = p.surfarray.array_alpha(tex).copy()

        # Fill with the new color (this replaces all pixels)
        tex.fill(new_color)

        # Restore the original alpha channel
        p.surfarray.pixels_alpha(tex)[:] = alpha

        # Update the sprite
        self.__o_sprite = tex
        self.sprite = p.transform.scale(tex, self.dimensions)
        del alpha
        del tex

    def update(self, delta: float):
        if self.__is_rotating or self.__is_scaling:
            if self.__o_sprite is not None:
                self.sprite = p.transform.rotozoom(
                    self.__o_sprite, self.transform.rotation, self.transform.scale
                )
                self.rect.size = p.Vector2(self.__o_dimensions) * self.transform.scale
                self.rect.center = self.transform.position
        if self.__is_moving:
            self.rect.center = self.transform.position
        self.position = p.Vector2(self.rect.center)

        # MB - Check if sprite has moved enough to warrant motion blur
        if self.mb["active"] and self.sprite:
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
        if self.children:
            for c in self.children:
                c.update(delta)

        # self.move(self.transform.position + p.Vector2(0.1, 0))

    def render(self, surf: p.surface.Surface):
        if self.sprite is not None and self.is_visible:
            if not self.mb["active"]:
                surf.blit(self.sprite, self.sprite.get_rect(center=self.rect.center))
            else:
                # Render motion blur frames with fading alpha
                mb_frames = self.mb_sprites.to_list()
                for i, (sprite, rect) in enumerate(mb_frames):
                    alpha = int(
                        255 * (1 - i / self.mb["n_frames"])
                    )  # Fade older frames
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
        if self.children:
            for c in self.children:
                c.render(surf)
