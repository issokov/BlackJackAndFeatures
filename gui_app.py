import tkinter as tk
from queue import Queue
from tkinter import messagebox

import requests

from controllers.ai_controller import AIController

from controllers.controller import Controller
from engine.blackjack_basics import GameOutcome, get_score, TURN
from engine.deck import Deck

from engine.engine import Engine
from engine.user import User

client_id = None
server_url = None


class GuiUser(User):
    # pylint: disable=too-many-instance-attributes, too-many-arguments
    def __init__(self, root_widget, username, controller, turn_callback, restart_callback):
        super().__init__(controller.user_id, controller)
        self.username = username
        self.card_widgets = []
        self.turn_callback = turn_callback
        self.restart_callback = restart_callback
        self.nick_label = tk.Label(root_widget, text=username, bg='white')
        self.nick_label.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.score_label = tk.Label(root_widget, text='Score: 0', bg='white')
        self.score_label.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.cards_frame = tk.Frame(root_widget, bg='yellow')
        self.cards_frame.grid(row=2, column=0, columnspan=2, sticky='nsew')
        self.cards_frame.columnconfigure(0, weight=1)
        self.cards_frame.columnconfigure(1, weight=1)
        self.hit_button = tk.Button(root_widget, text="Hit me!", bg='white', state='disabled',
                                    command=lambda: turn_callback(self.user_id, TURN.HIT_ME))
        self.hit_button.grid(row=10, column=0, sticky='news')
        self.enough_button = tk.Button(root_widget, text="Enough!", state='disabled', bg='white',
                                       command=lambda: turn_callback(self.user_id, TURN.ENOUGH))
        self.enough_button.grid(row=10, column=1, sticky='news')

    def make_turn(self, users_status: dict, users_cards: dict):
        self.cards_frame['bg'] = 'green'
        if client_id:
            requests.post(server_url + '/yourturn', json={'player_id': self.user_id})
        if client_id is None or client_id == self.user_id:
            self.hit_button['state'] = 'normal'
            self.enough_button['state'] = 'normal'
        turn = self.controller.make_turn(users_status, users_cards)
        if turn:
            self.turn_callback(self.user_id, turn)

    def update_table(self, users_status: dict, users_cards: dict):
        for card_number, card in enumerate(users_cards[self.user_id]):
            if card_number >= len(self.card_widgets):
                self.card_widgets.append(tk.Label(self.cards_frame, text=str(card), bg='white'))
                self.card_widgets[-1].grid(row=len(self.card_widgets) - 1, column=0,
                                           columnspan=2, sticky='ew')
                self.cards_frame.rowconfigure(len(self.card_widgets) - 1)
        self.score_label['text'] = f"Score: {get_score(users_cards[self.user_id])}" \
                                   f" ({users_status[self.user_id].name})"
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
        color = 'green' if status in [GameOutcome.WINNER, GameOutcome.DRAW] else 'red'
        self.cards_frame['bg'] = color
        self.score_label['text'] = f"OUTCOME: {status.name} ({game_score} p)"


