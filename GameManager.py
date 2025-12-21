from datetime import date
import random
from threading import Timer
import time
from typing import Dict, List
from Bot import Bot
from Constants import CARD_PLAYED_SHOW_TIME
from Game import Game
from GameObjects.Board import Board
from GameObjects.Card import (
    Card,
    CardController,
    CardControllerBase,
    ChangeStructureCardController,
    SpellCardController,
)
from GameObjects.Database import CARD_DATABASE
from GameObjects.Deck import DeckController
from GameObjects.EffectContext import EffectContext
from GameObjects.GameObject import GameObject
from GameObjects.Graveyard import GraveyardController
from GameObjects.Hand import HandController
from GameObjects.MathRing import Ring, Rings, StructureController
from States.GraveyardViewState import GraveyardViewState
from States.CardDetailedView import CardDetailedView
import pygame as p
from Tween.Tween import EasingType
from PModels import (
    EventKind,
    PCardModel,
    PHistoryEvent,
    Player,
    GameState,
    OmniGameState,
    PlayerType,
)
from Utils.Timer import SpacedCallback


class GameManager(GameObject):
    def __init__(self, game: Game, players: List[Player]):
        super().__init__(game)
        self.players = players
        self.active_player_index = 0  # TODO: this is obviously temporary
        self.game.tweener_manager.set_tween_motion_method(EasingType.EASE_OUT_QUAD)
        self.board = Board(game, self)
        self.hand_me = HandController(
            self.game,
            self,
            center=(self.game.GAME_CENTER[0], self.game.GAME_H),
        )
        self.hand_op = HandController(
            self.game, self, center=(self.game.GAME_CENTER[0], 0)
        )
        self.deck_me = DeckController(self.game, self)
        self.deck_op = DeckController(self.game, self)
        self.gy = GraveyardController(self.game, self)
        self.structure = StructureController(self.game, self, initial_scale=2.0)
        self.history: List[PHistoryEvent] = []
        self.debug = True
        self._should_snap_back = True

        def adjust_hand():
            if self.dragged_card is None:
                self.hand_me.reorder()

        self.sc = SpacedCallback(adjust_hand, 30.0)
        self.sc.start()
        self.setup()

    def setup(self):
        self.hand_me.owner = PlayerType.ME
        self.hand_op.owner = PlayerType.OP
        self.board.move_center(self.game.GAME_CENTER)
        # self.board.grid.get(0, 0).set_available(False)
        self.board.center_slot.set_special(True)
        self.deck_me.move((0.85 * self.game.GAME_W, 0.75 * self.game.GAME_H))
        self.deck_me.owner = PlayerType.ME
        self.deck_op.move((0.85 * self.game.GAME_W, 0.25 * self.game.GAME_H))
        self.deck_op.owner = PlayerType.OP
        self.gy.move((0.15 * self.game.GAME_W, 0.5 * self.game.GAME_H))
        self.hovered_card: CardControllerBase = None
        self.dragged_card: CardControllerBase = None
        self._should_dragged_card_follow_mouse = True
        self.turn_count = self.ply_count = (
            0  # ply = half turn, turn = both players played something
        )
        self.active_player: PlayerType = PlayerType.ME
        self.opponent_card_in_progress = (
            False  # Track if opponent is currently playing a card
        )
        self.structure.set_structure(Ring(Rings.Z))
        self.structure.set_color(p.Color("white"))
        self.structure.move(
            0.5 * (self.deck_me.transform.position + self.deck_op.transform.position)
        )
        if self.debug:
            for _ in range(13):
                self.deck_me.add_card(random.choice(list(CARD_DATABASE.values())))
                self.deck_op.add_card(CARD_DATABASE["goth_girl"])
            self.deck_me.add_card(CARD_DATABASE["frobenius"])
            self.deck_me.add_card(CARD_DATABASE["goth_girl"])
            for i in range(5):
                self.hand_me.add_card(
                    self.deck_me.get_and_remove_top_card(), bg_image="BG2.png"
                )
                self.hand_op.add_card(
                    self.deck_op.get_and_remove_top_card(), bg_image="BG4.png"
                )
                # self.hand_op.cards[i].flip()
            for card in self.deck_me.cards:
                card.owner = PlayerType.ME
            for card in self.deck_op.cards:
                card.owner = PlayerType.OP

    # Hands
    def handle_hands(self, dt):
        mouse_in_hand = self.hand_me.rect.collidepoint(self.game.cursorpos)

        for c in self.hand_me.cards:
            # Check if mouse is hovering this specific card
            is_hovering = mouse_in_hand and c.rect.collidepoint(self.game.cursorpos)

            # Only trigger tween when hover state changes
            if is_hovering and not c.hovered:
                # Mouse just entered the card
                self.hovered_card = c
                c.hovered = True
                target_pos = c.transform.position + c.rect.h * 0.5 * p.Vector2(0, -1)
                # c.tween_scale_to(1.5, target_card_position=target_pos)
                c.tween_pos(target_pos, drop=False)
            elif not is_hovering and c.hovered:
                # Mouse just left the card
                self.hovered_card = None
                c.hovered = False
                # c.tween_scale_to(1, target_card_position=c.last_saved_pos)
                c.snap_back()

    def hand_me_handle_click_sx(self, dt):
        for c in self.hand_me.cards:
            if c.rect.collidepoint(self.game.cursorpos):
                print(f"Clicked sx my card: {c.name}")
                self.dragged_card = c
                break

    def hand_me_handle_click_dx(self, dt):
        for c in self.hand_me.cards:
            if c.rect.collidepoint(self.game.cursorpos):
                print(f"Clicked dx my card: {c.name}")
                self.game.push_state(CardDetailedView(self.game, card=c.card_model))
                return

    # BOARD
    def update_cards_in_board(self, dt):
        for c in self.board.cards:
            c.update(dt)
        # Note: this could be optimized, I don't think I need this for loop (TODO)

    def process_card_release(self):
        if self.active_player == PlayerType.OP:
            self.dragged_card.snap_back()
            self.dragged_card = None
            return
        if isinstance(
            self.dragged_card, (SpellCardController, ChangeStructureCardController)
        ):
            # If card is back to hand dont play it
            if not self.hand_me.rect.collidepoint(self.game.cursorpos):
                self._should_dragged_card_follow_mouse = False
                self._should_snap_back = False
                self.dragged_card.move_percent(0.15, 0.25)
                # self.dragged_card.scale_by(2.0)

                def _play_it():
                    self.play_card(self.dragged_card)

                timer = Timer(CARD_PLAYED_SHOW_TIME, _play_it)
                timer.start()
                # _play_it()
                return

        card_placed = False
        for row in range(self.board.n_rows):
            for col in range(self.board.n_cols):
                slot = self.board.grid.get(row, col)
                if slot.rect.collidepoint(self.game.cursorpos):
                    card_placed = self.board.can_play_card(self.dragged_card, row, col)
                    # print(f"card placed? {card_placed}")
                    if card_placed:
                        self.dragged_card.tween_scale_to(1.0)
                        # Remove card from hand
                        if self.dragged_card in self.hand_me.cards:
                            self.hand_me.cards.remove(self.dragged_card)
                            self.hand_me.reorder()
                        # So the card is played successfully
                        self.play_card(self.dragged_card, row, col)
                    break
            if card_placed:
                break

        if not card_placed or not self._should_snap_back:
            self.dragged_card.snap_back()

        self.dragged_card = None

    def play_card(
        self,
        card: CardControllerBase,
        row: int = None,
        col: int = None,
        who=PlayerType.ME,
    ):
        self.history.append(
            PHistoryEvent(
                kind=EventKind.CARD_PLAYED_FROM_HAND,
                who_made_it=who,
                card_id=card.uid,
                card_name=card.name,
                turn_number=self.turn_count,
            )
        )

        if isinstance(card, (SpellCardController, ChangeStructureCardController)):
            if card.card_model.effects.get("on_play"):
                ctx = EffectContext(
                    game_state=self.get_game_state(),
                    source_card=card,
                    game_manager=self,
                    board=self.board,
                    trigger="on_play",
                )
            for effect in card.card_model.effects["on_play"]:
                effect(ctx)
        else:
            # Trigger on_play effects with full context
            if card.card_model.effects.get("on_play"):
                ctx = EffectContext(
                    game_state=self.get_game_state(),
                    source_card=card,
                    game_manager=self,
                    board=self.board,
                    row=row,
                    col=col,
                    slot=self.board.grid.get(row, col),
                    trigger="on_play",
                )
                for effect in card.card_model.effects["on_play"]:
                    effect(ctx)

        # Trigger effects on other cards (e.g., reactive triggers)
        for other_card in self.board.cards:
            if other_card.card_model.effects.get("trigger"):
                trigger_ctx = EffectContext(
                    game_state=self.get_game_state(),
                    game_manager=self,
                    source_card=other_card,
                    board=self.board,
                    trigger="trigger",
                    # The card that was just played can be accessed if needed
                    target_card=card,
                    row=row,
                    col=col,
                )
                for effect in other_card.card_model.effects["trigger"]:
                    effect(trigger_ctx)

        if isinstance(card, CardController):
            self.board.play_card(card, row, col)
        else:
            # Remove from hand immediately to prevent handle_hands from calling snap_back
            if card in self.hand_me.cards:
                self.hand_me.cards.remove(card)
                self.hand_me.reorder()

            def _on_finish():
                print(f"onfinish of spell or changering {card} at {time.asctime()}")
                self.gy.add_card(card.card_model)
                self.dragged_card = None
                self._should_snap_back = True
                self._should_dragged_card_follow_mouse = True

            print(f"card tween started at {time.asctime()}")
            card.tween_pos_and_scale(
                self.gy.transform.position, 0.0, on_finish=_on_finish
            )
        self.active_player = (
            PlayerType.ME if self.active_player == PlayerType.OP else PlayerType.OP
        )
        # print(f"Now active player: {self.active_player}")
        self.active_player_index += 1
        self.active_player_index %= 2
        self.ply_count += 1
        if self.active_player_index == 0:
            self.turn_count += 1

    def play_op_card(self, card: Card, row: int, col: int):
        """I think it's fine that locally we don't know our opponent's hand"""

        if self.opponent_card_in_progress:
            return

        # if len(self.hand_op.cards) == 0:
        #     print("[ERROR] Opponent hand is empty! Cannot play card.")
        #     return

        self.opponent_card_in_progress = True
        c = self.hand_op.cards[0]
        print(f"[DEBUG] Selected card from opponent hand: {c.name}")
        c.from_card(card)
        c.tween_pos_and_scale(p.Vector2(self.game.GAME_W * 0.75, 120), 1.5)
        c.flip()

        def move_c_to_board(card_controller: CardController):
            print(
                f"[DEBUG] Timer callback - moving {card_controller.name} to board at ({row}, {col})"
            )
            # Remove the card from the hand before playing it
            if card_controller in self.hand_op.cards:
                self.hand_op.cards.remove(card_controller)
                self.hand_op.reorder()
            self.play_card(card_controller, row, col, who=PlayerType.OP)
            self.opponent_card_in_progress = False
            print("[DEBUG] Card played, opponent_card_in_progress reset to False")

        t = Timer(CARD_PLAYED_SHOW_TIME, lambda: move_c_to_board(c))
        t.start()
        print(f"[DEBUG] Timer started for {c.name}")

    def update(self, dt):
        super().update(dt)
        self.sc.update()
        # self.handle_hands(dt)

        # Debug: Press '1' to print game state as JSON
        if self.game.actions.get("action1") == 1:
            print("\n=== GAME STATE (Player View) ===")
            print(self.export_state_json(omni=False))
            print("\n=== OMNI GAME STATE (Server View) ===")
            print(self.export_state_json(omni=True))
            print("\n")

        if self.game.clicked_sx == 1:
            if self.hand_me.rect.collidepoint(self.game.cursorpos):
                self.hand_me_handle_click_sx(dt)
        if self.game.clicked_sx == -1:
            if self.dragged_card is not None:
                self.process_card_release()
        if self.game.clicked_dx == -1:
            if self.hand_me.rect.collidepoint(self.game.cursorpos):
                self.hand_me_handle_click_dx(dt)
            elif self.gy.rect.collidepoint(self.game.cursorpos):
                print(f"Clicked dx gy")
                self.game.push_state(
                    GraveyardViewState(
                        self.game,
                        {"cards": self.gy.cards},
                        previous_state=self.game.state_stack.top(),
                    )
                )
            for c in self.board.cards:
                if c.rect.collidepoint(self.game.cursorpos):
                    self.game.push_state(CardDetailedView(self.game, card=c.card_model))
        if self.dragged_card is None:
            self.handle_hands(dt)
        else:
            if self._should_dragged_card_follow_mouse:
                self.dragged_card.move(self.game.cursorpos)
            # Update dragged card so tweens sync transform.position -> rect.center
            self.dragged_card.update(dt)
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
            turn_count=self.turn_count,
            current_turn_player_id=self.players[
                self.active_player_index
            ].player_id,  # TODO: do this
            cards_in_hand_me=cards_in_hand_me,
            history=self.history,
            cards_in_board=cards_in_board,
            cards_in_gy_me=cards_in_gy_me,
            cards_in_gy_op=cards_in_gy_op,
            cards_in_deck_me=cards_in_deck_me,
            active_structure=str(self.structure.structure),
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
        # Render dragged/animating card on top if it's not in hand (already rendered there)
        if (
            self.dragged_card is not None
            and self.dragged_card not in self.hand_me.cards
        ):
            self.dragged_card.render(surface)


class OfflineGameManager(GameManager):
    def __init__(self, game, players):
        super().__init__(game, players)
        self.bot = Bot()
        self.bot.hand = [c.card_model for c in self.hand_op.cards]
