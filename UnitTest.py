from server import app
import unittest
import json
class FlaskTest(unittest.TestCase):
    
    def test_login(self):
        tester = app.test_client(self)
        response = tester.post('/login', data = {
            "email" : "test@example.com",
            "password" : "12345"
            })
        self.assertEqual(response.status_code, 401)
    # def test_get_all_tareas(self):
    #     tester = app.test_client(self)
    #     response = tester.get('http://127.0.0.1:5000/get_tareas')
    #     self.assertEqual(response.status_code, 200)


if __name__ =="__main__":
    unittest.main()