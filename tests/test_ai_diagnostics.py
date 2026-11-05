import pytest
from engine.ai import _safe_api_message, _extract_text, AIUnavailable

def test_quota_message():
    msg=_safe_api_message(429, '{"error":{"status":"RESOURCE_EXHAUSTED","message":"hidden sensitive request data"}}')
    assert '429' in msg and 'quota' in msg.lower()
    assert 'hidden sensitive' not in msg

def test_model_not_found_message():
    assert 'Model not found' in _safe_api_message(404, '{"error":{"status":"NOT_FOUND"}}')

def test_multichunk_json():
    assert _extract_text({'candidates':[{'content':{'parts':[{'text':'{"status"'},{'text':':"ok"}'}]}}]}) == '{"status"\n:"ok"}'

def test_empty_candidate_message():
    with pytest.raises(AIUnavailable,match='no text'):
        _extract_text({'candidates':[{'content':{'parts':[]},'finishReason':'MAX_TOKENS'}]})
