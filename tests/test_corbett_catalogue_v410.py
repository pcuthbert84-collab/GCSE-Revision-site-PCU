from courses.corbett_catalogue import parse_index,automatic_resources,candidate_matches,resources_for_entry,fetch_catalogue
from engine.quality_store import blank_store,add_resource,matching_resources
from courses.verified_resources import topic_resources
import pytest


def mock_html(n=120):
    rows=[]
    for i in range(n):
        name='Standard form' if i==0 else ('Vectors' if i==1 else f'Maths topic {i}')
        num=300 if i==0 else 353 if i==1 else i
        slug='standard-form' if i==0 else 'vectors' if i==1 else f'lesson-{i}'
        rows.append(f'<p>{name}&nbsp; <a href="https://corbettmaths.com/2013/04/28/{slug}/">Video {num}</a> '
                    f'<a href="https://corbettmaths.com/2019/08/29/{slug}-practice-questions/">Practice Questions</a> '
                    f'<a href="https://corbettmaths.com/2019/10/07/{slug}-textbook-exercise/">Textbook Exercise</a></p>')
    return '<html><body>'+''.join(rows)+'</body></html>'


def test_parse_full_publisher_index_and_direct_links():
    rows=parse_index(mock_html())
    assert len(rows)==120
    assert rows[0]['video_number']=='300'
    assert rows[0]['video'].endswith('/standard-form/')
    assert rows[0]['practice'].endswith('/standard-form-practice-questions/')
    assert rows[0]['textbook'].endswith('/standard-form-textbook-exercise/')
    assert len(automatic_resources(rows,'Mathematics','Standard form'))==3
    assert not automatic_resources(rows,'Science','Standard form')


def test_does_not_invent_missing_links():
    html='<p>Vectors <a href="https://corbettmaths.com/2016/04/25/vectors/">Video 353</a></p>'
    r=parse_index(html)[0]
    assert [x['url'] for x in resources_for_entry(r,'Vectors')]==['https://corbettmaths.com/2016/04/25/vectors/']


def test_vague_topic_never_auto_match():
    rows=parse_index(mock_html())
    assert automatic_resources(rows,'Mathematics','Maths')==[]
    assert automatic_resources(rows,'Mathematics','Standard')==[]
    assert automatic_resources(rows,'Mathematics','Year 10 Standard Form')==[]
    assert candidate_matches(rows,'Y10 · Number 6','Number 6\nStandard form')[0]['entry']['title']=='Standard form'


def test_duplicitous_same_name_requires_admin_review():
    rows=parse_index(mock_html(2))
    rows.append({**rows[0],'video_number':'300a','video':'https://corbettmaths.com/2014/05/01/standard-form-advanced/'})
    assert automatic_resources(rows,'Mathematics','Standard form')==[]


def test_non_provider_links_are_excluded():
    html='<p>Standard form <a href="https://example.com/fake">Video 300</a> <a href="https://corbettmaths.com/contents/">Practice Questions</a></p>'
    assert parse_index(html)==[]


def test_bad_index_fails_safely():
    class Response:
        text='<html><p>hello</p></html>'
        def raise_for_status(self): pass
    class Client:
        def get(self,*a,**kw):return Response()
    with pytest.raises(ValueError,match='not accepted'):
        fetch_catalogue(Client())


def test_approved_bundle_persists_for_exact_topic():
    rows=parse_index(mock_html(2))
    data=blank_store()
    for item in resources_for_entry(rows[1],'Y11 · Graphs 7'):
        data=add_resource(data,subject='Mathematics',topic='Y11 · Graphs 7',title=item['title'],url=item['url'],provider='Corbettmaths',reviewer_note='Reviewed against curriculum map and source pages.')
    assert len(matching_resources(data,'Mathematics','Y11 · Graphs 7'))==3
    assert len(topic_resources(data,'Mathematics','Y11 · Graphs 7'))==3
    assert not matching_resources(data,'Mathematics','Y10 · Number 6')
