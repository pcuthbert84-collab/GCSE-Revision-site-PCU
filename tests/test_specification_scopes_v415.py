"""V4.15 regression tests: model context stays concise and qualified."""
import unittest
from courses.specification_scopes import SCOPES,specification_scope
from engine.v4_ai import _payload

class QualificationScopeTests(unittest.TestCase):
    def test_every_mapped_subject_has_an_independent_scope(self):
        from courses.v4_catalog import COURSES
        missing=[name for name in COURSES if name not in SCOPES]
        self.assertFalse(missing, f"Missing subject scope: {missing}")
    def test_correct_geography_route(self):
        text=specification_scope({"name":"Geography","code":"4XGE1"},{"title":"Coasts"})
        self.assertIn("4WGE1",text)
        self.assertIn("4WGE2",text)
        self.assertIn("4XGE1",text)
    def test_combined_versus_separate_science(self):
        combined=specification_scope({"name":"Combined Science"},{"title":"Energy"})
        separate=specification_scope({"name":"Separate Sciences"},{"title":"Energy"})
        self.assertIn("8464",combined)
        self.assertIn("8461",separate)
        self.assertIn("8462",separate)
        self.assertIn("8463",separate)
        self.assertIn("Space Physics",combined)
    def test_business_new_route_not_silently_substituted(self):
        text=specification_scope({"name":"Business Studies"},{"title":"Marketing"})
        self.assertIn("4BS1",text)
        self.assertIn("September 2027",text)
    def test_ai_payload_has_scope_and_authoritative_code_metadata(self):
        course={"name":"Geography","code":"4XGE1","board":"Pearson Edexcel"}
        topic={"title":"Coasts","source":"Waves, erosion, deposition","kind":"school"}
        payload=_payload(course,topic,"Physical Geography","Not tiered","Standard")
        self.assertIn("4WGE1",payload["curated_specification_scope"])
        self.assertIn("not fetched by model",payload["official_qualification_reference"])
        self.assertEqual(payload["topic"],"Coasts")
    def test_no_unrequested_generic_profile(self):
        self.assertEqual(specification_scope({"name":"Unknown"},{"title":"Something"}),"")

if __name__=="__main__":
    unittest.main()
