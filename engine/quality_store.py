"""Server-side persistence of approved academic rules and vetted resource links.

Uses a GitHub private repository through Contents API when configured. Cloud Streamlit
filesystems are ephemeral: without GitHub configuration this runs in explicit preview
mode, and cannot claim a durable save. No client-side storage or student accounts.
"""
import base64
import copy
import hmac
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import requests

DATA_PATH = 'data/academic_quality.json'
LOCAL_PATH = Path(__file__).resolve().parents[1] / DATA_PATH
ALLOWED_DOMAINS = {'corbettmaths.com', 'www.corbettmaths.com',
                   'www.thenational.academy', 'thenational.academy',
                   'www.freesciencelessons.co.uk', 'freesciencelessons.co.uk',
                   'www.physicsandmathstutor.com', 'physicsandmathstutor.com',
                   'www.bbc.co.uk', 'bbc.co.uk', 'www.youtube.com', 'youtube.com',
                   'youtu.be', 'qualifications.pearson.com', 'www.aqa.org.uk',
                   'www.savemyexams.com', 'savemyexams.com'}


def _now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def blank_store():
    return {'version': 1, 'rules': [], 'resources': [], 'audit': []}


def _settings():
    # Secrets are only read on the server, never shown to visitors.
    try:
        import streamlit as st
        return {'repo': str(st.secrets.get('QUALITY_GITHUB_REPO','')).strip(),
                'token': str(st.secrets.get('QUALITY_GITHUB_TOKEN','')).strip(),
                'branch': str(st.secrets.get('QUALITY_GITHUB_BRANCH','main')).strip() or 'main',
                'password': str(st.secrets.get('QUALITY_ADMIN_PASSWORD',''))}
    except Exception:
        return {'repo': '', 'token': '', 'branch': 'main', 'password': ''}


