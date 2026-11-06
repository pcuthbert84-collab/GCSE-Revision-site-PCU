"""Regression tests for scope-aware study context and resource reportability."""
import unittest
from courses.scope_filters import selected_source
from engine.v4_ai import _payload

class ScopeProtectionTests(unittest.TestCase):
    def test_mixed_science_block_does_not_contaminate_bioenergetics(self):
        course={"name":"Combined Science","code":"8464"}
        topic={"title":"Y10 · Biology: Bioenergetics",
               "source":"Biology: Bioenergetics\nChemistry: Structures and Bonding",
               "kind":"school"}
        result=selected_source(course,topic)
        self.assertIn("Bioenergetics",result)
        self.assertNotIn("Chemistry",result)
        self.assertNotIn("Bonding",_payload(course,topic,"Year 10","Higher","Standard")["allowed_school_content"])
    def test_other_science_lines_not_included(self):
        course={"name":"Separate Sciences"}
        topic={"title":"Y10 · Physics: Forces","source":"Physics: Forces\nChemistry: Chemical changes\nBiology: Disease"}
        self.assertEqual(selected_source(course,topic),"Physics: Forces")
    def test_general_non_science_topics_retained(self):
        course={"name":"History"}
        topic={"title":"The New Deal","source":"Causes\nConsequences\nReactions"}
        self.assertEqual(selected_source(course,topic),topic["source"])
    def test_ambiguous_science_header_preserved_for_teacher_review(self):
        course={"name":"Combined Science"}
        topic={"title":"Year 11: Mixed science review","source":"Physics: Energy\nChemistry: Bonding"}
        self.assertEqual(selected_source(course,topic),topic["source"])
    def test_student_link_reporting_function_is_wired(self):
        # Integration check: report code is tested by a Streamlit smoke test too.
        from courses.subject_resource_atlas import topic_references
        rows=topic_references("Combined Science","Y10 · Biology: Bioenergetics",area="Year 10")
        self.assertTrue(any(x["kind"]=="direct_topic" for x in rows))

if __name__=="__main__":
    unittest.main()
