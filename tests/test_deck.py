from unittest import TestCase

from engine.deck import Deck, EmptyDeckException
from engine.card import Card, SUIT, VALUE


class TestDeck(TestCase):

    def test_deck_correctness(self):
        deck = Deck(shuffle=True, is_small=False)
        cards = [deck.pull_out() for _ in range(52)]
        with self.subTest():
            with self.assertRaises(EmptyDeckException):
                deck.pull_out()
        with self.subTest():
            sorted_cards = []
            for suit in SUIT:
                for value in VALUE:
                    sorted_cards.append(Card(suit, value))
            self.assertNotEqual(cards, sorted_cards)

    def test_different_card_orders(self):
        first_deck = Deck(shuffle=True, is_small=False)
        second_deck = Deck(shuffle=True, is_small=False)
        first_deck_cards = [first_deck.pull_out() for _ in range(52)]
        second_deck_cards = [second_deck.pull_out() for _ in range(52)]
        self.assertNotEqual(first_deck_cards, second_deck_cards)
