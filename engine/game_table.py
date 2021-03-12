from .card import Card
from .user import User
from .blackjack_basics import get_score, WrongRightsException, UserStatus


class BlackJackGameTable:
    def __init__(self, users: list):
        self.users = users
        self.users_status = dict((user.user_id, UserStatus.IN_GAME) for user in self.users)
        self.users_cards = dict((user.user_id, []) for user in self.users)

    def get_user_score(self, user: User):
        return get_score(self.users_cards[user.user_id])

    def get_cards(self, user):
        return self.users_cards[user.user_id]

    def add_card(self, user: User, card: Card):
        if self.users_status[user.user_id] is UserStatus.IN_GAME:
            self.users_cards[user.user_id].append(card)
            new_score = self.get_user_score(user)
            if new_score > 21:
                self.set_status(user, UserStatus.LOSE)
            elif new_score == 21:
                self.set_status(user, UserStatus.BLACKJACK)
        else:
            raise WrongRightsException(f"The user {user.user_id} "
                                       f"cannot take the card according to the rules")

    def get_status(self, user) -> UserStatus:
        return self.users_status[user.user_id]

    def set_status(self, user: User, status: UserStatus):
        self.users_status[user.user_id] = status

    def get_users(self):
        return self.users

    def get_active_users(self):
        return list(
            filter(lambda u: self.users_status[u.user_id] is UserStatus.IN_GAME, self.users))
