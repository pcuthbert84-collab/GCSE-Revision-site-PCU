from courses.verified_resources import corbett_resources, topic_resources
from engine.quality_store import blank_store


def test_standard_form_three_direct_verified_resources():
    entries=corbett_resources('Mathematics','Standard Form')
    assert len(entries)==3
    assert 'Video 300' in entries[0]['title']
    assert entries[0]['url']=='https://corbettmaths.com/2013/04/28/standard-form/'
    assert entries[1]['url']=='https://corbettmaths.com/2019/08/29/standard-form-practice-questions/'
    assert entries[2]['url']=='https://corbettmaths.com/2019/10/07/standard-form-textbook-exercise/'
    assert len(topic_resources(blank_store(),'Mathematics','Standard Form'))==3


def test_extended_standard_form_has_distinct_video():
    for topic, number in [('Standard Form: Addition','301'),('Standard Form: Multiplication','302'),('Standard Form: Division','303')]:
        entries=corbett_resources('Mathematics',topic)
        assert len(entries)==3
        assert 'Video '+number in entries[0]['title']
        assert 'Video 300' not in entries[0]['title']


def test_vectors_are_separate_topics_and_no_fabricated_textbook():
    assert len(corbett_resources('Mathematics','Vectors'))==2
    assert len(corbett_resources('Mathematics','Column Vectors'))==3


def test_no_generic_homepages_and_no_loose_matching():
    for label in ['Standard', 'Averages', 'Algebraic fractions', 'Transformations of vectors', 'Vectors and transformations']:
        assert corbett_resources('Mathematics',label)==[]
    assert corbett_resources('History','Standard Form')==[]
    for topic in ['Standard Form','Vectors','Column Vectors']:
        assert all(r['url']!='https://corbettmaths.com/contents/' for r in corbett_resources('Mathematics',topic))
