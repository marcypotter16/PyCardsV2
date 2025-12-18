from Bot import Bot
from GameManager import GameManager
from PModels import Player, PlayerType
from SocketManager import SocketManager
from States.HistoryViewState import HistoryViewState
from States.MainMenu import MainMenu
from States.State import State
from UI.Button import TextButton
from UI.Label import Label

# from Utils.Timer import Timer
from threading import Timer


class OnlineGameManagerTestState(State):
    def __init__(
        self, game, data: object | None = None, layer="foreground", previous_state=None
    ):
        super().__init__(game, data, layer, previous_state=previous_state)
        self.gm = None
        if data:
            self.socket_manager: SocketManager = data["socket_manager"]
            self.socket_manager.send_sync({"type": "start_game_ok"})
            self.gm = GameManager(self.game)
        else:
            self.lab_err_no_socket = Label(
                self.canvas,
                center=self.game.GAME_CENTER,
                text="Connection error, returning to main menu",
                fg_color=(255, 255, 255),
            )

            def on_timer_finish():
                self.game.state_stack.clear()
                self.game.state_stack.push(MainMenu(self.game))

            timer = Timer(interval=5.0, function=on_timer_finish)
            timer.start()

    def update(self, delta_time):
        super().update(delta_time)
        if self.gm:
            self.gm.update(delta_time)

    def render(self, surf):
        super().render(surf)
        if self.gm:
            self.gm.render(surf)


class OfflineGameManagerTestState(State):
    def __init__(
        self,
        game,
        data=None,
        layer="foreground",
        bg_color=(0, 0, 0),
        previous_state=None,
    ):
        super().__init__(game, data, layer, bg_color, previous_state)
        player = Player(player_id="player", player_name="player")
        bot = Player(player_id="bot", player_name="bot")
        self.gm = GameManager(game, players=[player, bot])
        # Pass the HandController so the bot can dynamically access cards
        self.bot = Bot(self.gm.hand_op)
        self.turn_info_label = Label(
            self.canvas,
            x=self.game.GAME_W * 0.75 - 100,
            y=0,
            width=200,
            height=20,
            fg_color=(255, 255, 255),
            bg_color=(50, 50, 50),
            text=f"Turn Count: {self.gm.turn_count}",
            corner_radius=0,
        )
        self.turn_info_label2 = Label(
            self.canvas,
            x=self.game.GAME_W * 0.75 - 100,
            y=25,
            width=200,
            height=20,
            fg_color=(255, 255, 255),
            bg_color=(50, 50, 50),
            text=f"Active player: {self.gm.active_player}",
            corner_radius=0,
        )

        self.open_history = TextButton(
            self.canvas,
            center=(self.game.GAME_W * 0.15, self.game.GAME_H * 0.75),
            text="Open history",
            command=lambda: self.game.push_state(
                HistoryViewState(game, {"history": self.gm.history})
            ),
        )
        self.open_history.pack()

    def state_machine(self):
        if self.gm.active_player == PlayerType.OP:
            card, row, col = self.bot.think(self.gm.board)
            self.gm.play_op_card(card, row, col)

    def update(self, delta_time):
        super().update(delta_time)
        self.gm.update(delta_time)
        self.state_machine()
        self.turn_info_label.set_text(f"Turn Count: {self.gm.turn_count}")
        self.turn_info_label2.set_text(f"Active player: {self.gm.active_player}")
        self.debug_label.set_text(
            f"mouse: {(100*float(self.game.cursorpos[0])/self.game.GAME_W):.2f}%, {(100*float(self.game.cursorpos[1])/self.game.GAME_H):.2f}%"
        )

    def render(self, surface):
        super().render(surface)
        self.gm.render(surface)
