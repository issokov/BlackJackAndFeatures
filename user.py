from enum import Enum

from controllers import Controller, TURN


class UserStatus(Enum):
    in_game = 0
    enough = 1
    lose = 2
    blackjack = 3


class User:
    def __init__(self, user_id, controller: Controller):
        self.id = user_id
        self.controller = controller

    def make_turn(self, game_table) -> TURN:
        return self.controller.make_turn(game_table)

    def outcome_notify(self, game_score: int, status):
        print(f"Game is over user #{self.id}. Your score: {game_score}. Your status: {status.name}")

    def turn_result_notify(self, result: str):
        print(result)