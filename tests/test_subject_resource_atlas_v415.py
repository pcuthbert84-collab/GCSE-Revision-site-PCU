"""V4.15 regression tests for specification matching and resource safety."""
import unittest
from courses.subject_resource_atlas import (
    OFFICIAL,PMT_TOPIC_PAGES,qualification_reference,directory_resources,
    topic_references,pmt_topic_resources,metadata_for_ai,SEPARATE_SCIENCE_SPECS
)

def course(name,code):
    return {"name":name,"code":code}

class ResourceAtlasTests(unittest.TestCase):
    def test_correct_4xge1_modular_route(self):
        row=qualification_reference(course("Geography","4XGE1"))
        self.assertIn("geography-2023-modular.html",row["url"])
        self.assertNotIn("2017",row["url"])
    def test_do_not_link_wrong_code(self):
        self.assertIsNone(qualification_reference(course("Geography","4GE1")))
        self.assertIsNone(qualification_reference(course("English Literature","4EA1")))
        self.assertIsNone(qualification_reference(course("Random","0000")))
    def test_verified_science_qualifications(self):
        self.assertEqual(len(SEPARATE_SCIENCE_SPECS),3)
        self.assertEqual({x["title"].split(" · ")[1].split()[0] for x in SEPARATE_SCIENCE_SPECS},
                         {"8461","8462","8463"})
        self.assertIsNone(qualification_reference(course("Separate Sciences","8461 / 8462 / 8463")))
    def test_exact_science_topic_page(self):
        result=pmt_topic_resources("Combined Science","Cell biology","Biology · Course topics")
        self.assertEqual(len(result),1)
        self.assertTrue(result[0]["url"].endswith("/cell-biology/"))
        self.assertEqual(result[0]["kind"],"direct_topic")
    def test_no_wrong_discipline(self):
        self.assertEqual(pmt_topic_resources("Combined Science","Energy","Chemistry · Course topics"),[])
        self.assertEqual(pmt_topic_resources("Combined Science","Atomic structure",""),[])
        self.assertEqual(pmt_topic_resources("History","Cell biology",""),[])
    def test_space_physics_not_trilogy(self):
        self.assertEqual(pmt_topic_resources("Combined Science","Space physics","Physics"),[])
        self.assertEqual(len(pmt_topic_resources("Separate Sciences","Space physics","Physics")),1)
    def test_no_fuzzy_student_matching(self):
        self.assertEqual(pmt_topic_resources("Combined Science","Y10 General Science Block","Biology"),[])
        self.assertEqual(pmt_topic_resources("Combined Science","Biology revision","Biology"),[])
    def test_all_pmt_topic_pages_are_unique_and_https(self):
        urls=[x[2] for x in PMT_TOPIC_PAGES]
        self.assertEqual(len(urls),25)
        self.assertEqual(len(urls),len(set(urls)))
        self.assertTrue(all(u.startswith("https://www.physicsandmathstutor.com/") for u in urls))
    def test_4bs1_course_2017_not_2027(self):
        row=qualification_reference(course("Business Studies","4BS1"))
        self.assertIn("business-2017.html",row["url"])
    def test_directory_label_not_exact(self):
        resources=directory_resources("Computer Science")
        self.assertTrue(resources)
        self.assertTrue(all(item["kind"]=="directory" for item in resources))
    def test_no_ai_webpage_text_claims(self):
        text=metadata_for_ai(course("Geography","4XGE1"),{"title":"Coasts"})
        self.assertIn("not fetched by model",text)
        self.assertIn("not yet audited",text)
        self.assertNotIn("measured fieldwork",text)
    def test_subject_specific_mdn(self):
        resources=topic_references("BTEC Information Technology","Website development")
        self.assertTrue(any("developer.mozilla.org" in item["url"] for item in resources))

if __name__=="__main__":
    unittest.main()
