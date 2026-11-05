import pytest
from engine.ai import _parse_json_object, request_json, AIUnavailable
from engine import ai, v4_ai


def test_fenced_json_still_parseable():
    assert _parse_json_object('```json\n{"title":"Works"}\n```')['title']=='Works'


def test_bad_json_safe_failure():
    with pytest.raises(AIUnavailable,match='invalid or truncated'):
        _parse_json_object('{"title":')


def test_max_tokens_is_explained(monkeypatch):
    monkeypatch.setattr(ai,'get_model',lambda:'test')
    monkeypatch.setattr(ai,'_request',lambda *a,**k:{'candidates':[{'finishReason':'MAX_TOKENS','content':{'parts':[{'text':'{}'}]}}]})
    with pytest.raises(AIUnavailable,match='MAX_TOKENS'):
        request_json('create note',{'topic':'sample'})


def test_revision_guide_validation_detects_specific_missing_parts():
    assert 'quick_check' in v4_ai._study_validation(dict(title='Topic',explanation='x'*130,worked_example='example',outcomes=['a','b'],key_points=['a','b'],pitfalls=['a','b']))


def test_valid_short_study_guide(monkeypatch):
    response={'title':'Team-leading','explanation':'Leading a team involves assigning responsibilities and communicating clear targets. '*3,
              'worked_example':'A team leader delegates each role, then checks progress against the agreed goals.',
              'outcomes':['Describe team roles','Explain communication'],
              'key_points':['Delegation assigns responsibilities to team members','Clear milestones help leaders monitor progress','Two-way communication allows concerns to be raised','Defined roles reduce duplicated work'], 'pitfalls':['Mistake1','Mistake2'],
              'quick_check':[{'question':'What is a team?','answer':'People with shared goal'}, {'question':'Why delegate?','answer':'Match work to skills'}]}
    monkeypatch.setattr(v4_ai,'request_json',lambda *a,**k:response)
    result=v4_ai.create_study({'name':'BTEC Business'}, {'title':'Teams','source':''},'Business')
    assert result['uncertainty']==''
