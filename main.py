from Game import Game
from Models.CardDatabase import CARD_DATABASE
from States.CardTestState import CardTestState

g: Game = Game()
# g.load_state(BezierTestState(g))
c = CardTestState(g)
c.from_card(CARD_DATABASE["goth_girl"])
c.card.move_center(g.SCREEN_CENTER)
c.card.drop()
g.load_state(c)
g.game_loop()