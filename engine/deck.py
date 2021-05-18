from random import shuffle as random_shuffle
from .card import VALUE, SUIT, Card


class EmptyDeckException(Exception):
    pass


class Deck:
    def __init__(self, str_deck=None, shuffle=True, is_small=False):
        self.cards = []
        if str_deck:
            for str_card in str_deck.split(','):
                suit, value = str_card.split('-')
                self.cards.append(Card(SUIT(int(suit)), VALUE(int(value))))
        else:
            for suit in SUIT:
                for value in VALUE:
                    if not is_small:
                        self.cards.append(Card(suit, value))
                    elif value >= VALUE.SIX:
                        self.cards.append(Card(suit, value))
            if shuffle:
                random_shuffle(self.cards)

    def size(self) -> int:
        return len(self.cards)

    def pull_out(self) -> Card:
        if self.size() > 0:
            return self.cards.pop(0)
        raise EmptyDeckException("The deck is empty")

    def __str__(self):
        return ','.join(f'{card.suit.value}-{card.value.value}' for card in self.cards)
