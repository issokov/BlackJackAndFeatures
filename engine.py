from enum import Enum
from controllers import TURN
from deck import Deck
from game_table import BlackJackGameTable, WrongRightsException
from user import User, UserStatus


class GameOutcome(Enum):
    loser = 0
    draw = 1
    winner = 2


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
                turn = user.make_turn(self.game_table)
                user.turn_result_notify(self.process_turn(user, turn))
            if len(self.game_table.get_active_users()) == 0:
                self.is_running = False

        scores = [self.game_table.get_user_score(user) for user in self.users]
        max_score = max(scores, key=lambda x: 0 if x > 21 else x)
        winners_count = scores.count(max_score)
        for score, user in zip(scores, self.users):
            outcome = GameOutcome.loser
            if score == max_score:
                outcome = GameOutcome.winner if winners_count == 1 else GameOutcome.draw
            user.outcome_notify(score, outcome)

    def process_turn(self, user: User, turn: TURN):
        if user in self.game_table.get_active_users():
            if turn is TURN.hit_me:
                new_card = self.deck.pull_out()
                self.game_table.add_card(user, new_card)
                return f"You took: {new_card}"
            elif turn is TURN.enough:
                self.game_table.update_status(user, UserStatus.enough)
                return "You can't take cards anymore"
        else:
            raise WrongRightsException("User is not in game")
