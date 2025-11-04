from Game import Game
from GameObjects.Board import Board
from GameObjects.Card import CardController
from GameObjects.Database import CARD_DATABASE
from GameObjects.Deck import DeckController
from GameObjects.GameObject import GameObject
from GameObjects.Hand import HandController
from GameObjects.PlayerType import PlayerType
from States.CardDetailedView import CardDetailedView
import pygame as p
from Tween.Tween import EasingType
from PModels import PCardModel, Player, GameState, OmniGameState


class GameManager(GameObject):
    def __init__(self, game: Game):
        super().__init__(game)
        self.game.tweener_manager.set_tween_motion_method(EasingType.EASE_OUT_QUAD)
        self.board = Board(game, self)
        self.hand_me = HandController(
            self.game, self, center=(self.game.SCREEN_CENTER[0], self.game.GAME_H)
        )
        self.hand_op = HandController(
            self.game, self, center=(self.game.SCREEN_CENTER[0], 0)
        )
        self.deck_me = DeckController(self.game, self)
        self.deck_op = DeckController(self.game, self)
        self.debug = True
        self.setup()

    def setup(self):
        self.hand_me.owner = PlayerType.ME
        self.hand_op.owner = PlayerType.OP
        self.board.move_center(self.game.SCREEN_CENTER)
        self.deck_me.move((0.85 * self.game.GAME_W, 0.75 * self.game.GAME_H))
        self.deck_me.owner = PlayerType.ME
        self.deck_op.move((0.85 * self.game.GAME_W, 0.25 * self.game.GAME_H))
        self.deck_op.owner = PlayerType.OP
        self.hovered_card: CardController = None
        self.dragged_card: CardController = None
        if self.debug:
            for _ in range(5):
                self.hand_me.add_card(CARD_DATABASE["goth_girl"])

    # Hands
    def handle_hands(self, dt):
        mouse_in_hand = self.hand_me.rect.collidepoint(self.game.mousepos)

        for c in self.hand_me.cards:
            # Check if mouse is hovering this specific card
            is_hovering = mouse_in_hand and c.rect.collidepoint(self.game.mousepos)

            # Only trigger tween when hover state changes
            if is_hovering and not c.hovered:
                # Mouse just entered the card
                self.hovered_card = c
                c.hovered = True
                c.tween_scale_to(1.5)
                c.tween_pos(
                    c.transform.position + c.rect.h * 0.5 * p.Vector2(0, -1), drop=False
                )
            elif not is_hovering and c.hovered:
                # Mouse just left the card
                self.hovered_card = None
                c.hovered = False
                c.tween_scale_to(1)
                c.snap_back()

    def hand_me_handle_click_sx(self, dt):
        for c in self.hand_me.cards:
            if c.rect.collidepoint(self.game.mousepos):
                print(f"Clicked sx my card: {c.name}")
                self.dragged_card = c
                break

    def hand_me_handle_click_dx(self, dt):
        for c in self.hand_me.cards:
            if c.rect.collidepoint(self.game.mousepos):
                print(f"Clicked dx my card: {c.name}")
                self.game.push_state(CardDetailedView(self.game, card=c.card_model))

    # BOARD
    def update_cards_in_board(self, dt):
        for c in self.board.cards:
            c.update(dt)

    def process_card_release(self):
        card_placed = False
        for row in range(self.board.n_rows):
            for col in range(self.board.n_cols):
                slot = self.board.grid.get(row, col)
                if slot.rect.collidepoint(self.game.mousepos):
                    self.board.play_card(self.dragged_card, row, col)
                    self.dragged_card.tween_scale_to(1.0)
                    # Remove card from hand
                    if self.dragged_card in self.hand_me.cards:
                        self.hand_me.cards.remove(self.dragged_card)
                    card_placed = True
                    break
            if card_placed:
                break

        if not card_placed:
            self.dragged_card.snap_back()

        self.dragged_card = None

    def update(self, dt):
        super().update(dt)
        # self.handle_hands(dt)

        # Debug: Press 'P' to print game state as JSON
        if self.game.actions.get("action1") == 1:
            print("\n=== GAME STATE (Player View) ===")
            print(self.export_state_json(omni=False))
            print("\n=== OMNI GAME STATE (Server View) ===")
            print(self.export_state_json(omni=True))
            print("\n")

        if self.game.clicked_sx == 1:
            if self.hand_me.rect.collidepoint(self.game.mousepos):
                self.hand_me_handle_click_sx(dt)
        if self.game.clicked_sx == -1:
            if self.dragged_card is not None:
                self.process_card_release()
        if self.game.clicked_dx == -1:
            if self.hand_me.rect.collidepoint(self.game.mousepos):
                self.hand_me_handle_click_dx(dt)
        if self.dragged_card is None:
            self.handle_hands(dt)
        else:
            self.dragged_card.move(self.game.mousepos)
        self.update_cards_in_board(dt)
        # self.board.update(dt)

    def get_game_state(self, player: int = PlayerType.ME) -> GameState:
        """
        Serialize the current game state for a specific player.
        Only includes information that player should see.
        """
        # Serialize hand
        cards_in_hand_me = [card.to_pydantic() for card in self.hand_me.cards]

        # Serialize board (both players can see all cards on board)
        cards_in_board = []
        for row in range(self.board.n_rows):
            for col in range(self.board.n_cols):
                slot = self.board.grid.get(row, col)
                if slot.content is not None:
                    cards_in_board.append((slot.content.to_pydantic(), (row, col)))

        # TODO: Implement graveyards and decks
        cards_in_gy_me = []
        cards_in_gy_op = []
        cards_in_deck_me = []

        return GameState(
            turn_count=0,  # TODO: Implement turn counter
            cards_in_hand_me=cards_in_hand_me,
            cards_in_board=cards_in_board,
            cards_in_gy_me=cards_in_gy_me,
            cards_in_gy_op=cards_in_gy_op,
            cards_in_deck_me=cards_in_deck_me,
        )

    def get_omni_game_state(self) -> OmniGameState:
        """
        Serialize the complete game state (server-side).
        Includes hidden information like opponent's hand.
        """
        # Get base game state
        base_state = self.get_game_state()

        # Add opponent's hidden information
        cards_in_hand_op = [card.to_pydantic() for card in self.hand_op.cards]
        cards_in_deck_op = []  # TODO: Implement

        return OmniGameState(
            **base_state.model_dump(),
            cards_in_hand_op=cards_in_hand_op,
            cards_in_deck_op=cards_in_deck_op,
        )

    def load_game_state(self, state: GameState):
        """
        Restore the game from a GameState.
        This would be called on the client when receiving state from server.
        """
        # TODO: Implement this - will need to:
        # 1. Clear current game state
        # 2. Recreate cards from PCardModel data
        # 3. Place them in correct positions
        # 4. Handle animations/transitions
        pass

    def export_state_json(self, omni: bool = False) -> str:
        """
        Export game state as JSON string for networking.

        Args:
            omni: If True, export OmniGameState (server-side, includes hidden info)
                  If False, export GameState (client-side, player's view only)
        """
        if omni:
            state = self.get_omni_game_state()
        else:
            state = self.get_game_state()

        return state.model_dump_json(indent=2)

    def render(self, surface):
        super().render(surface)
