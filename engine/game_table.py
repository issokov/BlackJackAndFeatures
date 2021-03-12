from .card import Card
from .user import User
from .blackjack_basics import get_score, WrongRightsException, UserStatus


class BlackJackGameTable:
    def __init__(self, users: list):
        self.users = users
        self.users_status = dict((user.id, UserStatus.in_game) for user in self.users)
        self.users_cards = dict((user.id, []) for user in self.users)

    def get_user_score(self, user: User):
        return get_score(self.users_cards[user.id])

    def get_cards(self, user):
        return self.users_cards[user.id]

    def add_card(self, user: User, card: Card):
        if self.users_status[user.id] is UserStatus.in_game:
            self.users_cards[user.id].append(card)
            new_score = self.get_user_score(user)
            if new_score > 21:
                self.set_status(user, UserStatus.lose)
            elif new_score == 21:
                self.set_status(user, UserStatus.blackjack)
        else:
            raise WrongRightsException(f"The user {user.id} cannot take the card according to the rules")

    def get_status(self, user) -> UserStatus:
        return self.users_status[user.id]

    def set_status(self, user: User, status: UserStatus):
        self.users_status[user.id] = status

    def get_users(self):
        return self.users

    def get_active_users(self):
        return list(filter(lambda u: self.users_status[u.id] is UserStatus.in_game, self.users))
