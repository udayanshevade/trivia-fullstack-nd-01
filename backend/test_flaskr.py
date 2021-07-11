import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        """Tests getting the categories"""
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotIn('error', data)
        # populated dict
        categories = data['categories']
        self.assertTrue(categories)
        # check a key/value pair to ensure integrity
        self.assertEqual(categories['1'], 'Science')

    def test_get_paginated_questions(self):
        """Tests getting paginated questions with request param"""
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotIn('error', data)

        # populated array
        questions = data['questions']
        self.assertTrue(type(questions) == list and len(questions))

        # non-zero int
        total_questions = data['total_questions']
        self.assertTrue(type(total_questions) == int and total_questions)

        # populated array
        categories = data['categories']
        self.assertTrue(categories)
        self.assertEqual(categories['1'], 'Science')

        # None, but the key should still exist
        self.assertIn('current_category', data)

    def test_get_paginated_questions_with_404_for_out_of_range_page(self):
        """Returns 404 error for an out-of-range page"""
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'not found')

    def test_get_paginated_questions_with_404_for_invalid_category(self):
        """Returns 404 error for an out-of-range page"""
        res = self.client().get('/questions?current_category=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
