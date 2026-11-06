import pytest
from engine import v4_ai
from engine.ai import AIUnavailable

COURSE = {'name':'Mathematics','board':'Pearson Edexcel','code':'4MA1','spec_verified':False}
TOPIC = {'title':'Vectors','kind':'index','source':''}


def sample_question(**changes):
    obj = {'prompt':'Find the vector from A(2, 3) to B(5, 8).',
           'hint':'Subtract the coordinates in the same order.',
           'model_answer':'(5-2, 8-3) = (3, 5).',
           'max_marks':2,
           'marking_points':[{'criterion':'Subtract x coordinates correctly', 'credit':1},
                             {'criterion':'Subtract y coordinates correctly', 'credit':1}]}
    obj.update(changes)
    return obj


def test_absent_reference_method_is_valid_for_any_subject():
    result = v4_ai._complete_question(sample_question())
    assert result['reference_method']==''
    assert result['question_type']=='Original practice question'


def test_short_but_valid_hint_is_accepted():
    assert v4_ai._validate_question(sample_question(hint='Use subtraction.')) is None


def test_wrong_credit_sum_rejected():
    error=v4_ai._validate_question(sample_question(max_marks=3))
    assert 'add up' in error


def test_missing_hint_triggers_one_compact_retry(monkeypatch):
    seen=[]
    def fake_request(instructions,payload,max_output_tokens=8192):
        seen.append((instructions,max_output_tokens))
        return sample_question(hint='') if len(seen)==1 else sample_question()
    monkeypatch.setattr(v4_ai,'request_json',fake_request)
    q=v4_ai.create_question(COURSE,TOPIC,'Vectors')
    assert len(seen)==2 and seen[0][1]==3072 and seen[1][1]==2048
    assert 'COMPACT' not in q['prompt']


def test_valid_question_does_not_use_second_api_request(monkeypatch):
    seen=[]
    def fake_request(*args,**kwargs):
        seen.append(True)
        return sample_question()
    monkeypatch.setattr(v4_ai,'request_json',fake_request)
    assert v4_ai.create_question(COURSE,TOPIC,'Vectors')['max_marks']==2
    assert len(seen)==1


def test_quota_failure_does_not_retry(monkeypatch):
    seen=[]
    def fake_request(*args,**kwargs):
        seen.append(True)
        raise AIUnavailable('Gemini HTTP 429: quota exceeded')
    monkeypatch.setattr(v4_ai,'request_json',fake_request)
    with pytest.raises(AIUnavailable, match='429'):
        v4_ai.create_question(COURSE,TOPIC,'Vectors')
    assert len(seen)==1


def test_failure_after_retry_is_explicit(monkeypatch):
    monkeypatch.setattr(v4_ai,'request_json',lambda *args,**kwargs: sample_question(hint=''))
    with pytest.raises(AIUnavailable,match='after a compact retry'):
        v4_ai.create_question(COURSE,TOPIC,'Vectors')
