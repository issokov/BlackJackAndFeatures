from card import VALUE, SUIT, Card
from random import shuffle as random_shuffle


class EmptyDeckException(Exception):
    pass


class Deck:
    def __init__(self, shuffle=True, is_small=False, use_joker=False):
        self.cards = []
        for suit in SUIT:
            for value in VALUE:
                if value is VALUE.joker:
                    if use_joker:
                        self.cards.append(Card(suit, value))
                else:
                    if not is_small:
                        self.cards.append(Card(suit, value))
                    elif value >= VALUE.six:
                        self.cards.append(Card(suit, value))
        if shuffle:
            random_shuffle(self.cards)

    def size(self) -> int:
        return len(self.cards)

    def pull_out(self) -> Card:
        if self.size() > 0:
            return self.cards.pop(0)
        raise EmptyDeckException("The deck is empty")
