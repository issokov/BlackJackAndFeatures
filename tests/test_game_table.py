from unittest import TestCase

from blackjack_basics import UserStatus, WrongRightsException
from card import *
from user import User
from controllers import ManualController
from game_table import BlackJackGameTable


class TestGameTable(TestCase):
    def setUp(self):
        self.user_1 = User(0, ManualController(0))
        self.user_2 = User(1, ManualController(1))
        self.game_table = BlackJackGameTable([self.user_1, self.user_2])

    def test_user_status(self):
        with self.subTest():
            self.assertEqual(self.game_table.get_status(self.user_1), UserStatus.in_game)
        with self.subTest():
            self.assertEqual(self.game_table.get_status(self.user_2), UserStatus.in_game)

        with self.subTest():
            self.game_table.add_card(self.user_1, Card(SUIT.diamonds, VALUE.ace))
            self.game_table.add_card(self.user_1, Card(SUIT.diamonds, VALUE.jack))
            self.assertEqual(self.game_table.get_status(self.user_1), UserStatus.blackjack)

        with self.subTest():
            self.game_table.add_card(self.user_2, Card(SUIT.hearts, VALUE.ten))
            self.game_table.add_card(self.user_2, Card(SUIT.hearts, VALUE.jack))
            self.game_table.add_card(self.user_2, Card(SUIT.hearts, VALUE.two))
            self.assertEqual(self.game_table.get_status(self.user_2), UserStatus.lose)

    def test_both_enough(self):
        self.game_table.add_card(self.user_1, Card(SUIT.hearts, VALUE.king))
        self.game_table.add_card(self.user_2, Card(SUIT.hearts, VALUE.ace))
        self.game_table.set_status(self.user_1, UserStatus.enough)
        self.game_table.set_status(self.user_2, UserStatus.enough)

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
            self.game_table.add_card(self.user_1, Card(SUIT.hearts, VALUE.king))
            self.game_table.add_card(self.user_1, Card(SUIT.hearts, VALUE.ten))
            self.game_table.set_status(self.user_1, UserStatus.enough)
            with self.assertRaises(WrongRightsException):
                self.game_table.add_card(self.user_1, Card(SUIT.hearts, VALUE.two))

        with self.subTest():
            self.game_table.add_card(self.user_2, Card(SUIT.hearts, VALUE.king))
            self.game_table.add_card(self.user_2, Card(SUIT.hearts, VALUE.ten))
            self.game_table.add_card(self.user_2, Card(SUIT.hearts, VALUE.two))
            with self.assertRaises(WrongRightsException):
                self.game_table.add_card(self.user_2, Card(SUIT.hearts, VALUE.two))
