from abc import ABC, abstractmethod
from collections import defaultdict
from copy import deepcopy
from itertools import chain

from blackjack_basics import TURN, get_score, GameOutcome, UserStatus
from deck import Deck


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
        self.my_cards = []

    def show_table(self, users_status: dict, users_cards: dict):
        for user_id in users_status.keys():
            print(f"User {'YOU' if self.user_id == user_id else user_id} has '{users_status[user_id].name}' status")
            print("\n".join(map(lambda x: str(x), users_cards[user_id])))
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
        return TURN.enough if answer == 'e' else TURN.hit_me

    def outcome_notify(self, game_score: int, status):
        print(f"Game is over user #{self.user_id}. Your score: {game_score}. Your status: {status.name}")


def recreate_deck(users_cards: dict):
    was_pulled = chain.from_iterable(users_cards.values())
    deck = Deck(shuffle=True, is_small=False, use_joker=False)
    for card in was_pulled:
        deck.cards.remove(card)
    return deck


def eval_scores(users_cards: dict, score_count=1000):
    result = defaultdict(list)
    for user_id, user_cards in users_cards.items():
        for _ in range(score_count):
            curr_deck = recreate_deck(users_cards)
            curr_cards = deepcopy(user_cards)
            curr_cards.append(curr_deck.pull_out())
            result[user_id].append(get_score(curr_cards))
    return result


class IntelligenzaArtificialeControllore(Controller):
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