def configured():
    s = _settings()
    return bool(s['repo'] and s['token'] and s['password'] and
                re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', s['repo']))


def password_valid(attempt):
    configured_password = _settings()['password']
    return bool(configured_password and hmac.compare_digest(configured_password, str(attempt)))


def _api_path():
    s = _settings()
    return f"https://api.github.com/repos/{s['repo']}/contents/{DATA_PATH}"


def _headers():
    return {'Authorization': 'Bearer ' + _settings()['token'],
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'}


def _validate_store(payload):
    if not isinstance(payload, dict):
        raise ValueError('Academic quality data is not an object')
    for key in ('rules', 'resources', 'audit'):
        if not isinstance(payload.get(key), list):
            raise ValueError('Academic quality file is missing list: ' + key)
    return payload


def load():
    """Returns (store, SHA, durable). No silent remote-to-local write fallback."""
    if not configured():
        if LOCAL_PATH.exists():
            return _validate_store(json.loads(LOCAL_PATH.read_text(encoding='utf-8'))), None, False
        return blank_store(), None, False
    resp = requests.get(_api_path(), headers=_headers(),
                        params={'ref': _settings()['branch']}, timeout=15)
    if resp.status_code == 404:
        # Can create a new file when the path does not yet exist. GitHub repo must exist.
        return blank_store(), None, True
    if not resp.ok:
        raise RuntimeError(f'GitHub quality-data read failed (HTTP {resp.status_code}). Check repository permissions and branch.')
    record = resp.json()
    decoded = base64.b64decode(record['content']).decode('utf-8')
    return _validate_store(json.loads(decoded)), record['sha'], True


def save(payload, sha, *, action):
    """Durable save only when a private GitHub repo is configured.
    GitHub uses SHA as an optimistic lock, avoiding overwrites from two admins.
    """
    if not configured():
        raise RuntimeError('Permanent saving is not yet configured. Add QUALITY_GITHUB_REPO, QUALITY_GITHUB_TOKEN, QUALITY_ADMIN_PASSWORD to Streamlit Secrets. No change has been saved.')
    _validate_store(payload)
    raw = json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')
    body = {'message': f'Academic quality review: {action[:75]}',
            'content': base64.b64encode(raw).decode('ascii'),
            'branch': _settings()['branch']}
    if sha: body['sha'] = sha
    resp = requests.put(_api_path(), headers=_headers(), json=body, timeout=20)
    if resp.status_code in (409, 422):
        raise RuntimeError('Quality data was changed by another reviewer. Reload and try again; your change was not saved.')
    if not resp.ok:
        raise RuntimeError(f'GitHub save failed (HTTP {resp.status_code}). No change was saved.')
    return resp.json()['content']['sha']


def _clean_text(value, limit):
    return str(value or '').strip()[:limit]


def approve_rule(data, *, scope, subject, topic, correction, example=''):
    if scope not in ('all', 'subject', 'topic'):
        raise ValueError('Invalid rule scope')
    correction = _clean_text(correction, 1200)
    if len(correction) < 20:
        raise ValueError('Describe a specific, testable correction (at least 20 characters).')
    if scope in ('topic', 'subject') and not _clean_text(subject, 120):
        raise ValueError('Subject is required')
    if scope == 'topic' and not _clean_text(topic, 180):
        raise ValueError('Topic is required')
    out = copy.deepcopy(data)
    identifier = 'rule-' + datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')
    rule = {'id': identifier, 'scope': scope,
            'subject': _clean_text(subject,120) if scope != 'all' else '',
            'topic': _clean_text(topic,180) if scope == 'topic' else '',
            'instruction': correction, 'example': _clean_text(example,700),
            'approved_at': _now(), 'status':'approved'}
    out['rules'].append(rule)
    out['audit'].append({'action':'approve_rule', 'id': identifier, 'date': _now()})
    return out


def active_rules(data, subject, topic, max_rules=12):
    matched = []
    for rule in data.get('rules', []):
        if rule.get('status') != 'approved': continue
        scope=rule.get('scope')
        if scope=='all' or (scope in ('subject','topic') and rule.get('subject')==subject and
                            (scope=='subject' or rule.get('topic')==topic)):
            matched.append(rule['instruction'])
    return matched[-max_rules:]


def validate_direct_url(url):
    url=_clean_text(url, 1500)
    p=urlsplit(url)
    host=(p.hostname or '').lower()
    if p.scheme!='https' or host not in ALLOWED_DOMAINS or p.username or p.password:
        raise ValueError('Use a HTTPS URL from one of the approved education providers.')
    if not p.path or p.path in ('/', '/contents/', '/subjects/', '/qualifications.html'):
        raise ValueError('A direct lesson, worksheet or video URL is required, not a homepage.')
    if p.path.rstrip('/') in ('/search', '/results') or 'search_query=' in p.query:
        raise ValueError('Search pages are not allowed. Link to the exact lesson or resource.')
    return url


def add_resource(data, *, subject, topic, title, url, provider, reviewer_note):
    url = validate_direct_url(url)
    subject, topic, title = (_clean_text(subject,120), _clean_text(topic,180), _clean_text(title,180))
    if not (subject and topic and len(title)>5):
        raise ValueError('Subject, exact topic and descriptive resource title are required.')
    if len(_clean_text(reviewer_note,500)) < 15:
        raise ValueError('Document what was checked for topic and course relevance.')
    out = copy.deepcopy(data)
    if any(r.get('url')==url and r.get('subject')==subject and r.get('topic')==topic for r in out['resources']):
        raise ValueError('This direct URL is already approved for this exact topic.')
    identifier='resource-' + datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')
    out['resources'].append({'id':identifier, 'subject':subject, 'topic':topic,
                             'title':title, 'url':url, 'provider':_clean_text(provider,100),
                             'reviewer_note':_clean_text(reviewer_note,500), 'approved_at':_now(),
                             'status':'approved'})
    out['audit'].append({'action':'approve_resource','id':identifier,'date':_now()})
    return out


def matching_resources(data, subject, topic):
    return [r for r in data.get('resources',[]) if r.get('status')=='approved'
            and r.get('subject')==subject and r.get('topic')==topic]


def archive(data, identifier):
    out=copy.deepcopy(data)
    for collection in ('rules','resources'):
        for item in out.get(collection,[]):
            if item.get('id')==identifier and item.get('status')=='approved':
                item['status']='archived'
                out['audit'].append({'action':'archive','id':identifier,'date':_now()})
                return out
    raise ValueError('Approved item not found')
