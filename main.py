from Game import Game
from GameObjects.Database import CARD_DATABASE
from States.RingTestState import RingTestState
from States.CardDetailedView import CardDetailedView
from States.DeckTestState import DeckTestState
from States.BoardTestState import BoardTestState
from States.CardTestState import CardTestState
from States.GameManagerTestState import (
    OfflineGameManagerTestState,
    OnlineGameManagerTestState,
)
from States.HandTestState import HandTestState
from States.MainMenu import MainMenu
from States.PauseTestState import PauseTestState
from States.WheelTestState import WheelTestState
from Utils.Colors import BLACK, GRAY, WHITE

g: Game = Game()
# g.load_state(BezierTestState(g))
# c = CardTestState(g)
# c.from_card(CARD_DATABASE["goth_girl"])
# c.card.move(g.SCREEN_CENTER)
# c = HandTestState(g)
# c = OnlineGameManagerTestState(g)
c = OfflineGameManagerTestState(g)
# c = WheelTestState(g)
# c = PauseTestState(g)
# c = CardDetailedView(g)
# c = MainMenu(g)
# c = RingTestState(g, bg_color=GRAY)
# c.local_testing = True
g.load_state(c)
g.game_loop()
