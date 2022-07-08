import os
from flask import Flask, flash, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def paginate_Questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    paginated_Questions = questions[start:end]

    return paginated_Questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods",
            "PUT, POST, PATCH, DELETE, GET, OPTIONS, HEAD",
        )
        response.headers.add("Access-Control-Allow-Credentials", "true")
        # response.headers.add(
        #     "Access-Control-Allow-Origin", "*"
        # )
        return response

    # get categories
    @app.route("/api/categories", methods=["GET"])
    def retrieve_categories():
        allCategories = Category.query.all()

        result = {
            "categories": {
                str(category.id): category.type for category in allCategories
            }
        }
        return jsonify(result)

    # get questions per page
    @app.route("/api/questions")
    def retrieve_questions():
        Questions = Question.query.all()
        formatted_questions = paginate_Questions(request, Questions)

        if len(formatted_questions) == 0:
            abort(404)

        return jsonify(
            {
                "questions": formatted_questions,
                "totalQuestions": len(Questions),
                "currentCategory": "History",
                "categories": {
                    str(category.id): category.type for category in Category.query.all()
                },
            }
        )

    # delete question
    @app.route("/api/questions/<int:id>", methods=["DELETE"])
    def delete_question(id):
        try:
            question = Question.query.filter(Question.id == id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify(
                {
                    "success": True,
                    "deleted": id,
                }
            )
        except:
            abort(422)

    # post a new question or search for a question
    @app.route("/api/questions", methods=["POST"])
    def create_question():

        body = request.get_json()

        new_question = body.get("question")
        answer = body.get("answer")
        difficulty = body.get("difficulty")
        category = body.get("category")
        searchTerm = request.get_json().get("searchTerm")

        try:
            if searchTerm:
                Questions = Question.query.filter(
                    Question.question.ilike("%{}%".format(searchTerm))
                ).all()

                formatted_questions = paginate_Questions(request, Questions)

                return jsonify(
                    {
                        "questions": formatted_questions,
                        "totalQuestions": len(Question.query.all()),
                        "currentCategory": "Entertainment",
                    }
                )

            else:
                question = Question(
                    question=new_question,
                    answer=answer,
                    category=category,
                    difficulty=difficulty,
                )

            question.insert()
            db.session.close()
        except:
            abort(422)

            # flash("Question inserted successfully")

    # get question by category
    @app.route("/api/categories/<id>/questions")
    def get_question_by_category(id):
        Questions = Question.query.filter(Question.category == id).all()

        formatted_questions = paginate_Questions(request, Questions)

        if formatted_questions == None:
            abort(404)

        result = {
            "questions": formatted_questions,
            "totalQuestions": len(formatted_questions),
            "currentCategory": "History",
        }
        response = jsonify(result)
        return response

    # play quiz based on a category
    @app.route("/api/quizzes", methods=["POST"])
    def get_quiz_questions():
        body = request.get_json()
        previous_questions = body.get("previous_questions")
        quiz_category = body.get("quiz_category")
        questions = Question.query.all()

        play_question = []

        for item in questions:
            if len(previous_questions) == 0 and item.category != int(
                quiz_category["id"]
            ):
                play_question.append(item.format())
            else:
                for item_ in previous_questions:
                    if item_ != item.id and item.category != int(quiz_category["id"]):
                        play_question.append(item.format())

        return jsonify({"question": random.choice(play_question)})

    # error handlers
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    return app
