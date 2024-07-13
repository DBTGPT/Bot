import unittest
import json
from app import app, active_sessions

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_start_response(self):
        response = self.app.post('/api/start-response', data=json.dumps({
            'input': 'Hello, how are you?',
            'use_tts': True
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('session_id', data)
        self.assertIn(data['session_id'], active_sessions)

    def test_get_response_invalid_session(self):
        response = self.app.get('/api/get-response/invalid-session-id')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['error'], 'Invalid session ID')

    def test_get_response_valid_session(self):
        response = self.app.post('/api/start-response', data=json.dumps({
            'input': 'Hello, how are you?',
            'use_tts': False
        }), content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        session_id = data['session_id']

        response = self.app.get(f'/api/get-response/{session_id}')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
