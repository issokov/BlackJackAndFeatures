from controllers.controller import Controller, eval_scores
from engine.blackjack_basics import TURN, UserStatus, get_score, GameOutcome


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
        max_score, expect_max, my_score = 0, 0, get_score(users_cards[self.user_id])
        evaluated_scores = eval_scores(users_cards, score_count=self._evaluations_count)
        for user_id, user_cards in users_cards.items():
            if user_id != self.user_id:
                score = get_score(user_cards)
                max_score = max(max_score, score if score <= 21 else 0)
                if users_status[user_id] not in [UserStatus.ENOUGH, UserStatus.LOSE]:
                    expect_score = sorted(evaluated_scores[user_id])[self._evaluations_count // 2]
                    expect_max = max(expect_score if expect_score <= 21 else 0, expect_max)
        my_expected = sorted(evaluated_scores[self.user_id])[self._evaluations_count // 2]
        print(f"Intelligenza Artificiale:\n\tscore: {my_score}\n\tmy_expected: {my_expected}"
              f"\n\tmax_score: {max_score}\n\tenemy_expected: {expect_max}")
        print("\tSo...")

        if my_score < max_score or (my_score < expect_max and my_expected <= 21):
            print("\tHit me!")
            return TURN.HIT_ME
        print("\tEnough.")
        return TURN.ENOUGH

    def outcome_notify(self, score: int, status: GameOutcome):
        print(f"AI {self.user_id} SCORE: {score}\nAI {self.user_id}STATUS: {status.name}")
