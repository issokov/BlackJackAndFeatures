from engine.blackjack_basics import TURN, get_score, UserStatus, GameOutcome
from controllers.controller import Controller, eval_scores


class AIController(Controller):
    def __init__(self, user_id: int):
        super().__init__(user_id)
        self.my_cards = []
        self._greeting = True
        self._evaluations_count = 1000

    def update_table(self, users_status: dict, users_cards: dict):
        if not self._greeting:
            print("Intelligenza Artificiale:\n\tEXTERMINATE! EXTERMINATE!\n\tKhm\n\tHello!")
            self._greeting = True
        if self.my_cards != users_cards[self.user_id] and self.my_cards:
            print(f"AI pulled the {users_cards[self.user_id][-1]} card")
        self.my_cards = users_cards[self.user_id]

    def make_turn(self, users_status: dict, users_cards: dict) -> TURN:
        max_score, expected_max_score, my_score = 0, 0, get_score(users_cards[self.user_id])
        evaluated_scores = eval_scores(users_cards, score_count=self._evaluations_count)
        for user_id, user_cards in users_cards.items():
            if user_id != self.user_id:
                score = get_score(user_cards)
                max_score = max(max_score, score if score <= 21 else 0)
                if users_status[user_id] not in [UserStatus.enough, UserStatus.lose]:
                    expected_score = sorted(evaluated_scores[user_id])[self._evaluations_count // 2]
                    expected_max_score = max(expected_score if expected_score <= 21 else 0, expected_max_score)
        my_expected = sorted(evaluated_scores[self.user_id])[self._evaluations_count // 2]
        my_expected = my_expected if my_expected <= 21 else 0
        print(f"Intelligenza Artificiale:\n\tscore: {my_score}\n"
              f"\tmy_expected: {my_expected}\n\tmax_score: {max_score}\n\tenemy_expected: {expected_max_score}")
        print("\tSo...")

        if my_score < max_score or (my_score < expected_max_score and my_expected <= 21):
            print("\tHit me!")
            return TURN.hit_me
        print("\tEnough.")
        return TURN.enough

    def outcome_notify(self, score: int, status: GameOutcome):
        print(f"AI {self.user_id} SCORE: {score}\nAI {self.user_id}STATUS: {status.name}")
