import pytest
from engine import v4_ai
from engine.ai import AIUnavailable


def _mini():
    return dict(explanation='Effective leadership involves clear goals, communication, appropriate delegation and regular progress checks. The leader should adapt their approach to the needs of the team and task. Delegation helps colleagues contribute their strengths while staying accountable. Specific targets allow progress to be monitored and misunderstandings to be corrected early. A good leader listens to suggestions, responds to problems and checks that everyone understands their responsibilities.',worked_example='A team leader assigns research and presentation tasks by strength, agrees a deadline, then checks progress halfway through.',key_points=['Set clear objectives','Delegate according to capability','Monitor progress'],pitfalls=['Assume everyone knows their role','Avoid checking progress'],quick_check=[{'question':'What is delegation?','answer':'Assigning responsibilities appropriately'},{'question':'Why monitor progress?','answer':'To identify issues early'}])


def test_compact_study_is_valid(monkeypatch):
    monkeypatch.setattr(v4_ai,'request_json',lambda *a,**k:_mini())
    result=v4_ai.create_study({'name':'BTEC Business'},{'title':'Team-leading','source':''},'Business',compact=True)
    assert result['title']=='Team-leading'
    assert len(result['quick_check'])==2


def test_http_503_falls_back_to_smaller_guide(monkeypatch):
    calls=[]
    def fake_request(*a,**k):
        calls.append(k['max_output_tokens'])
        if len(calls)==1:raise AIUnavailable('Gemini HTTP 503 (UNAVAILABLE): service unavailable')
        return _mini()
    monkeypatch.setattr(v4_ai,'request_json',fake_request)
    result=v4_ai.create_study({'name':'BTEC Business'},{'title':'Team-leading','source':''},'Business')
    assert calls==[3072,2048]
    assert result['title']=='Team-leading'


def test_double_503_is_honest_failure(monkeypatch):
    def unavailable(*a,**k):raise AIUnavailable('Gemini HTTP 503 (UNAVAILABLE): overloaded')
    monkeypatch.setattr(v4_ai,'request_json',unavailable)
    with pytest.raises(AIUnavailable,match='temporarily unable'):
        v4_ai.create_study({'name':'BTEC Business'},{'title':'Team-leading','source':''},'Business')
