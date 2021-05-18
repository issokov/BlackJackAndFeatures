from flask import Flask, jsonify, request
from engine.deck import Deck

app = Flask(__name__)

players_count = 2
users = {}
deck = Deck()
whose_turn, turn_result = 0, None
next_turn, step_number = None, 0
accept_turn = set()


@app.route("/connect", methods=['POST'])
def connect():
    data = request.get_json()
    if data['name'] and data['name'] not in map(lambda v: v['name'], users.values()):
        if players_count > len(users):
            new_id = len(users)
            users[new_id] = {'id': new_id, 'name': data['name'], 'ready': False}
            return jsonify(status='OK', id=new_id)
        return jsonify(status='FAIL', error_msg='Server is full.')
    return jsonify(status='FAIL', error_msg='The nickname is already taken')


@app.route("/start", methods=['POST'])
def start_game():
    data = request.get_json()
    users[data['id']]['ready'] = True
    ready = all(map(lambda v: v['ready'], users.values())) and len(users) == players_count
    ready_players = list(map(lambda v: [v['name'], v['id']], users.values()))
    if ready:
        return jsonify(status='OK', ready=ready, players=ready_players, deck=str(deck))
    return jsonify(status='OK', ready=ready, players=ready_players)


@app.route("/yourturn", methods=['POST'])
def yourturn():
    data = request.get_json()
    global next_turn
    next_turn = data['player_id']
    return jsonify(status='OK')


@app.route("/make_turn", methods=['POST'])
def make_turn():
    global whose_turn, turn_result, step_number
    data = request.get_json()
    turn_result = data['turn']
    whose_turn = data['id']
    step_number += 1
    return jsonify(status='OK')


@app.route("/turn_request", methods=['POST'])
def turn_request():
    global whose_turn, turn_result, next_turn
    if whose_turn is not None and turn_result is not None:
        answer = jsonify(status='OK', user_id=whose_turn, turn=turn_result, number=step_number)
        accept_turn.add(request.json['id'])
        if len(accept_turn) == players_count:
            whose_turn = next_turn
            turn_result = None
            accept_turn.clear()
        return answer
    return jsonify(status='OK')


@app.route("/clear", methods=['POST'])
def clear():
    global users, deck, whose_turn, turn_result
    users = {}
    deck = Deck()
    whose_turn, turn_result = 0, None
    return jsonify(status='OK')


if __name__ == '__main__':
    app.run()
