from abc import ABC, abstractmethod
from enum import Enum


class TURN(Enum):
    hit_me = 0
    enough = 1


class Controller(ABC):
    def __init__(self, user_id: int):
        self.user_id = user_id

    @abstractmethod
    def make_turn(self, game_table) -> TURN:
        pass


class ManualController(Controller):
    def __init__(self, user_id: int):
        super().__init__(user_id)

    def make_turn(self, game_table) -> TURN:
        for _ in range(10):
            print('\n')
        for user in game_table.users:
            print(f"User: {user.id if self.user_id != user.id else 'You'}. Score: {game_table.get_user_score(user)}")
            for card in game_table.get_cards(user):
                print(f"\t{card}")
        answer = '?'
        print("Your turn (hit me / enough): write 'h' or 'e'")
        while answer not in ['e', 'h']:
            answer = input().lower()
        return TURN.enough if answer == 'e' else TURN.hit_me
