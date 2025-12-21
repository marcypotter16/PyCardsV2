from GameObjects.Card.Card import CardController
from GameObjects.Hand import HandController
from States.State import State
from Utils.Timer import SpacedCallback


class HandTestState(State):
    def __init__(self, game, data: object | None = None, layer="foreground"):
        super().__init__(game, data, layer)
        self.hand = HandController(self.game, center=self.game.GAME_CENTER)
        # spaced_call = SpacedCallback(self.spawn_and_add_card_to_hand, interval=1)
        spaced_call = SpacedCallback(self.spawn_and_add_card_to_hand, 1)
        self.game.timer_manager.add_timer(spaced_call)

    def spawn_and_add_card_to_hand(self):
        c = CardController(self.game)
        self.hand.add_card(c)

    def update(self, delta_time):
        super().update(delta_time)
        self.hand.update(delta_time)

    def render(self, surface):
        super().render(surface)
        self.hand.render(surface)
