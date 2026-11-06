"""V4.13 tests for equal learning and exam-practice pathways."""
import unittest
from engine.learning_path import learning_checks, suggested_route

class LearningPathTests(unittest.TestCase):
    def test_ai_checks_prioritised(self):
        ai={"quick_check":[
            {"question":"What is a cause?","answer":"A factor contributing to an event."},
            {"question":"What is a consequence?","answer":"An outcome of the event."},
            {"question":"Too many","answer":"Do not display"}]}
        assert len(learning_checks(ai))==2
        self.assertEqual(learning_checks(ai)[0]["question"],"What is a cause?")
    def test_local_question_fallback(self):
        local={"questions":[{"prompt":"Explain one consequence.","model":"A supported explanation."}]}
        self.assertEqual(learning_checks({},local)[0]["answer"],"A supported explanation.")
    def test_missing_and_malformed_content(self):
        self.assertEqual(learning_checks({"quick_check":[{"question":"Incomplete"}]},{}),[])
        self.assertEqual(learning_checks(None,None),[])
    def test_review_for_unmarked(self):
        self.assertEqual(suggested_route(None,8)[0],"review")
        self.assertEqual(suggested_route(6,8,uncertain=True)[0],"review")
        self.assertEqual(suggested_route(3,0)[0],"review")
    def test_learning_recommendation(self):
        self.assertEqual(suggested_route(1,8)[0],"learn")
        self.assertEqual(suggested_route(5,8)[0],"improve")
        self.assertEqual(suggested_route(7,8)[0],"challenge")
    def test_boundaries(self):
        self.assertEqual(suggested_route(4,8)[0],"improve")
        self.assertEqual(suggested_route(8,8)[0],"challenge")

if __name__=="__main__":
    unittest.main()
