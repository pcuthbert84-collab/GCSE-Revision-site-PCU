from courses.catalog import CATALOG,all_topics
from engine.offline import question
from courses.maths_4ma1 import SKILLS

def test_catalog_paths():
    assert len(CATALOG)>=25
    assert all_topics()>=200
    for name,c in CATALOG.items():
        assert c['themes'],name
        assert all(v for v in c['themes'].values())
        for area,topics in c['themes'].items():
            for topic in topics:
                q=question(c,area,topic)
                assert topic in q['prompt']
                assert q['marking_points']

def test_math_active_topics_present():
    all_themes=[t for a in CATALOG['Mathematics']['themes'].values() for t in a]
    for topic,skills in SKILLS.items():
        if any(s['enabled'] for s in skills):
            assert topic.split(' ',1)[-1] in all_themes

def test_qualifications_labeled():
    assert CATALOG['Mathematics']['code']=='4MA1'
    assert CATALOG['Combined Science']['code']=='8464'
    assert not CATALOG['History']['spec_verified']
