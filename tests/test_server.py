from server import app, players_count

import unittest


class BasicTestCase(unittest.TestCase):
    def test_connect(self):
        tester = app.test_client(self)
        response = tester.post('/connect', json={'name': 'Player 1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'status': 'OK', 'id': 0})

        response = tester.post('/connect', json={'name': 'Player 1'})
        self.assertEqual(response.json, {'status': 'FAIL', 'error_msg': 'The nickname is already taken'})

        response = tester.post('/connect', json={'name': 'Player 2'})
        self.assertEqual(response.json, {'status': 'OK', 'id': 1})

        for id in range(3, players_count + 1):
            response = tester.post('/connect', json={'name': f'Player {id}'})
            self.assertEqual(response.json, {'status': 'OK', 'id': id - 1})

        response = tester.post('/connect', json={'name': f'Player {players_count + 1}'})
        self.assertEqual(response.json, {'error_msg': 'Server is full.', 'status': 'FAIL'})

    def test_start(self):
        tester = app.test_client(self)
        response = tester.post('/start', json={'id': 0})
        self.assertEqual(response.status_code, 200)
        expected_answer = {
            'status': 'OK',
            'ready': False,
            'players': list(
                [f'Player {user_id + 1}', user_id]
                for user_id in range(0, players_count)
            )
        }
        self.assertEqual(response.json, expected_answer)
        for user_id in range(1, players_count - 1):
            response = tester.post('/start', json={'id': user_id})
            self.assertEqual(response.json, expected_answer)
        response = tester.post('/start', json={'id': players_count - 1})
        self.assertEqual(response.json['ready'], True)
        self.assertIn('deck', response.json.keys())

    def test_turn_rounding(self):
        tester = app.test_client(self)
        response = tester.post('/yourturn', json={'player_id': 0})
        self.assertEqual(response.json, {'status': 'OK'})
        response = tester.post('/make_turn', json={'id': 0, 'turn': 0})
        self.assertEqual(response.json, {'status': 'OK'})
        response = tester.post('/turn_request', json={'id': 0})
        self.assertEqual(response.json, {'number': 1, 'status': 'OK', 'turn': 0, 'user_id': 0})
        tester.post('/yourturn', json={'player_id': 1})

        for user_id in range(1, players_count):
            response = tester.post('/turn_request', json={'id': user_id})
            self.assertEqual(response.json, {'number': 1, 'status': 'OK', 'turn': 0, 'user_id': 0})

        response = tester.post('/turn_request', json={'id': 0})
        self.assertEqual(response.json, {'status': 'OK'})
        response = tester.post('/make_turn', json={'id': 1, 'turn': 1})
        self.assertEqual(response.json, {'status': 'OK'})
        response = tester.post('/turn_request', json={'id': 0})
        self.assertEqual(response.json, {'number': 2, 'status': 'OK', 'turn': 1, 'user_id': 1})
        response = tester.post('/make_turn', json={'id': 2, 'turn': 2})
        self.assertEqual(response.json, {'status': 'OK'})
        response = tester.post('/turn_request', json={'id': 0})
        self.assertEqual(response.json, {'number': 3, 'status': 'OK', 'turn': 2, 'user_id': 2})
