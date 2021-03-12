from copy import deepcopy

from .deck import Deck
from .user import User
from .game_table import BlackJackGameTable
from .blackjack_basics import GameOutcome, TURN, WrongRightsException, UserStatus


class GameNotInitedException(Exception):
    pass


class Engine:
    def __init__(self):
        self.users = []
        self.deck = Deck(shuffle=True, is_small=False)
        self.bj_gametable = None
        self._is_inited = False

    def add_user(self, user: User):
        self.users.append(user)

    def init_game(self):
        self.bj_gametable = BlackJackGameTable(self.users)
        for user in self.bj_gametable.get_active_users():
            self.bj_gametable.add_card(user, self.deck.pull_out())
            self.bj_gametable.add_card(user, self.deck.pull_out())
        self._is_inited = True

    def get_active_users(self):
        return self.bj_gametable.get_active_users()

    def get_game_table_info(self):
        return deepcopy(self.bj_gametable.users_status), deepcopy(self.bj_gametable.users_cards)

    def one_tick(self):
        if not self._is_inited:
            raise GameNotInitedException("Before .one_tick() you should call .init_game()")
        for user in self.bj_gametable.get_active_users():
            turn = user.make_turn(*self.get_game_table_info())
            if self.process_turn(user, turn):
                self.update_users()
            else:
                break
            if self.is_ended():
                return

    def is_ended(self) -> bool:
        alive = self.bj_gametable.get_active_users()
        if not len(alive):
            return True
        if len(alive) == 1:
            scores = [self.bj_gametable.get_user_score(user) for user in self.users]
            max_score = max(scores, key=lambda x: 0 if x > 21 else x)
            if max_score == self.bj_gametable.get_user_score(alive[0]):
                return True

        one_not_looser = False
        for status in self.bj_gametable.users_status.values():
            if status != UserStatus.lose:
                if one_not_looser:
                    return False
                one_not_looser = True
        return one_not_looser

    def update_users(self):
        for user in self.users:
            user.update_table(deepcopy(self.bj_gametable.users_status), deepcopy(self.bj_gametable.users_cards))

    def generate_outcomes(self):
        result = dict()
        scores = [self.bj_gametable.get_user_score(user) for user in self.users]
        max_score = max(scores, key=lambda x: 0 if x > 21 else x)
        if max_score > 21:
            max_score = 0
        winners_count = scores.count(max_score)
        for score, user in zip(scores, self.users):
            result[user.id] = (score, GameOutcome.loser)
            if score == max_score:
                result[user.id] = (score, GameOutcome.winner if winners_count == 1 else GameOutcome.draw)
        return result

    def outcomes_notify(self, outcomes: dict):
        for user in self.users:
            user.outcome_notify(*outcomes[user.id])

    def process_turn(self, user: User, turn: TURN):
        if user in self.bj_gametable.get_active_users():
            if turn is TURN.hit_me:
                new_card = self.deck.pull_out()
                self.bj_gametable.add_card(user, new_card)
            elif turn is TURN.enough:
                self.bj_gametable.set_status(user, UserStatus.enough)
            else:
                return False
            return True
        elif turn is not None:
            raise WrongRightsException(f"User {user.id} is not in game")