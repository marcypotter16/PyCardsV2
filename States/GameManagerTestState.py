from GameManager import GameManager
from PModels import Player
from SocketManager import SocketManager
from States.MainMenu import MainMenu
from States.State import State
from UI.Label import Label

# from Utils.Timer import Timer
from threading import Timer


class OnlineGameManagerTestState(State):
    def __init__(self, game, data: object | None = None, layer="foreground"):
        super().__init__(game, data, layer)
        self.gm = None
        if data:
            self.socket_manager: SocketManager = data["socket_manager"]
            self.socket_manager.send_sync({"type": "start_game_ok"})
            self.gm = GameManager(self.game)
        else:
            self.lab_err_no_socket = Label(
                self.canvas,
                center=self.game.SCREEN_CENTER,
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
    def __init__(self, game, data=None, layer="foreground"):
        super().__init__(game, data, layer)
        player = Player(player_id="player", player_name="player")
        bot = Player(player_id="bot", player_name="bot")
        self.gm = GameManager(game, players=[player, bot])

    def update(self, delta_time):
        super().update(delta_time)
        self.gm.update(delta_time)

    def render(self, surface):
        super().render(surface)
        self.gm.render(surface)
