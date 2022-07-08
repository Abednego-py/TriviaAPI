import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_TEST_NAME


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client

        self.database_path = "postgres://{}/{}".format("localhost:5432", DB_TEST_NAME)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # get list of questions
    def test_get_paginated_questions(self):
        resp = self.client().get("/api/questions?page=1")
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(data["categories"])

    def test_404_request(self):
        resp = self.client().get("/api/questions?page=1000")
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(data["message"], "resource not found")

    # delete a question
    def test_delete_question(self):
        resp = self.client().delete("/api/questions/4")
        data = json.loads(resp.data)
        question = Question.query.filter(Question.id == 4).one_or_none()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(question, None)

    def test_404_if_question_does_not_exit(self):
        resp = self.client().delete("/api/questions/1000")
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 422)
        self.assertEqual(data["message"], "unprocessable")

    # search for a question
    def test_get_question_by_search(self):
        resp = self.client().post("/api/questions", json={"searchTerm": "whose"})
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(data["totalQuestions"])

    def test_search_without_result(self):
        resp = self.client().post("/api/questions", json={"searchTerm": "fan"})

    # get categories
    def test_get_categories(self):
        resp = self.client().get("/api/categories")
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(data["categories"])

    def get_test_fail_to_get_categories(self):
        resp = self.client().get("/api/categories")
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(data["success"], "false")

    # get questions by category
    def test_get_question_by_category(self):
        resp = self.client().get("/api/categories/3/questions")
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])

    def test_failed_to_get_questions_by_category(self):
        resp = self.client().get("/api/categories/1000/questions")
        data = json.loads(resp.data)
        self.assertEqual(data["success"], "false")

    # get quiz questions by category

    def test_get_quiz_question_by_category(self):
        resp = self.client().post(
            "/api/quizzes",
            json={"previous_questions": [5, 6], "quiz_category": "Sports"},
        )
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(data["questions"])

    def test_get_quiz_by_category_failed(self):
        resp = self.client().post(
            "/api/quizzes", json={"previous_questions": [6], "quiz_category": "food"}
        )
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 422)
        self.assertEqual(data["success"], "false")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
