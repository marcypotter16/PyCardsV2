from GameObjects.Database import CARD_DATABASE
from GameObjects.Deck import DeckController
from States.State import State


class DeckTestState(State):
    def __init__(self, game, data: object | None = None, layer="foreground"):
        super().__init__(game, msg, layer)
        self.deck = DeckController(self.game, self)
        self.deck.move(self.game.GAME_CENTER)
        for _ in range(10):
            self.deck.add_card(CARD_DATABASE["goth_girl"])

    def update(self, delta_time):
        super().update(delta_time)
        self.deck.update(delta_time)

    def render(self, surface):
        super().render(surface)
        self.deck.render(surface)
