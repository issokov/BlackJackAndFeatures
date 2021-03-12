from enum import Enum, unique


@unique
class VALUE(Enum):
    TWO = 0
    THREE = 1
    FOUR = 2
    FIVE = 3
    SIX = 4
    SEVEN = 5
    EIGHT = 6
    NINE = 7
    TEN = 8
    JACK = 9
    QUEEN = 10
    KING = 11
    ACE = 12


@unique
class SUIT(Enum):
    HEARTS = 0
    DIAMONDS = 1
    CLUBS = 2
    SPADES = 3


class Card:
    def __init__(self, suit: SUIT, value: VALUE):
        self.suit = suit
        self.value = value

    def __str__(self):
        return f"{self.suit.name} {self.value.name}"

    def __eq__(self, other):
        return self.suit == other.suit and self.value == other.value
