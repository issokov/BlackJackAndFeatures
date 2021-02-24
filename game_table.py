from typing import List

from card import Card, VALUE
from user import User, UserStatus


class WrongDeckConfiguration(Exception):
    pass


class WrongRightsException(Exception):
    pass


def get_score(cards: List[Card]):
    score = 0
    value_to_score = {
        VALUE.two: 2, VALUE.three: 3, VALUE.four: 4, VALUE.five: 5,
        VALUE.six: 6, VALUE.seven: 7, VALUE.eight: 8, VALUE.nine: 9,
        VALUE.ten: 10, VALUE.jack: 10, VALUE.queen: 10, VALUE.king: 10
    }
    for card in cards:
        if card.value is not VALUE.ace:
            score += value_to_score[card.value]
        elif card.value is VALUE.ace:
            score += 1 if score + 11 > 21 else 11
        else:
            raise WrongDeckConfiguration
    return score


class BlackJackGameTable:
    def __init__(self, users: List):
        self.users = users
        self.users_status = dict((user.id, UserStatus.in_game) for user in self.users)
        self.users_cards = dict((user.id, []) for user in self.users)

    def get_user_score(self, user: User):
        return get_score(self.users_cards[user.id])

    def get_cards(self, user):
        return self.users_cards[user.id]

    def add_card(self, user: User, card: Card):
        if card.value is VALUE.joker:
            raise WrongDeckConfiguration("Joker is not in game")
        if self.users_status[user.id] is UserStatus.in_game:
            self.users_cards[user.id].append(card)
            new_score = self.get_user_score(user)
            if new_score > 21:
                self.update_status(user, UserStatus.lose)
            elif new_score == 21:
                self.update_status(user, UserStatus.blackjack)
        else:
            raise WrongRightsException(f"The user {user.id} cannot take the card according to the rules")

    def get_status(self, user) -> UserStatus:
        return self.users_status[user.id]

    def update_status(self, user: User, status: UserStatus):
        self.users_status[user.id] = status

    def get_users(self):
        return self.users

    def get_active_users(self):
        return list(filter(lambda u: self.users_status[u.id] is UserStatus.in_game, self.users))
