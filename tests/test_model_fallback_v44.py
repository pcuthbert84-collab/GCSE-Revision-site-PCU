import pytest
from engine import ai

def test_failover_only_for_upstream_503(monkeypatch):
    monkeypatch.setattr(ai,'get_model',lambda:'gemini-3.5-flash-lite')
    monkeypatch.setattr(ai,'get_fallback_model',lambda:'gemini-3.1-flash-lite')
    attempted=[]
    def request(body,model,timeout):
        attempted.append(model)
        if model=='gemini-3.5-flash-lite':
            raise ai.AIUnavailable('Gemini HTTP 503 (UNAVAILABLE)')
        return {'candidates':[{'content':{'parts':[{'text':'{"ok":true}'}]}}]}
    monkeypatch.setattr(ai,'_request',request)
    assert ai.request_json('test',{})=={'ok':True}
    assert attempted==['gemini-3.5-flash-lite','gemini-3.1-flash-lite']

def test_does_not_bypass_429(monkeypatch):
    monkeypatch.setattr(ai,'get_model',lambda:'gemini-3.5-flash-lite')
    monkeypatch.setattr(ai,'get_fallback_model',lambda:'gemini-3.1-flash-lite')
    attempted=[]
    def request(body,model,timeout):
        attempted.append(model)
        raise ai.AIUnavailable('Gemini HTTP 429 (RESOURCE_EXHAUSTED)')
    monkeypatch.setattr(ai,'_request',request)
    with pytest.raises(ai.AIUnavailable,match='429'):
        ai.request_json('test',{})
    assert attempted==['gemini-3.5-flash-lite']

def test_clear_message_for_both_models_unavailable(monkeypatch):
    monkeypatch.setattr(ai,'get_model',lambda:'gemini-3.5-flash-lite')
    monkeypatch.setattr(ai,'get_fallback_model',lambda:'gemini-3.1-flash-lite')
    def request(body,model,timeout):
        raise ai.AIUnavailable('Gemini HTTP 503 (UNAVAILABLE)')
    monkeypatch.setattr(ai,'_request',request)
    with pytest.raises(ai.AIUnavailable,match='Both free-tier Gemini models'):
        ai.request_json('test',{})

def test_reject_unapproved_fallback(monkeypatch):
    monkeypatch.setenv('GEMINI_FALLBACK_MODEL','gemini-3.1-pro-preview')
    assert ai.get_fallback_model()==''
