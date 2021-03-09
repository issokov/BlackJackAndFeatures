from user import User
from engine import Engine
from controllers import ManualController, IntelligenzaArtificialeControllore


def main():
    while True:
        game = Engine()
        user_1 = User(1, IntelligenzaArtificialeControllore(1))
        user_2 = User(2, ManualController(2))
        game.add_user(user_1)
        game.add_user(user_2)

        game.init_game()
        game.update_users()

        while not game.is_ended():
            game.one_tick()

        game.outcomes_notify(game.generate_outcomes())

        # print("One more time? ('Y/n':)")
        # answer = '?'
        # while answer and answer[0].lower() not in ['y', 'n']:
        #     answer = input()
        # if answer and answer[0].lower() == 'n':
        #     break


if __name__ == "__main__":
    main()
