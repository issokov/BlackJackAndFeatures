from unittest import TestCase
from unittest.mock import Mock

from engine.card import Card, SUIT, VALUE
from controllers.manual_controller import ManualController
from engine.deck import Deck
from engine.engine import Engine
from engine.user import User
from engine.blackjack_basics import TURN, UserStatus, GameOutcome


class TestEngine(TestCase):
    def setUp(self):
        self.controller_1 = ManualController(0)
        self.controller_2 = ManualController(1)
        self.user_1 = User(0, self.controller_1)
        self.user_2 = User(1, self.controller_2)
        self.engine = Engine()
        self.engine.add_user(self.user_1)
        self.engine.add_user(self.user_2)

    def test_general(self):
        self.engine.deck = Deck(shuffle=False, is_small=False)

        self.engine.deck.pull_out = Mock(return_value=Card(SUIT.clubs, VALUE.six))
        self.engine.init_game()
        with self.subTest():
            self.assertEqual(len(self.engine.bj_gametable.get_cards(self.user_1)), 2)
        with self.subTest():
            self.assertEqual(len(self.engine.bj_gametable.get_cards(self.user_2)), 2)
        with self.subTest():
            self.assertTrue(self.engine._is_inited)
        with self.subTest():
            self.assertEqual(self.engine.deck.pull_out.call_count, 4)

        self.controller_1.make_turn = Mock(return_value=TURN.hit_me)
        self.controller_2.make_turn = Mock(return_value=TURN.hit_me)
        self.controller_1.update_table = Mock()
        self.controller_2.update_table = Mock()

        self.engine.one_tick()
        with self.subTest():
            self.controller_1.make_turn.assert_called_once()
        with self.subTest():
            self.assertEqual(self.controller_1.update_table.call_count, 2)
        with self.subTest():
            self.controller_2.make_turn.assert_called_once()
        with self.subTest():
            self.assertEqual(self.controller_2.update_table.call_count, 2)
        with self.subTest():
            self.assertEqual(self.engine.deck.pull_out.call_count, 6)
        with self.subTest():
            self.assertFalse(self.engine.is_ended())

        self.engine.deck.pull_out.side_effect = [Card(SUIT.clubs, VALUE.three),
                                                 Card(SUIT.clubs, VALUE.two),
                                                 Card(SUIT.clubs, VALUE.ace)]
        self.controller_1.make_turn.return_value = TURN.hit_me
        self.controller_2.make_turn.side_effect = [TURN.hit_me, TURN.hit_me]

        self.engine.one_tick()
        with self.subTest():
            self.assertEqual(self.engine.bj_gametable.get_status(self.user_1), UserStatus.blackjack)
        with self.subTest():
            self.assertEqual(self.engine.bj_gametable.get_status(self.user_2), UserStatus.in_game)
        with self.subTest():
            self.assertFalse(self.engine.is_ended())

        self.controller_1.outcome_notify = Mock()
        self.controller_2.outcome_notify = Mock()
        self.engine.one_tick()
        with self.subTest():
            self.assertEqual(self.controller_1.make_turn.call_count + 1, self.controller_2.make_turn.call_count)
        with self.subTest():
            self.assertTrue(self.engine.is_ended())

        self.engine.outcomes_notify(self.engine.generate_outcomes())
        with self.subTest():
            self.controller_1.outcome_notify.assert_called_once_with(21, GameOutcome.draw)
        with self.subTest():
            self.controller_2.outcome_notify.assert_called_once_with(21, GameOutcome.draw)