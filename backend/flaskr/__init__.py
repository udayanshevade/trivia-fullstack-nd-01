import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
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

    #  ------------------------------------------------------------------------
    #  Categories
    #  ------------------------------------------------------------------------

    @app.route('/categories', methods=['GET'])
    def get_categories():
        """Handles GET requests for all available categories."""
        try:
            print('Request - [GET] /categories')

            data = Category.query.all()
            categories = {category.id: category.type for category in data}

            return jsonify({
                'success': True,
                'categories': categories
            }), 200
        except Exception as e:
            print(f'Error - [GET] /categories - {e}')
            abort(500)
        finally:
            db.session.close()

    QUESTIONS_PER_PAGE = 10

    #  ------------------------------------------------------------------------
    #  Questions
    #  ------------------------------------------------------------------------

    # Get paginated questions

    @app.route('/questions', methods=['GET'])
    def get_paginated_questions():
        """
          Handles getting paginated responses with optional query and pagination params
          Request params:
            - page: default of 1, filter by which batch of questions
            - current_category: (optional) filter questions down by a specified category
        """
        try:
            print('Request - [GET] /questions')

            page = request.args.get('page', 1, type=int)

            # calculate offset, if page is specified, defaults to 0
            offset = (page - 1) * QUESTIONS_PER_PAGE

            questions_total_count = db.session.query(
                func.count(Question.id)).first()[0]
            # FIRST eliminate an out-of-range query
            if offset >= questions_total_count:
                abort(404)

            # default current category to None, returned in response as is
            current_category = request.args.get(
                'current_category', None, type=int)

            # if the category does not exist, fail early
            if current_category and not Category.query.get(current_category):
                abort(404)

            questions_query = Question.query
            # apply an optional category filter before pagination
            if current_category:
                questions_query = questions_query.filter(
                    Question.category == current_category)
            questions_query = questions_query.limit(
                QUESTIONS_PER_PAGE).offset(offset)
            questions_data = [
                question.format() for question in questions_query.all()]

            categories_data = {
                category.id: category.type for category in Category.query.all()}

            return jsonify({
                'success': True,
                'questions': questions_data,
                'total_questions': questions_total_count,
                'categories': categories_data,
                'current_category': current_category,
            }), 200
        except Exception as e:
            print(f'Error - [GET] /questions - {e}')
            code = getattr(e, 'code', 500)
            abort(code)
        finally:
            db.session.close()

    # Search question
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        """
          Handles searching a query to pick specific questions
          Request body:
            - search - actual text query to filter questions
        """
        try:
            print('Request - [POST] /questions/search')
            body = request.get_json()
            search = body.get('search', '')

            questions_total_count = db.session.query(
                func.count(Question.id)).first()[0]

            questions_query = Question.query
            if search:
                questions_query = questions_query.filter(
                    Question.question.ilike(
                        f'%{search}%')
                )

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions_query.all()],
                'total_questions': questions_total_count,
                'current_category': None,
            }), 200
        except Exception as e:
            print(f'Error - [POST] /questions/search - {e}')
            code = getattr(e, 'code', 500)
            abort(code)
        finally:
            db.session.close()

    # Delete question

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """Handles deletion of a question"""
        try:
            print(f'Request - [DELETE] /questions/{question_id}')

            question = Question.query.get(question_id)

            # should not delete a non-existing item
            if not question:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
            }), 200
        except Exception as e:
            print(f'Error - [DELETE] /questions/{question_id} - {e}')
            code = getattr(e, 'code', 500)
            db.session.rollback()
            abort(code)
        finally:
            db.session.close()

    # Create question

    @app.route('/questions', methods=['POST'])
    def add_question():
        """
          Handles addition of a new question
          Request body:
            - question: text of the question to add
            - answer: text of the answer
            - difficulty: integer indicating how hard the question is
            - category: integer identifying the category of the question
        """
        try:
            print('Request - [POST] - /questions')
            body = request.get_json()

            question = body.get('question', None)
            answer = body.get('answer', None)
            difficulty = body.get('difficulty', None)
            category = body.get('category', None)

            if [x for x in [question, answer, difficulty, category] if not x] or not Category.query.get(category):
                # invalid request with missing field(s)
                abort(422)

            new_question = Question(
                question=question,
                answer=answer,
                difficulty=difficulty,
                category=category
            )

            db.session.add(new_question)
            db.session.commit()

            return jsonify({
                'success': True
            }), 201
        except Exception as e:
            print(f'Error - [POST] /questions - {e}')
            code = getattr(e, 'code', 500)
            abort(code)
        finally:
            db.session.close()

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_questions(category_id):
        '''
          Handles explicitly fetching questions by a specified category
          Request arguments:
            - category_id - variable specifying the category to get
        '''
        try:
            print(f'Request - [GET] /categories/{category_id}/questions')
            category = Category.query.get(category_id)

            # throw early if category is non-existent
            if not category:
                abort(404)

            questions_total_count = db.session.query(
                func.count(Question.id)).first()[0]

            questions_query = Question.query.filter(
                Question.category == category_id)
            questions = [question.format()
                         for question in questions_query.all()]
            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': questions_total_count,
                'current_category': None,
            })

        except Exception as e:
            print(f'Error - [GET] /categories/{category_id}/questions - {e}')
            code = getattr(e, 'code', 500)
            abort(code)
        finally:
            db.session.close()

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
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handles an unpredicted internal server error"""
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
        })

    return app
