import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        """Processes the response before sending"""
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods', ['GET', 'POST', 'DELETE', 'OPTIONS'])

        return response

    @app.route('/healthcheck', methods=['GET'])
    def healthcheck():
        return 'OK', 200

    @app.route('/categories', methods=['GET'])
    def get_categories():
        """Create an endpoint to handle GET requests for all available categories."""
        try:
            print('Request - [GET] /categories')

            categories = {}
            data = Category.query.all()

            for category in data:
                categories[category.id] = category.type

            return jsonify({
                'success': True,
                'categories': categories
            })
        except Exception as e:
            print(f'Error - [GET] /categories - {e}')
            abort(e)
        finally:
            db.session.close()

    '''
      @TODO:
      Create an endpoint to handle GET requests for questions,
      including pagination (every 10 questions).
      This endpoint should return a list of questions,
      number of total questions, current category, categories.

      TEST: At this point, when you start the application
      you should see questions and categories generated,
      ten questions per page and pagination at the bottom of the screen for three pages.
      Clicking on the page numbers should update the questions.
    '''

    '''
      @TODO: 
      Create an endpoint to DELETE question using a question ID.

      TEST: When you click the trash icon next to a question, the question will be removed.
      This removal will persist in the database and when you refresh the page.
    '''

    '''
      @TODO: 
      Create an endpoint to POST a new question,
      which will require the question and answer text,
      category, and difficulty score.

      TEST: When you submit a question on the "Add" tab,
      the form will clear and the question will appear at the end of the last page
      of the questions list in the "List" tab.
    '''

    '''
      @TODO: 
      Create a POST endpoint to get questions based on a search term.
      It should return any questions for whom the search term
      is a substring of the question.

      TEST: Search by any phrase. The questions list will update to include
      only question that include that string within their question.
      Try using the word "title" to start.
    '''

    '''
      @TODO: 
      Create a GET endpoint to get questions based on category.

      TEST: In the "List" tab / main screen, clicking on one of the
      categories in the left column will cause only questions of that
      category to be shown.
    '''

    '''
      @TODO: 
      Create a POST endpoint to get questions to play the quiz.
      This endpoint should take category and previous question parameters
      and return a random questions within the given category,
      if provided, and that is not one of the previous questions.

      TEST: In the "Play" tab, after a user selects "All" or a category,
      one question at a time is displayed, the user is allowed to answer
      and shown whether they were correct or not.
    '''

    #  Error handlers
    #  ------------------------------------------------------------------------

    @app.errorhandler(400)
    def invalid_request(error):
        """Error handler for invalid request"""
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'invalid request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        """Error handler for a resource that can't be found"""
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'not found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Error handler for an unallowed request method"""
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(408)
    def request_timeout(error):
        """Error handler for a request timeout"""
        return jsonify({
            'success': False,
            'error': 408,
            'message': 'request timed out'
        }), 408

    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Error handler for an invalid request with valid syntax"""
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'could not process the request'
        }), 4222

    return app
