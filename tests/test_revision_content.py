from courses.catalog import CATALOG
from courses.revision_content import CONTENT

def test_curated_topics_exist_in_course_catalogue():
    for (subject, topic), content in CONTENT.items():
        assert subject in CATALOG
        assert any(topic in topics for topics in CATALOG[subject]['themes'].values())
        assert content['goal'] and len(content['points']) >= 3
        assert content['example'] and content['mistake']
        for q in content['questions']:
            assert q['prompt'] and q['hint'] and q['model']
            assert len(q['points']) >= 2
