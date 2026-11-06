"""Read Corbettmaths' published Videos and Worksheets index.

The index is the authority for titles and URLs. We NEVER construct a lesson URL
from a video number, a topic string or a language model. The site index is fetched
at runtime with a bounded timeout; failure produces no speculative links.
"""
from __future__ import annotations

import re
import unicodedata
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from engine.quality_store import validate_direct_url

INDEX_URL = 'https://corbettmaths.com/contents/'
HEADERS = {'User-Agent':'DBSJP-Revision-Hub/4.10 (educational resource catalogue; request once per cache period)'}


def normalize(value):
    value = unicodedata.normalize('NFKD', str(value or '')).casefold()
    value = value.replace('&', ' and ').replace('–', '-').replace('—','-')
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', value)).strip()


def _safe_external_url(link):
    if not link: return None
    url = urljoin(INDEX_URL,link.strip())
    host = (urlparse(url).hostname or '').lower()
    if host not in {'corbettmaths.com','www.corbettmaths.com'}: return None
    try: return validate_direct_url(url)
    except ValueError: return None


def _row_from_tag(tag):
    """One index row, supporting the WordPress paragraphs and table cells."""
    raw = tag.get_text(' ', strip=True)
    m = re.search(r'\bVideo\s+(\d+[a-z]?)\b', raw, re.I)
    if not m: return None
    # Everything before the first video link is the published topic title.
    title = raw[:m.start()].strip(' \u00a0\u200b\u2013-:')
    if len(title) < 2 or len(title) > 140: return None
    # A single row contains exactly one labelled video. If it contains multiple,
    # this is likely the parent block and must not be treated as a single row.
    if len(re.findall(r'\bVideo\s+\d+[a-z]?\b', raw, re.I)) != 1: return None
    links = {'video':None,'practice':None,'textbook':None}
    for a in tag.find_all('a'):
        label = a.get_text(' ',strip=True).lower()
        url = _safe_external_url(a.get('href'))
        if not url: continue
        if re.search(r'\bvideo\s+\d+', label): links['video']=url
        elif 'practice question' in label: links['practice']=url
        elif 'textbook exercise' in label: links['textbook']=url
    if not any(links.values()): return None
    return {'title':title, 'key':normalize(title),'video_number':m.group(1), **links, 'source':INDEX_URL}


def parse_index(html):
    soup = BeautifulSoup(html,'html.parser')
    records = []
    for tag in soup.find_all(['p','li','tr']):
        if tag.find_parent(['p','li','tr']): continue
        rec = _row_from_tag(tag)
        if rec: records.append(rec)
    # Some WordPress themes use heading-free line breaks inside a single div;
    # parse plain non-nested leaf containers in that case.
    if not records:
        for tag in soup.find_all(['div']):
            if tag.find(['p','li','tr','div']): continue
            rec=_row_from_tag(tag)
            if rec: records.append(rec)
    # Preserve distinct video numbers but de-duplicate DOM copies.
    seen=set(); out=[]
    for row in records:
        key=(row['key'],row['video_number'],row['video'])
        if key in seen: continue
        seen.add(key);out.append(row)
    return out


def fetch_catalogue(session=None):
    client=session or requests
    response=client.get(INDEX_URL,timeout=(5,18),headers=HEADERS)
    response.raise_for_status()
    rows=parse_index(response.text)
    if len(rows)<100:
        raise ValueError(f'Corbettmaths index returned only {len(rows)} index rows; catalogue was not accepted.')
    return rows


def resources_for_entry(entry, topic):
    if not entry: return []
    items=[]
    for kind,title in [('video','Teaching video'),('practice','Practice questions'),('textbook','Textbook exercise')]:
        url=entry.get(kind)
        if not url: continue
        try: validate_direct_url(url)
        except ValueError: continue
        items.append({'subject':'Mathematics','topic':topic,
                      'title':f"Corbettmaths · {entry['title']} · {title}" + (f" {entry['video_number']}" if kind=='video' else ''),
                      'provider':'Corbettmaths','url':url,'status':'approved',
                      'source':'direct link published in Corbettmaths topic index'})
    return items


def exact_matches(entries,topic):
    """Exact published-title equality; no substring / fuzzy autosuggestions."""
    key=normalize(topic)
    return [r for r in entries if key and r['key']==key]


def automatic_resources(entries, subject, topic):
    if subject!='Mathematics': return []
    rows=exact_matches(entries,topic)
    # Multiple index rows with one title may be different skills and require review.
    if len(rows)!=1: return []
    return resources_for_entry(rows[0],topic)


def candidate_matches(entries,topic,source='',max_items=32):
    """Unapproved admin suggestions. Never used for automatic student links."""
    # Course-map blocks have multiple teaching lines. Match exact lines to index
    # headings first, then present broader fuzzy matches only for manual review.
    parts=[]
    for line in (str(topic)+'\n'+str(source)).splitlines():
        clean=re.sub(r'^\s*(?:Y1[01]\s*[·:-]\s*|\d+(?:\.\d+)?\s+)', '',line).strip()
        key=normalize(clean)
        if len(key)>=4 and key not in parts:parts.append(key)
    exact=[r for r in entries if r['key'] in parts]
    # A broad title like "Graphs" could match dozens; require 2+ useful tokens
    # for fuzzy suggestions and never treat them as approved.
    fuzzy=[]
    for r in entries:
        if r in exact: continue
        tokens=r['key'].split()
        if len(tokens)>=2 and any(len(p)>7 and (r['key'] in p or p in r['key']) for p in parts):
            fuzzy.append(r)
    return [{'entry':r,'match':'index title matches a curriculum-map line' if r in exact else 'possible match — review required'}
            for r in (exact+fuzzy)[:max_items]]
