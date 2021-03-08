from enum import Enum, unique


@unique
class VALUE(Enum):
    two = 0
    three = 1
    four = 2
    five = 3
    six = 4
    seven = 5
    eight = 6
    nine = 7
    ten = 8
    jack = 9
    queen = 10
    king = 11
    ace = 12
    joker = 13


@unique
class SUIT(Enum):
    hearts = 0
    diamonds = 1
    clubs = 2
    spades = 3


class Card:
    def __init__(self, suit: SUIT, value: VALUE):
        self.suit = suit
        self.value = value

    def __str__(self):
        return f"{self.suit.name} {self.value.name}"

    def __eq__(self, other):
        return self.suit == other.suit and self.value == other.value
