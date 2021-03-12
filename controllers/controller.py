from abc import ABC
from collections import defaultdict
from copy import deepcopy
from itertools import chain

from engine.blackjack_basics import TURN, get_score, GameOutcome
from engine.deck import Deck


class Controller(ABC):
    def __init__(self, user_id: int):
        self.user_id = user_id

    def update_table(self, users_status: dict, users_cards: dict):
        pass

    def make_turn(self, users_status: dict, users_cards: dict) -> TURN:
        pass

    def outcome_notify(self, score: int, status: GameOutcome):
        pass


def recreate_deck(users_cards: dict):
    was_pulled = chain.from_iterable(users_cards.values())
    deck = Deck(shuffle=True, is_small=False)
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
