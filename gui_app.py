import tkinter as tk
from queue import Queue

from controllers.ai_controller import AIController

from controllers.controller import Controller
from engine.blackjack_basics import GameOutcome, get_score, TURN

from engine.engine import Engine
from engine.user import User


class GuiUser(User):
    def __init__(self, root_widget, username, controller, turn_callback, restart_callback):
        super().__init__(controller.user_id, controller)
        self.username = username
        self.root_widget = root_widget
        self.card_widgets = []
        self.turn_callback = turn_callback
        self.restart_callback = restart_callback

        self.root_widget.rowconfigure(0, weight=0)
        self.root_widget.rowconfigure(1, weight=0)
        self.root_widget.rowconfigure(2, weight=1)
        self.root_widget.columnconfigure(0, weight=1)
        self.root_widget.columnconfigure(1, weight=1)
        self.nick_label = tk.Label(self.root_widget, text=username, bg='white')
        self.nick_label.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.score_label = tk.Label(self.root_widget, text='Score: 0', bg='white')
        self.score_label.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.cards_frame = tk.Frame(self.root_widget, bg='yellow')
        self.cards_frame.grid(row=2, column=0, columnspan=2, sticky='nsew')
        self.cards_frame.columnconfigure(0, weight=1)
        self.cards_frame.columnconfigure(1, weight=1)
        self.hit_button = tk.Button(self.root_widget, text="Hit me!", bg='white',
                                    state='disabled', command=lambda: turn_callback(self.id, True))
        self.hit_button.grid(row=10, column=0, sticky='news')
        self.enough_button = tk.Button(self.root_widget, text="Enough!", bg='white',
                                       state='disabled', command=lambda: turn_callback(self.id, False))
        self.enough_button.grid(row=10, column=1, sticky='news')

    def make_turn(self, users_status: dict, users_cards: dict):
        turn = self.controller.make_turn(users_status, users_cards)
        if not turn:
            self.cards_frame['bg'] = 'green'
            self.hit_button['state'] = 'normal'
            self.enough_button['state'] = 'normal'
        else:
            self.turn_callback(self.id, turn)

    def update_table(self, users_status: dict, users_cards: dict):
        for card_number, card in enumerate(users_cards[self.id]):
            if card_number >= len(self.card_widgets):
                self.card_widgets.append(tk.Label(self.cards_frame, text=str(card), bg='white'))
                self.card_widgets[-1].grid(row=len(self.card_widgets) - 1, column=0, columnspan=2, sticky='ew')
                self.cards_frame.rowconfigure(len(self.card_widgets) - 1)
        self.score_label['text'] = f"Score: {get_score(users_cards[self.id])} ({users_status[self.id].name})"
        self.cards_frame['bg'] = 'yellow'
        self.hit_button['state'] = 'disabled'
        self.enough_button['state'] = 'disabled'
        self.controller.update_table(users_status, users_cards)

    def outcome_notify(self, game_score: int, status: GameOutcome):
        self.hit_button['state'] = 'normal'
        self.hit_button['text'] = "BACK TO MENU"
        self.hit_button['command'] = self.restart_callback
        self.enough_button['state'] = 'normal'
        self.enough_button['text'] = "BACK TO MENU"
        self.enough_button['command'] = self.restart_callback
        self.cards_frame['bg'] = 'green' if status is GameOutcome.winner or status is GameOutcome.draw else 'red'
        self.score_label['text'] = f"OUTCOME: {status.name} ({game_score} p)"


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('200x250')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.players_info = []
        self.game = Game(self)
        self.menu = Menu(self, self.players_info)

    def start_game(self):
        if len(self.players_info) >= 2:
            for user_id, user_info in enumerate(self.players_info):
                controller = AIController(user_id) if user_info[1].get() else Controller(user_id)
                self.game.add_player(user_info[0].get() + (' (AI)' if user_info[1].get() else ''), controller)
            self.game.tkraise()
            self.game.start_game()


