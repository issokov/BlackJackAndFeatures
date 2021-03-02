from enum import Enum
from typing import List

from card import Card, VALUE


class TURN(Enum):
    hit_me = 0
    enough = 1


class GameOutcome(Enum):
    loser = 0
    draw = 1
    winner = 2


class WrongDeckConfiguration(Exception):
    pass


class WrongRightsException(Exception):
    pass


def get_score(cards: List[Card]):
    score = 0
    value_to_score = {
        VALUE.two: 2, VALUE.three: 3, VALUE.four: 4, VALUE.five: 5,
        VALUE.six: 6, VALUE.seven: 7, VALUE.eight: 8, VALUE.nine: 9,
        VALUE.ten: 10, VALUE.jack: 10, VALUE.queen: 10, VALUE.king: 10
    }
    for card in cards:
        if card.value is not VALUE.ace:
            score += value_to_score[card.value]
        elif card.value is VALUE.ace:
            score += 1 if score + 11 > 21 else 11
        else:
            raise WrongDeckConfiguration
    return score
