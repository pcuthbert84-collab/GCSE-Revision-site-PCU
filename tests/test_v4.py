"""V4 regression / safeguarding tests, requiring no Streamlit installation or API credentials."""
from courses.v4_catalog import COURSES,topic_groups
from engine.v4_ai import create_question,create_study,evaluate,AIUnavailable,safe_source
from unittest.mock import patch
import pytest

def test_course_scope():
    assert len(COURSES)==28
    assert 'Arabic' not in COURSES and 'Islamic Education' not in COURSES
    assert COURSES['BTEC Sport']['code']=='HYP4'
    assert 'Further Mathematics' in COURSES and 'BTEC Music' in COURSES
    assert all('Level 3' not in c['kind'] for c in COURSES.values())

def test_school_map_french_spanish_not_mixed():
    fr=topic_groups('French')['Year 10 · DBSJP taught curriculum'][0]['source']
    es=topic_groups('Spanish')['Year 10 · DBSJP taught curriculum'][0]['source']
    assert 'Qui suis-je' in fr
    assert 'Desconéctate' in es
    assert 'Qui suis-je' not in es

def test_catalog_all_have_topics():
    for subject in COURSES:
        groups=topic_groups(subject)
        assert groups and all(v for v in groups.values()),subject

def test_source_text_strips_direct_identifiers():
    s=safe_source('Contact test@example.com +971 50 123 4567. Study ratios.')
    assert 'test@example.com' not in s
    assert 'Study ratios' in s

def test_ai_rejects_wrong_rubric_sum():
    c=COURSES['Mathematics'];g=topic_groups('Mathematics');name=next(iter(g));topic=g[name][0]
    q=dict(prompt='Solve 2+2.',hint='Consider addition',model_answer='4',reference_method='2 plus 2 = 4',max_marks=3,
           marking_points=[{'criterion':'Four','credit':2}])
    with patch('engine.v4_ai.request_json',return_value=q):
        with pytest.raises(AIUnavailable):create_question(c,topic,name)

def test_ai_accepts_coherent_original_question_shape():
    c=COURSES['Mathematics'];g=topic_groups('Mathematics');name=next(iter(g));topic=g[name][0]
    q=dict(prompt='Solve x + 3 = 7 and explain your working.',hint='Keep the equation balanced',model_answer='Subtract 3: x = 4.',
           reference_method='Subtract three from each side',max_marks=3,
           marking_points=[{'criterion':'Rearranges correctly','credit':2},{'criterion':'States x=4','credit':1}])
    with patch('engine.v4_ai.request_json',return_value=q):
        assert create_question(c,topic,name)['max_marks']==3

def test_low_confidence_must_be_review():
    q=dict(prompt='Explain why a method is valid',model_answer='Logical reason',marking_points=[{'criterion':'reason','credit':1}],max_marks=1)
    fake=dict(indicative_mark=0,strength='Alternative method considered',next_step='Check the step',confidence='low',needs_review=False)
    with patch('engine.v4_ai.request_json',return_value=fake):
        assert evaluate(q,'My different answer')['needs_review'] is True
