from enum import Enum
from typing import List

from engine.card import Card, VALUE


class UserStatus(Enum):
    IN_GAME = 0
    ENOUGH = 1
    LOSE = 2
    BLACKJACK = 3


class TURN(Enum):
    HIT_ME = 0
    ENOUGH = 1


class GameOutcome(Enum):
    LOSER = 0
    DRAW = 1
    WINNER = 2


class WrongDeckConfiguration(Exception):
    pass


class WrongRightsException(Exception):
    pass


def get_score(cards: List[Card]):
    score = 0
    value_to_score = {
        VALUE.TWO: 2, VALUE.THREE: 3, VALUE.FOUR: 4, VALUE.FIVE: 5,
        VALUE.SIX: 6, VALUE.SEVEN: 7, VALUE.EIGHT: 8, VALUE.NINE: 9,
        VALUE.TEN: 10, VALUE.JACK: 10, VALUE.QUEEN: 10, VALUE.KING: 10
    }
    for card in cards:
        if card.value is not VALUE.ACE:
            score += value_to_score[card.value]
        elif card.value is VALUE.ACE:
            score += 1 if score + 11 > 21 else 11
        else:
            raise WrongDeckConfiguration
    return score
