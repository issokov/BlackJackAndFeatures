from engine.blackjack_basics import get_score, TURN, GameOutcome
from controllers.controller import Controller


class ManualController(Controller):
    def __init__(self, user_id: int):
        super().__init__(user_id)
        self.my_cards = []

    def show_table(self, users_status: dict, users_cards: dict):
        for user_id in users_status.keys():
            print(f"User {'YOU' if self.user_id == user_id else user_id}"
                  f" has '{users_status[user_id].name}' status")
            print("\n".join(map(str, users_cards[user_id])))
            print(f"Score: {get_score(users_cards[user_id])}")
            print('------------------------------')

    def update_table(self, users_status: dict, users_cards: dict):
        if self.my_cards != users_cards[self.user_id] and self.my_cards:
            print(f"User {self.user_id} pulled the {users_cards[self.user_id][-1]} card")
        self.my_cards = users_cards[self.user_id]

    def make_turn(self, users_status: dict, users_cards: dict) -> TURN:
        self.show_table(users_status, users_cards)
        answer = '?'
        print("Your turn (hit me / enough): write 'h' or 'e'")
        while answer not in ['e', 'h']:
            answer = input().lower()
        return TURN.ENOUGH if answer == 'e' else TURN.HIT_ME

    def outcome_notify(self, score: int, status: GameOutcome):
        print(f"Game is over user #{self.user_id}. Your score: {score}. Your status: {status.name}")
