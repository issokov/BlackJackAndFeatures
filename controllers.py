from abc import ABC, abstractmethod

from blackjack_basics import TURN, get_score, GameOutcome


class Controller(ABC):
    def __init__(self, user_id: int):
        self.user_id = user_id

    @abstractmethod
    def update_table(self, users_status: dict, users_cards: dict):
        pass

    @abstractmethod
    def make_turn(self, users_status: dict, users_cards: dict) -> TURN:
        pass

    @abstractmethod
    def outcome_notify(self, score: int, status: GameOutcome):
        pass


class ManualController(Controller):
    def __init__(self, user_id: int):
        super().__init__(user_id)
        self.my_turn = False

    def update_table(self, users_status: dict, users_cards: dict):
        if self.my_turn:
            for user_id in users_status.keys():
                print(f"User {'YOU' if self.user_id == user_id else user_id} has '{users_status[user_id].name}' status")
                print("\n".join(map(lambda x: str(x), users_cards[user_id])))
                print(f"Score: {get_score(users_cards[user_id])}")
                print('------------------------------')

    def make_turn(self, users_status: dict, users_cards: dict) -> TURN:
        self.my_turn = True
        self.update_table(users_status, users_cards)
        answer = '?'
        print("Your turn (hit me / enough): write 'h' or 'e'")
        while answer not in ['e', 'h']:
            answer = input().lower()
        self.my_turn = False
        return TURN.enough if answer == 'e' else TURN.hit_me

    def outcome_notify(self, game_score: int, status):
        print(f"Game is over user #{self.user_id}. Your score: {game_score}. Your status: {status.name}")
