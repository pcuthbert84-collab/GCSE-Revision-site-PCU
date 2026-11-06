"""DBSJP course catalogue; codes from user-provided entry lists, topics from school maps and prior booklet index.
Entry codes are not the same as confirmed specification content."""
import json
from pathlib import Path
from courses.catalog import CATALOG as ORIGINAL
from courses.revision_content import get_content
from courses.maths_4ma1 import TOPICS

MAPS=json.loads((Path(__file__).parent/'school_maps.json').read_text())
EXTRA={
 'Further Mathematics':{'kind':'International GCSE','board':'Pearson Edexcel','code':'4PM1','themes':{'Topics':['Number','Algebra','Calculus','Geometry','Trigonometry','Series and functions']}},
 'BTEC Music':{'kind':'BTEC Level 2','board':'Pearson','code':'HVXB7','themes':{'Music practice':['Introduction to Performing','Introduction to Composing','Creating a Music Product']}},
}
CODES={'English Language':('Pearson Edexcel','4EA1'),'English Literature':('Pearson Edexcel','4ET1'),
'English as a Second Language':('Pearson Edexcel','4XES2'), 'History':('Pearson Edexcel','4HI1'),
'Geography':('Pearson Edexcel','4XGE1'),'French':('Pearson Edexcel','4FR1'), 'Spanish':('Pearson Edexcel','4SP1'),
'Business Studies':('Pearson Edexcel','4BS1'),'Computer Science':('Pearson Edexcel','1CP2'),
'Psychology':('AQA','8182'),'Music':('Pearson Edexcel','1MU0'),'Drama':('AQA','8261'),
'Design & Technology':('AQA','8552'), 'Food Preparation & Nutrition':('AQA','8585'),
'Fine Art':('AQA','8202'),'Photography':('AQA','8206'),'Graphic Communication':('AQA','8203'),
'BTEC Information Technology':('Pearson BTEC International','HBHZ2'),
'BTEC Business Studies':('Pearson BTEC International','HBGY2'),
'BTEC Sport':('Pearson BTEC International','HYP4'),
'BTEC Performing Arts':('Pearson BTEC International','HPMN9'),
'BTEC Applied Science':('Pearson BTEC International','JCPV2'),
'BTEC Music':('Pearson BTEC International','HVXB7'),
'Separate Sciences':('AQA','8461 / 8462 / 8463')}

def get_courses():
    courses={k:dict(v) for k,v in ORIGINAL.items() if k not in ('Arabic','Islamic Education')}
    courses.update({k:{'name':k,**v} for k,v in EXTRA.items()})
    for name,c in courses.items():
        if name in CODES:c['board'],c['code']=CODES[name]
        if name=='BTEC Sport':c['note']='HYP4 only; verify unit size prior to live assessment.'
        if name=='Separate Sciences':c['note']='Each separate science has its own AQA paper and specification.'
        if name=='Geography':c['note']='The 4XGE1 code identifies Pearson modular Geography. Confirm the 4WGE1 and 4WGE2 unit route and chosen topics before treating practice questions as exam-specific.'
        c['mapped']=MAPS.get(name,[])
        c['spec_verified']=name=='Mathematics' # Confirmed by user; the others require final exact unit-level audit
    return courses

COURSES=get_courses()

def topic_groups(name):
    c=COURSES[name]
    result={}
    if c['mapped']:
        for year in (10,11):
            entries=[x for x in c['mapped'] if x['year']==year]
            if entries:result[f'Year {year} · DBSJP taught curriculum']=[{'title':x['title'], 'source':x['source_text'], 'file':x['source_file'], 'year':year, 'kind':'school'} for x in entries]
    # Important: these are from the booklet topic outline and may need further spec audit.
    for group, topics in c.get('themes',{}).items():
        items=[{'title':t,'source':'', 'file':'DBSJP KS4 options booklet / course index','year':None,'kind':'booklet'} for t in topics]
        if items:result[f'{group} · Course topics']=items
    return result