class Application(tk.Tk):
    def __init__(self, server_ip: str, port: str, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('200x250')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.players_info = []
        self.game = Game(self)
        self.menu = Menu(self, self.players_info)
        self.last_step_number = -1
        global server_url
        server_url = f"http://{server_ip}:{port}"

    def start_pooling(self):
        data = requests.post(server_url + '/turn_request', json={'id': client_id}).json()
        if data.get('turn', None) is not None and data['user_id'] != client_id and data['number'] > self.last_step_number:
            self.last_step_number = data['number']
            self.game.turn_callback(data['user_id'], TURN(data['turn']))
        if client_id is not None:
            self.after(100, self.start_pooling)

    def start_game(self, deck=None):
        if len(self.players_info) >= 2:
            for user_id, user_info in enumerate(self.players_info):
                nickname = user_info[0].get()
                if user_info[1].get():
                    controller = AIController(user_id)
                    nickname += ' (AI)'
                else:
                    controller = Controller(user_id)
                self.game.add_player(nickname, controller)
            if client_id is not None:
                self.start_pooling()
            self.game.tkraise()
            self.game.start_game(deck)

    def connect_to_server(self):
        if len(self.players_info) != 1 or self.players_info[0][1].get():
            messagebox.showerror(title='Wrong player count', message='Should be one not AI player with your nickname')
        else:
            resp = requests.post(server_url + '/connect', json={'name': self.players_info[0][0].get()})
            data = resp.json()
            if data['status'] == 'FAIL':
                messagebox.showerror(title='Wrong nickname', message=data['error_msg'])
            elif data['status'] == 'OK':
                messagebox.showinfo(title='Please, wait', message='Waiting another players...')
                global client_id
                client_id = data['id']
                self.start_game_awaiting()

    def start_game_awaiting(self):
        resp = requests.post(server_url + '/start', json={'id': client_id})
        data = resp.json()
        while self.players_info:
            self.menu.rem_player()
        for player in data['players']:
            self.menu.add_player(username=player[0], ai=False)
        if data['status'] == 'OK' and data['ready']:
            self.start_game(Deck(str_deck=data['deck']))
        else:
            self.after(100, self.start_game_awaiting)


class Game(tk.Frame):  # pylint: disable=too-many-ancestors
    def __init__(self, master):
        super().__init__(master)
        self.grid(column=0, row=0, sticky="news")
        self.rowconfigure(0, weight=1)
        self.master = master

        self.engine = None
        self.users = []
        self.user_frames = []
        self.active_users_queue = Queue()

    def turn_callback(self, user_id: int, turn: TURN):
        self.engine.process_turn(self.users[user_id], turn)
        if None not in [client_id, turn] and user_id == client_id:
            resp = requests.post(server_url + '/make_turn', json={'id': user_id, 'turn': turn.value})
            data = resp.json()
            if data['status'] == 'FAIL':
                messagebox.showerror(title='Not your turn', message=data['error_msg'])

        self.users[user_id].update_table(*self.engine.get_game_table_info())
        if self.active_users_queue.empty():
            queue_update = self.engine.get_active_users()
            if queue_update:
                for user in queue_update:
                    self.active_users_queue.put(user)
            else:
                self.engine.outcomes_notify(self.engine.generate_outcomes())
                return
        user = self.active_users_queue.get()
        self.engine.process_turn(user, user.make_turn(*self.engine.get_game_table_info()))

    def to_menu_callback(self):
        global client_id
        if client_id:
            requests.post(server_url + '/clear')
        client_id = None
        for user_frame in self.user_frames:
            user_frame.grid_forget()
            user_frame.destroy()
        self.user_frames.clear()
        self.users.clear()
        self.active_users_queue.queue.clear()
        self.engine = None
        self.master.geometry('200x250')
        self.master.menu.tkraise()

    def add_player(self, username: str, controller: Controller):
        frame = tk.Frame(self, bg="white")
        frame.grid(column=controller.user_id, row=0, sticky="news")
        self.columnconfigure(controller.user_id, weight=1)
        self.user_frames.append(frame)
        frame.rowconfigure(0, weight=0)
        frame.rowconfigure(1, weight=0)
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        user = GuiUser(frame, username, controller, self.turn_callback, self.to_menu_callback)
        self.users.append(user)

    def start_game(self, deck=None):
        self.master.geometry('1100x250')
        deck = Deck() if deck is None else deck
        self.engine = Engine(deck)
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
    # pylint: disable=too-many-ancestors
    # pylint: disable=too-many-instance-attributes
    def __init__(self, master, players_info: list):
        super().__init__(master)
        self.players_table = tk.Frame(self)
        self.head_player_label = tk.Label(self.players_table, text="Players",
                                          padx=10, pady=10, bg="white", fg="black")
        self.head_ai_label = tk.Label(self.players_table, text="AI",
                                      padx=10, pady=10, bg="white", fg="black")
        self.add_player_btn = tk.Button(self, text="Add player",
                                        bg='white', command=self.add_player)
        self.rem_player_btn = tk.Button(self, text="Remove player",
                                        bg='white', command=self.rem_player)
        self.start_game_btn = tk.Button(self, text="Start game",
                                        bg='white', command=master.start_game)
        self.start_server_game = tk.Button(self, text="Connect to server", bg='white', command=master.connect_to_server)
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
        self.start_server_game.grid(row=4, column=0, sticky='news')
        self.add_player()
        self.add_player()

    def add_player(self, username=None, ai=None):
        if len(self.players_info) < 5:
            player_number = 1 + len(self.player_widgets)
            username = f"Player {player_number}" if username is None else username
            ai = False if ai is None else ai
            self.players_info.append((tk.StringVar(self, value=username),
                                      tk.BooleanVar(value=ai)))
            username = tk.Entry(self.players_table, bg="white",
                                textvariable=self.players_info[-1][0])
            checkbox = tk.Checkbutton(self.players_table, bg="white",
                                      variable=self.players_info[-1][1])
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
    # noinspection PyMissingOrEmptyDocstring
    app = Application('0.0.0.0', '5000')
    app.mainloop()
