from controllers.controller import Controller
from engine.blackjack_basics import TURN, GameOutcome


class User:
    def __init__(self, user_id, controller: Controller):
        self.user_id = user_id
        self.controller = controller

    def make_turn(self, users_status: dict, users_cards: dict) -> TURN:
        # Any other logics
        return self.controller.make_turn(users_status, users_cards)

    def update_table(self, users_status: dict, users_cards: dict):
        # Any other logics
        self.controller.update_table(users_status, users_cards)

    def outcome_notify(self, game_score: int, status: GameOutcome):
        # Any other logics
        self.controller.outcome_notify(game_score, status)
