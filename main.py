from Game import Game
from GameObjects.Database import CARD_DATABASE
from States.CardDetailedView import CardDetailedView
from States.DeckTestState import DeckTestState
from States.BoardTestState import BoardTestState
from States.CardTestState import CardTestState
from States.GameManagerTestState import GameManagerTestState
from States.HandTestState import HandTestState
from States.MainMenu import MainMenu
from States.PauseTestState import PauseTestState
from States.WheelTestState import WheelTestState

g: Game = Game()
# g.load_state(BezierTestState(g))
# c = CardTestState(g)
# c.from_card(CARD_DATABASE["goth_girl"])
# c.card.move(g.SCREEN_CENTER)
# c = HandTestState(g)
# c = GameManagerTestState(g)
# c = WheelTestState(g)
# c = PauseTestState(g)
# c = CardDetailedView(g)
c = MainMenu(g)
g.load_state(c)
g.game_loop()
