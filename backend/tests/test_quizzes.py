import unittest
from uuid import uuid4

from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from backend.app.main import create_app


class QuizTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app())
        self.addCleanup(self.client.close)

    def test_frontend_entry_and_assets_are_served(self):
        page = self.client.get("/")
        self.assertEqual(page.status_code, 200)
        for asset in ("/static/styles.css", "/static/app.js"):
            with self.subTest(asset=asset):
                self.assertIn(asset, page.text)
                self.assertEqual(self.client.get(asset).status_code, 200)

    def test_practice_hides_answers_until_submission(self):
        response = self.client.post("/api/quizzes", json={"topic": "  python asyncio  "})
        self.assertEqual(response.status_code, 201)
        quiz = response.json()
        self.assertEqual(len(quiz["questions"]), 3)
        self.assertTrue(all(set(q) == {"question", "options"} for q in quiz["questions"]))

        url = f"/api/quizzes/{quiz['id']}/grade"
        self.assertEqual(self.client.post(url, json={"answers": ["B"]}).status_code, 422)
        grade = self.client.post(url, json={"answers": ["B", "A", "A"]})
        self.assertEqual(grade.status_code, 200)
        self.assertEqual(grade.json()["score"], 2)
        self.assertEqual(grade.json()["results"][1]["answer"], "C")
        self.assertFalse(grade.json()["results"][1]["correct"])
        self.assertTrue(grade.json()["results"][1]["explanation"])

    def test_offline_modes_report_unsupported_requests(self):
        for request in ({"topic": "SQL"}, {"topic": "LangChain", "notes": "参考资料"}, {"topic": "  "}):
            with self.subTest(request=request):
                response = self.client.post("/api/quizzes", json=request)
                self.assertEqual(response.status_code, 422)

    def test_unknown_quiz_reports_expiration(self):
        response = self.client.post(f"/api/quizzes/{uuid4()}/grade", json={"answers": ["A", "B", "C"]})
        self.assertEqual(response.status_code, 404)

    def test_invalid_model_output_is_reported_as_an_upstream_failure(self):
        model = FakeListChatModel(responses=['{"questions": []}'])
        with TestClient(create_app(model)) as client:
            response = client.post("/api/quizzes", json={"topic": "SQL", "notes": "使用 SELECT 查询数据"})
        self.assertEqual(response.status_code, 502)
        self.assertIn("格式不正确", response.json()["detail"])
