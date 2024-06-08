import unittest
import json
from app import app, initialize_db

class ToDoTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        initialize_db()

    def signup(self, username, password):
        return self.app.post('/signup', data=dict(username=username, password=password), follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/login', data=dict(username=username, password=password), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_signup(self):
        response = self.signup('testuser', 'testpass')
        self.assertEqual(response.status_code, 200)

    def test_login_logout(self):
        self.signup('testuser', 'testpass')
        response = self.login('testuser', 'testpass')
        self.assertIn(b'To-Do List', response.data)

        response = self.logout()
        self.assertIn(b'Log In', response.data)

    def test_add_task(self):
        self.signup('testuser', 'testpass')
        self.login('testuser', 'testpass')

        task_data = {'task': 'Test Task', 'due_date': '2023-12-31', 'priority': 1}
        response = self.app.post('/addTask', data=json.dumps(task_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json)

    def test_get_tasks(self):
        self.signup('testuser', 'testpass')
        self.login('testuser', 'testpass')

        task_data = {'task': 'Test Task', 'due_date': '2023-12-31', 'priority': 1}
        self.app.post('/addTask', data=json.dumps(task_data), content_type='application/json')

        response = self.app.get('/getTasks')
        self.assertEqual(response.status_code, 200)
        self.assertIn('tasks', response.json)

    def test_update_task(self):
        self.signup('testuser', 'testpass')
        self.login('testuser', 'testpass')

        task_data = {'task': 'Test Task', 'due_date': '2023-12-31', 'priority': 1}
        self.app.post('/addTask', data=json.dumps(task_data), content_type='application/json')

        task_id = self.app.get('/getTasks').json['tasks'][0]['tid']
        update_data = {'updated_task': 'Updated Task'}
        response = self.app.put(f'/updateTask/{task_id}', data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json)

    def test_delete_task(self):
        self.signup('testuser', 'testpass')
        self.login('testuser', 'testpass')

        task_data = {'task': 'Test Task', 'due_date': '2023-12-31', 'priority': 1}
        self.app.post('/addTask', data=json.dumps(task_data), content_type='application/json')

        task_id = self.app.get('/getTasks').json['tasks'][0]['tid']
        response = self.app.delete(f'/deleteTask/{task_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json)

    def test_update_task_order(self):
        self.signup('testuser', 'testpass')
        self.login('testuser', 'testpass')

        task_data1 = {'task': 'Test Task 1', 'due_date': '2023-12-31', 'priority': 1}
        task_data2 = {'task': 'Test Task 2', 'due_date': '2023-12-31', 'priority': 2}
        self.app.post('/addTask', data=json.dumps(task_data1), content_type='application/json')
        self.app.post('/addTask', data=json.dumps(task_data2), content_type='application/json')

        task_id1 = self.app.get('/getTasks').json['tasks'][0]['tid']
        task_id2 = self.app.get('/getTasks').json['tasks'][1]['tid']

        update_data1 = {'task_id': task_id1, 'new_index': 2}
        update_data2 = {'task_id': task_id2, 'new_index': 1}
        self.app.put('/updateTaskOrder', data=json.dumps(update_data1), content_type='application/json')
        response = self.app.put('/updateTaskOrder', data=json.dumps(update_data2), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json)

    def test_move_to_todo(self):
        self.signup('testuser', 'testpass')
        self.login('testuser', 'testpass')

        task_data = {'task': 'Test Task', 'due_date': '2023-12-31', 'priority': 1}
        self.app.post('/addTask', data=json.dumps(task_data), content_type='application/json')

        task_id = self.app.get('/getTasks').json['tasks'][0]['tid']
        self.app.post(f'/move-to-done/{task_id}/Test Task', content_type='application/json')

        completed_task_id = self.app.get('/getTasks').json['done'][0]['did']
        response = self.app.post(f'/move-to-todo/{completed_task_id}/Test Task', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json)

if __name__ == '__main__':
    unittest.main()
