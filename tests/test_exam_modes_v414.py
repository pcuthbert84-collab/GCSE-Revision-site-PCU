"""V4.14 regression tests: exact exam-practice modes and cautious marking."""
import unittest
from unittest.mock import patch
from engine.exam_modes import exam_modes, exam_instruction
from engine.v4_ai import _validate_question, create_exam_question
from engine.ai import AIUnavailable

HISTORY={"name":"History","code":"4HI1","kind":"International GCSE"}
LITERATURE={"name":"English Literature","code":"4ET1","kind":"International GCSE"}
LANGUAGE={"name":"English Language","code":"4EA1","kind":"International GCSE"}
MATHS={"name":"Mathematics","code":"4MA1","kind":"International GCSE"}

class ExamModeTests(unittest.TestCase):
    def test_history_marks_and_relevant_comparison(self):
        modes=exam_modes(HISTORY,"Year 11 Medicine",{"title":"Changes in Surgery"})
        expected={m["id"]:m["marks"] for m in modes}
        self.assertEqual(expected["history_evaluate"],16)
        self.assertEqual(expected["history_effects"],8)
        self.assertEqual(expected["history_compare"],6)
        modes=exam_modes(HISTORY,"Year 10",{"title":"The Vietnam War"})
        self.assertNotIn("history_compare",[m["id"] for m in modes])
    def test_unseen_poetry(self):
        ids=[m["id"] for m in exam_modes(LITERATURE,"Poetry",{"title":"Unseen poetry"})]
        self.assertIn("literature_unseen",ids)
        self.assertNotIn("literature_essay",ids)
    def test_literary_essay(self):
        ids=[m["id"] for m in exam_modes(LITERATURE,"Drama",{"title":"Romeo and Juliet"})]
        self.assertIn("literature_essay",ids)
    def test_transactional_writing_not_official_allocation(self):
        modes=exam_modes(LANGUAGE,"English Language",{"title":"Transactional writing"})
        chosen=next(m for m in modes if m["id"]=="language_writing")
        self.assertEqual(chosen["marks"],30)
        self.assertIn("NOT the official",chosen["description"])
    def test_maths_retains_existing_engine(self):
        self.assertEqual([x["id"] for x in exam_modes(MATHS,"Algebra",{"title":"Vectors"})],["short"])
    def test_invalid_generated_mark_totals_rejected(self):
        draft={"prompt":"Explain two effects of a historical event.",
               "model_answer":"Each effect needs a contextual explanation.",
               "hint":"Think of two distinct impacts.",
               "max_marks":16,
               "marking_points":[{"criterion":"First supported effect", "credit":4},
                                 {"criterion":"Second supported effect","credit":4}]}
        self.assertIn("add up",_validate_question(draft,max_allowed=30))
        self.assertIsNone(_validate_question({**draft,"marking_points":[
            {"criterion":str(i)+" developed criterion","credit":4} for i in range(4)]},
            max_allowed=30))
        self.assertIsNotNone(_validate_question(draft))
    @patch("engine.v4_ai.request_json")
    def test_extended_question_must_match_chosen_marks(self,mock_request):
        mock_request.return_value={
            "prompt":"Explain two effects of an original topic event.",
            "model_answer":"Two independently explained consequences.",
            "hint":"Think how each consequence arose.",
            "max_marks":4,
            "marking_points":[{"criterion":"Accurate initial effect","credit":1},
                              {"criterion":"Developed explanation","credit":1},
                              {"criterion":"Second effect explained","credit":1},
                              {"criterion":"Accurate evidence","credit":1}]}
        mode=next(x for x in exam_modes(HISTORY,"Germany",{"title":"Treaty of Versailles"})
                  if x["id"]=="history_evaluate")
        with self.assertRaises(AIUnavailable):
            create_exam_question(HISTORY,{"title":"Treaty of Versailles","kind":"school","source":"Terms and consequences."},
                                 "Germany",mode)
    def test_prompt_rejects_fake_historical_sources(self):
        mode=next(x for x in exam_modes(HISTORY,"Germany",{"title":"Treaty of Versailles"})
                  if x["id"]=="history_evaluate")
        prompt=exam_instruction(mode,HISTORY,{"title":"Treaty of Versailles"})
        self.assertIn("original",prompt.lower())
        self.assertIn("16",prompt)

if __name__=="__main__":
    unittest.main()
