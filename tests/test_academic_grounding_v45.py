import pytest
from engine import v4_ai
from engine.ai import AIUnavailable


def test_payload_uses_school_evidence_and_marks_unverified():
    data=v4_ai._payload({'name':'History','board':'Pearson Edexcel','code':'4HI1','spec_verified':False},
        {'title':'Medicine 1848–1948','kind':'school','source':'Public health; vaccination; hospitals','file':'History map.docx'},
        'Year 10','Not tiered','Standard')
    assert data['spec_verified'] is False
    assert data['allowed_school_content']=='Public health; vaccination; hospitals'
    assert data['evidence_status']=='school teaching map extract'
    assert 'History map.docx'==data['source_document']


def test_school_context_not_truncated_to_350_characters():
    excerpt='A'*500+' Photosynthesis and respiration in plants.'
    assert 'Photosynthesis' in v4_ai.safe_source(excerpt)


def test_generic_outcomes_fail_validation():
    r={'title':'Teams','explanation':'Team leadership involves communicating with members and allocating roles. '*3,
       'worked_example':'A leader assigns customer-service and stock-control tasks, and then reviews deadlines.',
       'outcomes':['Explain the key ideas in Teams','Apply the ideas in Teams'],
       'key_points':['A team needs a clear and shared purpose','A leader delegates to match skills and tasks'],
       'pitfalls':['Tasks are not assigned to individuals','The leader never checks progress against targets'],
       'quick_check':[{'question':'What is delegation?','answer':'Assigning responsibilities'},
                      {'question':'Why track progress?','answer':'Identify risks to deadlines'}]}
    assert 'generic' in v4_ai._study_validation(r).lower()


def test_question_prompt_rejects_invented_coursework_requirements():
    assert 'Do NOT fabricate' in v4_ai.QUESTION_RULES
    assert 'official coursework task' in v4_ai.QUESTION_RULES
    assert 'alternative' in v4_ai.FEEDBACK_RULES


def test_mini_outcomes_not_silently_invented():
    raw={'explanation':'Explanation '*20,'worked_example':'Worked example','key_points':['A sufficiently detailed point one','A sufficiently detailed point two'],
         'pitfalls':['One misconception','Another misconception'],
         'quick_check':[{'question':'Q1','answer':'A1'},{'question':'Q2','answer':'A2'}]}
    with pytest.raises(AIUnavailable,match='outcomes'):
        v4_ai._normalize_mini_study(raw,{'title':'Teams'})
