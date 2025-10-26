from Constants import CARD_ART_SIZE_RATIO, CARD_BASE_PATH, CARD_BACK_PATH, CARD_DIMENSIONS
from Game import Game
import pygame as p

from Models.GameObject import GameObject
from Utils.Text import draw_text

class Card:
    def __init__(self, name: str, base_power: int, art_path: str):
        self.name = name
        self.base_power = base_power
        self.art_path = art_path

class CardController(GameObject):
    def __init__(self, game: Game):
        super().__init__(game)
        self.rect = p.Rect((0, 0), CARD_DIMENSIONS)
        self.base_art = p.image.load(CARD_BASE_PATH)
        self.base_art = p.transform.smoothscale(self.base_art, CARD_DIMENSIONS)
        self.back_art = p.image.load(CARD_BACK_PATH) # is it a good idea to load the back of the card on every card even if not shown?
        self.back_art = p.transform.smoothscale(self.back_art, CARD_DIMENSIONS)
        self.art_rect = p.Rect((0, 0), CARD_ART_SIZE_RATIO * CARD_DIMENSIONS)
        self.art_rect.center = self.rect.center
        self.center = p.Vector2(self.rect.center)
        self.center_before_drag = self.center.copy()
        self.original_scale = self.current_scale = 1

        self.is_hovered = False
        self.is_being_dragged = False
        self.can_be_selected = True

    def from_card(self, card: Card):
        self.name = card.name
        self.base_power = card.base_power
        self.art_path = card.art_path
        self.art = p.image.load(card.art_path)
        self.art = p.transform.smoothscale(self.art, CARD_DIMENSIONS * CARD_ART_SIZE_RATIO)

    def move_center(self, new_center):
        self.center = new_center

    def drop(self):
        self.center_before_drag = self.center
    
    def snap_back(self):
        self.tween_center(self.center_before_drag, self.drop)
        # self.move_center(self.center_before_drag.copy())
        # self.drop()

    def tween_center(self, new_center, callback = None):
        self.game.tweener.add_tween(
            self,
            "center",
            p.Vector2(self.center),
            p.Vector2(new_center),
            0.5,
            callback if callback else None
        )

    def scale(self, factor: float):
        self.rect.scale_by_ip(factor)
        self.base_art = p.transform.smoothscale_by(self.base_art, factor)
        self.art_rect.scale_by_ip(factor)
        self.art = p.transform.smoothscale_by(self.art, factor)

    def update(self, delta_time):
        self.rect.center = self.art_rect.center = self.center
        # self.rect.update(self.rect)
        # self.art_rect.update(self.art_rect)
        self.is_hovered = self.rect.collidepoint(self.game.mousepos)
        # self.is_being_dragged = False
        if self.is_hovered and self.can_be_selected:
            if self.is_being_dragged and self.game.clicked_sx == -1: # Release
                print("Snapping Back")
                self.is_being_dragged = False
                self.snap_back()
                return
            self.is_being_dragged = self.game.actions["mouse_sx"] > 0

            # if self.game.clicked_dx == -1:
            #     self.scale(2.0)
        if self.is_being_dragged:
            self.move_center(self.game.mousepos)
    
    def render(self, surface):
        surface.blit(self.base_art, self.rect)
        surface.blit(self.art, self.art_rect)
        # draw_text(self.game.font_small, surface, f"Hovered: {self.is_hovered}, dragging: {self.is_being_dragged}, clicked sx: {self.game.clicked_sx}, cbd: {self.center_before_drag}, center: {self.center}")