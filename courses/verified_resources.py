"""Hand-checked, directly linked free resources. No generated URLs.
Only show a seed when a topic explicitly matches its narrow topic trigger.
These are teaching resources, not claims of exam-board endorsement.
"""
from engine.quality_store import validate_direct_url

SEEDS = [
 {'subject':'Mathematics', 'needles':['solving quadratics by factoris','quadratic equations by factoris','quadratic factoris'],
  'title':'Solving quadratic equations by factorising — video', 'provider':'Corbettmaths',
  'url':'https://corbettmaths.com/2013/05/03/solving-quadratics-by-factorising/'},
 {'subject':'Mathematics', 'needles':['quadratic formula'],
  'title':'Quadratic formula — worked video', 'provider':'Corbettmaths',
  'url':'https://corbettmaths.com/2013/04/24/quadratic-formula/'},
 {'subject':'Mathematics', 'needles':['quadratic formula'],
  'title':'Quadratic formula — practice worksheet', 'provider':'Corbettmaths',
  'url':'https://corbettmaths.com/wp-content/uploads/2021/09/Quadratic-Formula.pdf'},
 {'subject':'Mathematics', 'needles':['percentage increase','percentage decrease','percentage change'],
  'title':'Increasing and decreasing by a percentage — video', 'provider':'Corbettmaths',
  'url':'https://corbettmaths.com/2012/08/21/increasing-or-decreasing-by-a-percentage/'},
 {'subject':'Mathematics', 'needles':['ratio shar','sharing in a ratio','sharing an amount'],
  'title':'Sharing the total in a ratio — video', 'provider':'Corbettmaths',
  'url':'https://corbettmaths.com/2021/03/10/ratio-videos/'},
 {'subject':'Mathematics', 'needles':['ratio shar','sharing in a ratio','sharing an amount'],
  'title':'Sharing in a ratio — practice questions', 'provider':'Corbettmaths',
  'url':'https://corbettmaths.com/wp-content/uploads/2013/02/ratio-sharing-the-total-pdf.pdf'},
 {'subject':'English Literature','needles':['unseen poetry'],
  'title':'Analysing the structure of unseen poetry — lesson', 'provider':'Oak National Academy',
  'url':'https://www.thenational.academy/teachers/lessons/structural-analysis-of-unseen-poetry'},
 {'subject':'English Literature','needles':['an inspector calls'],
  'title':'An Inspector Calls: themes — Year 10 lesson', 'provider':'Oak National Academy',
  'url':'https://www.thenational.academy/teachers/programmes/english-secondary-ks4-edexcel/units/modern-text-first-study-4896/lessons/an-inspector-calls-understanding-and-exploring-key-themes'},
 {'subject':'Combined Science', 'needles':['diffusion','osmosis','active transport'],
  'title':'Diffusion, osmosis and active transport — AQA lesson', 'provider':'Oak National Academy',
  'url':'https://www.thenational.academy/teachers/lessons/moving-into-and-out-of-the-blood-diffusion-osmosis-and-active-transport'},
 {'subject':'Separate Sciences', 'needles':['diffusion','osmosis','active transport'],
  'title':'Diffusion, osmosis and active transport — lesson', 'provider':'Oak National Academy',
  'url':'https://www.thenational.academy/teachers/lessons/moving-into-and-out-of-the-blood-diffusion-osmosis-and-active-transport'},
]

def seeded_resources(subject, topic):
    text=' '.join(str(topic).lower().split())
    items=[]
    for entry in SEEDS:
        if entry['subject'] == subject and any(needle in text for needle in entry['needles']):
            items.append({**{k:v for k,v in entry.items() if k!='needles'},
                          'topic':topic, 'status':'approved', 'source':'hand-checked seed'})
    return items


def topic_resources(store, subject, topic):
    from engine.quality_store import matching_resources
    found = seeded_resources(subject,topic) + matching_resources(store,subject,topic)
    dedup={}
    for item in found:
        try:
            validate_direct_url(item['url'])
        except ValueError: continue
        dedup[item['url']]=item
    return list(dedup.values())
