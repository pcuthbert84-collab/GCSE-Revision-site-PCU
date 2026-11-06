import pytest
from courses.verified_resources import seeded_resources, topic_resources
from engine.quality_store import (blank_store, approve_rule, active_rules, validate_direct_url,
                                  add_resource, matching_resources, archive, password_valid,
                                  load, save)
from engine.v4_ai import _approved_rule_appendix


def test_exact_resource_links_only():
    resources=seeded_resources('Mathematics','Solving quadratic equations by factorisation')
    assert resources and all('corbettmaths.com/' in r['url'] for r in resources)
    assert not seeded_resources('Mathematics','Quadratic formula') == resources
    assert not seeded_resources('Mathematics','Statistics: averages')
    assert not seeded_resources('History','Solving quadratic equations by factorisation')
    assert not seeded_resources('BTEC Business Studies','Teams and team-leading')


def test_no_generic_homepages_search_or_untrusted_links():
    for url in ('https://www.bbc.co.uk', 'https://corbettmaths.com/',
                'https://www.google.com/search?q=quadratic',
                'https://corbettmaths.com/contents/',
                'http://corbettmaths.com/2013/05/03/solving-quadratics-by-factorising/',
                'https://evil.example/course', 'https://corbettmaths.com.evil.example/topic'):
        with pytest.raises(ValueError): validate_direct_url(url)
    assert validate_direct_url('https://corbettmaths.com/2013/05/03/solving-quadratics-by-factorising/')


def test_reviewed_corrections_are_scoped_and_archivable():
    base=blank_store()
    revised=approve_rule(base,scope='topic',subject='Mathematics',topic='Percentage change',
                         correction='Accept a correct two-stage calculation, even if it differs from the exemplar.')
    assert base['rules']==[]
    assert len(active_rules(revised,'Mathematics','Percentage change'))==1
    assert active_rules(revised,'Mathematics','Quadratic formula')==[]
    assert active_rules(revised,'History','Percentage change')==[]
    assert 'ADMIN-APPROVED' in _approved_rule_appendix(active_rules(revised,'Mathematics','Percentage change'))
    archived=archive(revised,revised['rules'][0]['id'])
    assert active_rules(archived,'Mathematics','Percentage change')==[]
    assert len(archived['audit'])==2


def test_admin_approved_link_exact_match():
    d=add_resource(blank_store(),subject='Mathematics',topic='Quadratic formula',
                   title='Quadratic formula — video lesson',
                   url='https://corbettmaths.com/2013/04/24/quadratic-formula/',
                   provider='Corbettmaths',reviewer_note='Checked exact content for level and topic')
    # Code does not pretend the title or URL alone proves academic relevance: admin must check.
    assert len(matching_resources(d,'Mathematics','Quadratic formula'))==1
    assert not matching_resources(d,'Mathematics','Ratio')
    assert not matching_resources(d,'History','Quadratic formula')
    with pytest.raises(ValueError):
        add_resource(d,subject='Mathematics',topic='Quadratic formula',title='Some lesson',
                     url='https://corbettmaths.com/2013/04/24/quadratic-formula/',
                     provider='Corbettmaths',reviewer_note='Checked exact content for level and topic')


def test_no_silent_durable_save_without_secrets(monkeypatch):
    import engine.quality_store as qs
    monkeypatch.setattr(qs,'_settings',lambda:{'repo':'','token':'','password':'','branch':'main'})
    with pytest.raises(RuntimeError,match='No change has been saved'):
        qs.save(blank_store(),None,action='test')


def test_password_check(monkeypatch):
    import engine.quality_store as qs
    monkeypatch.setattr(qs,'_settings',lambda:{'repo':'owner/repo','token':'abc','password':'secret-word','branch':'main'})
    assert qs.password_valid('secret-word')
    assert not qs.password_valid('wrong')


def test_github_content_api_round_trip(monkeypatch):
    """GitHub-backed rules survive app restarts; an optimistic SHA is sent on save."""
    import base64, json
    import engine.quality_store as qs
    settings={'repo':'school/private-revision-hub','token':'test-token','password':'long-admin-password','branch':'main'}
    monkeypatch.setattr(qs,'_settings',lambda:settings)
    start=qs.approve_rule(qs.blank_store(),scope='all',subject='',topic='',
                          correction='Accept every equivalent mathematically correct working method.')
    history=[]

    class Reply:
        def __init__(self,status,jsondata): self.status_code=status;self._data=jsondata
        @property
        def ok(self): return self.status_code==200 or self.status_code==201
        def json(self): return self._data

    def fake_get(url,**kwargs):
        assert 'school/private-revision-hub/contents/data/academic_quality.json' in url
        body=base64.b64encode(json.dumps(start).encode()).decode()
        return Reply(200,{'content':body,'sha':'sha-before'})

    def fake_put(url,**kwargs):
        body=kwargs['json']
        assert body['sha']=='sha-before'
        assert body['branch']=='main'
        assert 'Accept every equivalent' in base64.b64decode(body['content']).decode()
        history.append(body)
        return Reply(200,{'content':{'sha':'sha-after'}})

    monkeypatch.setattr(qs.requests,'get',fake_get)
    monkeypatch.setattr(qs.requests,'put',fake_put)
    current,sha,durable=qs.load()
    assert durable and sha=='sha-before' and len(current['rules'])==1
    assert qs.save(current,sha,action='new rule')=='sha-after'
    assert len(history)==1
