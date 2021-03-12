from unittest import TestCase

from engine.blackjack_basics import UserStatus, WrongRightsException
from engine.card import Card, SUIT, VALUE
from engine.user import User
from engine.game_table import BlackJackGameTable

from controllers.manual_controller import ManualController


class TestGameTable(TestCase):
    def setUp(self):
        self.user_1 = User(0, ManualController(0))
        self.user_2 = User(1, ManualController(1))
        self.game_table = BlackJackGameTable([self.user_1, self.user_2])

    def test_user_status(self):
        with self.subTest():
            self.assertEqual(self.game_table.get_status(self.user_1), UserStatus.IN_GAME)
        with self.subTest():
            self.assertEqual(self.game_table.get_status(self.user_2), UserStatus.IN_GAME)

        with self.subTest():
            self.game_table.add_card(self.user_1, Card(SUIT.DIAMONDS, VALUE.ACE))
            self.game_table.add_card(self.user_1, Card(SUIT.DIAMONDS, VALUE.JACK))
            self.assertEqual(self.game_table.get_status(self.user_1), UserStatus.BLACKJACK)

        with self.subTest():
            self.game_table.add_card(self.user_2, Card(SUIT.HEARTS, VALUE.TEN))
            self.game_table.add_card(self.user_2, Card(SUIT.HEARTS, VALUE.JACK))
            self.game_table.add_card(self.user_2, Card(SUIT.HEARTS, VALUE.TWO))
            self.assertEqual(self.game_table.get_status(self.user_2), UserStatus.LOSE)

    def test_both_enough(self):
        self.game_table.add_card(self.user_1, Card(SUIT.HEARTS, VALUE.KING))
        self.game_table.add_card(self.user_2, Card(SUIT.HEARTS, VALUE.ACE))
        self.game_table.set_status(self.user_1, UserStatus.ENOUGH)
        self.game_table.set_status(self.user_2, UserStatus.ENOUGH)

        with self.subTest():
            self.assertListEqual(self.game_table.get_active_users(), [])

        with self.subTest():
            self.assertEqual(self.game_table.get_user_score(self.user_1), 10)

        with self.subTest():
            self.assertEqual(self.game_table.get_user_score(self.user_2), 11)

        with self.subTest():
            self.assertListEqual(self.game_table.get_users(), [self.user_1, self.user_2])

    def test_forbid_add_card_when_unactive(self):
        with self.subTest():
            self.game_table.add_card(self.user_1, Card(SUIT.HEARTS, VALUE.KING))
            self.game_table.add_card(self.user_1, Card(SUIT.HEARTS, VALUE.TEN))
            self.game_table.set_status(self.user_1, UserStatus.ENOUGH)
            with self.assertRaises(WrongRightsException):
                self.game_table.add_card(self.user_1, Card(SUIT.HEARTS, VALUE.TWO))

        with self.subTest():
            self.game_table.add_card(self.user_2, Card(SUIT.HEARTS, VALUE.KING))
            self.game_table.add_card(self.user_2, Card(SUIT.HEARTS, VALUE.TEN))
            self.game_table.add_card(self.user_2, Card(SUIT.HEARTS, VALUE.TWO))
            with self.assertRaises(WrongRightsException):
                self.game_table.add_card(self.user_2, Card(SUIT.HEARTS, VALUE.TWO))