class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(column=0, row=0, sticky="news")
        self.rowconfigure(0, weight=1)
        self.master = master

        self.engine = None
        self.users = []
        self.user_frames = []
        self.active_users_queue = Queue()

    def turn_callback(self, user_id: int, is_hit_me: bool):
        self.engine.process_turn(self.users[user_id], TURN.hit_me if is_hit_me else TURN.enough)
        self.users[user_id].update_table(*self.engine.get_game_table_info())
        if self.active_users_queue.empty():
            queue_update = self.engine.get_active_users()
            if not queue_update:
                self.engine.outcomes_notify(self.engine.generate_outcomes())
                return
            else:
                for user in queue_update:
                    self.active_users_queue.put(user)
        user = self.active_users_queue.get()
        self.engine.process_turn(user, user.make_turn(*self.engine.get_game_table_info()))

    def restart_callback(self):
        self.user_frames = []
        self.users = []
        self.active_users_queue = Queue()
        self.engine = None
        self.master.geometry('200x250')
        self.master.menu.tkraise()


    def add_player(self, username: str, controller):
        frame = tk.Frame(self, bg="white")
        frame.grid(column=controller.user_id, row=0, sticky="news")
        self.columnconfigure(controller.user_id, weight=1)
        self.user_frames.append(frame)
        self.users.append(GuiUser(frame, username, controller, self.turn_callback, self.restart_callback))

    def start_game(self):
        self.master.geometry('1100x250')
        self.engine = Engine()
        for user in self.users:
            self.engine.add_user(user)
        self.engine.init_game()
        self.engine.update_users()
        for user in self.engine.get_active_users():
            self.active_users_queue.put(user)
        user = self.active_users_queue.get()
        self.engine.process_turn(user, user.make_turn(*self.engine.get_game_table_info()))
        if self.engine.is_ended():
            self.engine.outcomes_notify(self.engine.generate_outcomes())


class Menu(tk.Frame):
    def __init__(self, master, players_info: list):
        super().__init__(master)
        self.players_table = tk.Frame(self)
        self.head_player_label = tk.Label(self.players_table, text="Players", padx=10, pady=10, bg="white", fg="black")
        self.head_ai_label = tk.Label(self.players_table, text="AI", padx=10, pady=10, bg="white", fg="black")
        self.add_player_btn = tk.Button(self, text="Add player", bg='white', command=self.add_player)
        self.rem_player_btn = tk.Button(self, text="Remove player", bg='white', command=self.rem_player)
        self.start_game_btn = tk.Button(self, text="Start game", bg='white', command=master.start_game)
        self.player_widgets = []
        self.players_info = players_info
        self.put_widgets()

    def put_widgets(self):
        self.grid(column=0, row=0, sticky="news")
        self.players_table.grid(row=0, column=0, sticky='new')
        self.players_table.rowconfigure(0, weight=1)
        self.players_table.columnconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.head_player_label.grid(row=0, column=0, sticky='new')
        self.head_ai_label.grid(row=0, column=1, sticky='new')
        self.add_player_btn.grid(row=1, column=0, sticky='news')
        self.rem_player_btn.grid(row=2, column=0, sticky='news')
        self.start_game_btn.grid(row=3, column=0, sticky='news')
        self.add_player()
        self.add_player()

    def add_player(self):
        if len(self.players_info) < 5:
            player_number = 1 + len(self.player_widgets)
            self.players_info.append((tk.StringVar(self, value=f"Player {player_number}"), tk.BooleanVar(value=False)))
            username = tk.Entry(self.players_table, bg="white", textvariable=self.players_info[-1][0])
            checkbox = tk.Checkbutton(self.players_table, bg="white", variable=self.players_info[-1][1])
            username.grid(row=player_number, column=0, sticky='we')
            checkbox.grid(row=player_number, column=1, sticky='we')
            self.player_widgets.append((username, checkbox))

    def rem_player(self):
        if self.players_info:
            self.player_widgets[-1][0].destroy()
            self.player_widgets[-1][1].destroy()
            self.players_info.pop(-1)
            self.player_widgets.pop(-1)


if __name__ == "__main__":
    app = Application()
    app.mainloop()