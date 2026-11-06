"""Regression tests for the V4.11 curated teaching injection."""
import unittest
from engine.academic_teaching import teaching_context
from engine.v4_ai import _payload

class AcademicTeachingTests(unittest.TestCase):
    def setUp(self):
        self.english={"name":"English Literature","code":"4ET1","board":"Pearson Edexcel"}
        self.history={"name":"History","code":"4HI1","board":"Pearson Edexcel"}
    def test_romeo_character_guidance(self):
        text=teaching_context(self.english,{"title":"Romeo and Juliet"})
        self.assertIn("character relationships",text)
        self.assertIn("do not invent quotations",text.lower())
    def test_english_unseen_poetry(self):
        text=teaching_context(self.english,{"title":"Unseen poetry"})
        self.assertIn("speaker",text)
    def test_history_medicine_guard(self):
        text=teaching_context(self.history,{"title":"Changes in Medicine 1848-1948"})
        self.assertIn("Victoria",text)
    def test_history_watergate_guard(self):
        text=teaching_context(self.history,{"title":"Watergate"})
        self.assertIn("War Powers",text)
    def test_other_subject_unaffected(self):
        text=teaching_context({"name":"Mathematics"},{"title":"Algebra"})
        self.assertEqual(text,"")
    def test_payload_includes_teaching_approach(self):
        payload=_payload(self.english,{"title":"Romeo and Juliet","kind":"school","source":"Drama and character"}, "Literature","Higher","Standard")
        self.assertIn("pedagogical",payload["approved_teaching_approach"].lower())
        self.assertEqual(payload["code"],"4ET1")
    def test_do_not_invent_source_facts(self):
        text=teaching_context(self.history,{"title":"Germany: Treaty of Versailles"})
        self.assertIn("do not fabricate",text.lower())
        self.assertNotIn("Queen Victoria",text)

if __name__=="__main__":
    unittest.main()
