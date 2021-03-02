from deck import Deck
from user import User, UserStatus
from game_table import BlackJackGameTable
from blackjack_basics import GameOutcome, TURN, WrongRightsException


class Engine:
    def __init__(self):
        self.users = []
        self.deck = None
        self.game_table: BlackJackGameTable = None
        self.is_running = False

    def add_user(self, user: User):
        self.users.append(user)

    def start(self):
        self.deck = Deck()
        self.game_table = BlackJackGameTable(self.users)

        self.is_running = True
        for user in self.game_table.get_active_users():
            self.game_table.add_card(user, self.deck.pull_out())
            self.game_table.add_card(user, self.deck.pull_out())

        while self.is_running:
            for user in self.game_table.get_active_users():
                turn = user.make_turn(self.game_table.users_status, self.game_table.users_cards)
                self.process_turn(user, turn)
                self.update_users()
            if len(self.game_table.get_active_users()) == 0:
                self.is_running = False

        outcomes = self.generate_outcomes()
        for user in self.users:
            user.outcome_notify(*outcomes[user.id])

    def update_users(self):
        for user in self.users:
            user.update_table(self.game_table.users_status, self.game_table.users_cards)

    def generate_outcomes(self):
        result = dict()
        scores = [self.game_table.get_user_score(user) for user in self.users]
        max_score = max(scores, key=lambda x: 0 if x > 21 else x)
        if max_score > 21:
            max_score = 0
        winners_count = scores.count(max_score)
        for score, user in zip(scores, self.users):
            result[user.id] = (score, GameOutcome.loser)
            if score == max_score:
                result[user.id] = (score, GameOutcome.winner if winners_count == 1 else GameOutcome.draw)
        return result

    def process_turn(self, user: User, turn: TURN):
        if user in self.game_table.get_active_users():
            if turn is TURN.hit_me:
                new_card = self.deck.pull_out()
                self.game_table.add_card(user, new_card)
            elif turn is TURN.enough:
                self.game_table.set_status(user, UserStatus.enough)
        else:
            raise WrongRightsException("User is not in game")
