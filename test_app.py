import unittest
import json
from app import app, initialize_db

class TodoAppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        initialize_db()
        self.register_and_login()

    def register_and_login(self):
        self.app.post('/signup', data=json.dumps({
            'username': 'testuser',
            'password': 'testpass'
        }), content_type='application/json')
        self.app.post('/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpass'
        }), content_type='application/json')

    def test_signup(self):
        response = self.app.post('/signup', data=json.dumps({
            'username': 'newuser',
            'password': 'newpass'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'success', response.data)

    def test_login(self):
        response = self.app.post('/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpass'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data)

    def test_add_task(self):
        response = self.app.post('/addTask', data=json.dumps({
            'task': 'New Task',
            'due_date': '2023-12-31',
            'priority': 1
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'success', response.data)

    def test_get_tasks(self):
        self.app.post('/addTask', data=json.dumps({
            'task': 'New Task',
            'due_date': '2023-12-31',
            'priority': 1
        }), content_type='application/json')
        response = self.app.get('/getTasks')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New Task', response.data)

    def test_sort_filter_tasks(self):
        # Add multiple tasks with different due dates and priorities
        tasks = [
            {'task': 'Task 1', 'due_date': '2023-12-30', 'priority': 2},
            {'task': 'Task 2', 'due_date': '2023-12-31', 'priority': 1},
            {'task': 'Task 3', 'due_date': '2023-12-29', 'priority': 3}
        ]
        for task in tasks:
            self.app.post('/addTask', data=json.dumps(task), content_type='application/json')

        # Test sorting by due date
        response = self.app.get('/getTasks?sort_by=due_date')
        self.assertEqual(response.status_code, 200)
        tasks_due_date = response.json['tasks']
        self.assertTrue(tasks_due_date[0]['due_date'] <= tasks_due_date[1]['due_date'] <= tasks_due_date[2]['due_date'])

        # Test filtering by due date
        response = self.app.get('/getTasks?filter_by_date=2023-12-30')
        self.assertEqual(response.status_code, 200)
        filtered_tasks = response.json['tasks']
        self.assertTrue(all(task['due_date'] <= '2023-12-30' for task in filtered_tasks))

    def test_logout(self):
        response = self.app.get('/logout')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data)

        # Verify user is logged out
        response = self.app.get('/getTasks')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Unauthorized', response.data)

if __name__ == '__main__':
    unittest.main()
