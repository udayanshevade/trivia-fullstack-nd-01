import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import db, setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = 'trivia_test'
        self.database_path = 'postgresql://{}/{}'.format(
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
        db.session.close()
        pass

    #  ------------------------------------------------------------------------
    #  Categories
    #  ------------------------------------------------------------------------

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

    #  ------------------------------------------------------------------------
    #  Questions
    #  ------------------------------------------------------------------------

    # Get paginated questions

    def test_get_paginated_questions(self):
        """Tests getting paginated questions"""
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
        """Returns 404 error for an invalid category"""
        res = self.client().get('/questions?current_category=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'not found')

    # Search questions

    def test_search_questions(self):
        """Tests getting questions with a 'search' json"""
        # enter new data that is unique
        new_question = Question(
            question='How much wood could a woodchuck chuck if a woodchuck could chuck wood?',
            answer='A woodchuck would chuck as much wood as a woodchuck could if a woodchuck could chuck wood.',
            category=1,
            difficulty=2
        )
        db.session.add(new_question)
        db.session.commit()
        request_data = {'search': 'if a WoOdcHuCk could chuck wood'}
        res = self.client().post('/questions/search', json=request_data)  # case-insensitive
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotIn('error', data)

        # populated array
        questions = data['questions']
        self.assertTrue(type(questions) == list and len(questions) == 1)

        Question.query.get(new_question.id).delete()  # test-specific tear down

    #  Delete question

    def test_delete_question(self):
        """Tests deletion of a question"""
        # First insert a new question for the test and delete it
        new_question = Question(
            question='How do magnets work?',
            answer='Magic.',
            category=1,
            difficulty=1000,
        )
        db.session.add(new_question)
        db.session.commit()

        res = self.client().delete(f'/questions/{new_question.id}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        # We should not be able to find the item in the db now
        deleted_question = Question.query.get(new_question.id)
        self.assertEqual(deleted_question, None)

    def test_delete_question_with_404_for_out_of_range_item(self):
        """Tests failed deletion of a non-existing question"""
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    #  Post question

    def test_add_question(self):
        """Tests addition of a new question"""
        request_data = {
            'question': 'How do magnets work?',
            'answer': 'Magic',
            'difficulty': 1,
            'category': 1,
        }
        res = self.client().post('/questions', json=request_data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)

    def test_add_question_422_for_invalid_form_values(self):
        """Tests addition of a new question with invalid form data"""
        request_data = {
            'question': 'How do magnets work?',
            'answer': 'Magic',
            'difficulty': None,
            'category': 1,
        }
        res = self.client().post('/questions', json=request_data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'could not process the request')

    def test_add_question_422_for_invalid_category(self):
        """Tests addition of a new question with an invalid category"""
        request_data = {
            'question': 'How do magnets work?',
            'answer': 'Magic',
            'difficulty': 1,
            'category': 1000,
        }
        res = self.client().post('/questions', json=request_data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'could not process the request')

    # Get all questions by category

    def test_get_questions_by_category(self):
        """Tests getting all questions for a category"""
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        # populated array
        questions = data['questions']
        self.assertTrue(type(questions) == list and len(questions))

        # non-zero int
        total_questions = data['total_questions']
        self.assertTrue(type(total_questions) == int and total_questions)

        # None, but the key should still exist
        self.assertIn('current_category', data)

    def test_get_questions_with_404_for_invalid_category(self):
        """Returns 404 error for an invalid category"""
        res = self.client().get('/category/1000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'not found')

    # Quiz questions

    def test_get_quiz_question(self):
        """Tests getting a new random quiz question"""
        request_data = {
            'previous_questions': [],
            'quiz_category': {'id': 0, 'type': None}  # all
        }
        res = self.client().post('/quizzes', json=request_data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        question = data['question']
        self.assertTrue(question)
        self.assertIn('id', question)

    def test_get_quiz_question_for_category(self):
        """Tests getting a new random quiz question with a specified category"""
        request_data = {
            'previous_questions': [4, 6],
            'quiz_category': {'id': 5, 'type': 'Entertainment'}
        }
        res = self.client().post('/quizzes', json=request_data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        question = data['question']
        self.assertTrue(question)
        # check if the movie in the sample data is right
        # {'answer': 'Apollo 13', 'category': 5, 'difficulty': 4, 'id': 2, 'question': 'What movie earned Tom Hanks his third straight Oscar nomination, in 1996?'}
        self.assertEqual(question['id'], 2)

    def test_get_quiz_question_with_404_for_invalid_category(self):
        """Tests getting a new random quiz question with an invalid category"""
        request_data = {
            'previous_questions': [4, 6],
            'quiz_category': {'id': 1000, 'type': 'Foo'}
        }
        res = self.client().post('/quizzes', json=request_data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_nothing_for_invalid_category(self):
        """Tests getting no new questions if we are all out"""
        request_data = {
            'previous_questions': [2, 4, 6],
            'quiz_category': {'id': 5, 'type': 'Entertainment'}
        }
        res = self.client().post('/quizzes', json=request_data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], None)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
