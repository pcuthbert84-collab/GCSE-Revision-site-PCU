"""Verified external source atlas for the DBSJP Revision Hub.

Links are deliberately separated:
1. Official qualification pages, scoped by subject/code, not by inferred topic.
2. Provider topic catalogues, useful for student navigation, NOT exact links.
3. A few independently verified topic-specific lessons/indices.

No scraping of subscription-only content or passing third-party pages to Gemini.
Never infer that a UK GCSE provider is identical to an IGCSE specification.
"""
import re

PEARSON_IG="https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses.a-z.html"
PEARSON_BTEC="https://qualifications.pearson.com/en/qualifications/btec-international-level-2.html"
AQA_ROOT="https://www.aqa.org.uk/qualifications"
IG="https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses/"
GCSE="https://qualifications.pearson.com/en/qualifications/edexcel-gcses/"
BTEC="https://qualifications.pearson.com/en/qualifications/btec-international-level-2/"

# Checked against published awarder qualification pages, November 2026.
# Display only as qualification-level context, never as a verified subtopic URL.
OFFICIAL = {
 "Mathematics":("4MA1",IG+"international-gcse-mathematics-a-2016.html"),
 "Further Mathematics":("4PM1",IG+"international-gcse-further-pure-mathematics-2017.html"),
 "English Language":("4EA1",IG+"international-gcse-english-language-a-2016.html"),
 "English Literature":("4ET1",IG+"international-gcse-english-literature-2016.html"),
 "English as a Second Language":("4XES2",IG+"english-as-a-second-language-2023.html"),
 "History":("4HI1",IG+"international-gcse-history-2017.html"),
 "Geography":("4XGE1",IG+"geography-2023-modular.html"),
 "Business Studies":("4BS1",IG+"business-2017.html"),
 "French":("4FR1",IG+"international-gcse-french-2017.html"),
 "Spanish":("4SP1",IG+"international-gcse-spanish-2017.html"),
 "Computer Science":("1CP2",GCSE+"computer-science-2020.html"),
 "Physical Education":("1PE0",GCSE+"physical-education-2016.html"),
 "Music":("1MU0",GCSE+"music-2016.html"),
 "Psychology":("8182","https://www.aqa.org.uk/subjects/psychology/gcse/psychology-8182/specification"),
 "Drama":("8261","https://www.aqa.org.uk/subjects/drama/gcse/drama-8261/specification"),
 "Design & Technology":("8552","https://www.aqa.org.uk/subjects/design-and-technology/gcse/design-and-technology-8552/specification"),
 "Food Preparation & Nutrition":("8585","https://www.aqa.org.uk/subjects/food-preparation-and-nutrition/gcse/food-preparation-and-nutrition-8585/specification"),
 "Fine Art":("8202","https://www.aqa.org.uk/subjects/art-and-design/gcse/art-and-design-8202/specification"),
 "Photography":("8206","https://www.aqa.org.uk/subjects/art-and-design/gcse/art-and-design-8206/specification"),
 "Graphic Communication":("8203","https://www.aqa.org.uk/subjects/art-and-design/gcse/art-and-design-8203/specification"),
 "Combined Science":("8464","https://www.aqa.org.uk/subjects/science/gcse/science-8464/specification"),
 "BTEC Information Technology":("HBHZ2",BTEC+"information-technology-2022.html"),
 "BTEC Business Studies":("HBGY2",BTEC+"business-2022.html"),
 "BTEC Sport":("HYP4",BTEC+"sport-2022.html"),
 "BTEC Performing Arts":("HPMN9",BTEC+"performing-arts-2022.html"),
 "BTEC Applied Science":("JCPV2",BTEC+"applied-science.html"),
 "BTEC Music":("HVXB7",BTEC+"music-2022.html"),
}

# Verified directories. They are NOT exact-topic links and must be labelled.
# Some resources offer only free access tiers and some material is paid.
DIRECTORIES = {
 "Mathematics":[("Maths Genie · videos, practice and solutions","https://www.mathsgenie.co.uk/gcse.html","GCSE practice, cross-check IGCSE coverage")],
 "Further Mathematics":[("Maths Genie · higher algebra skills","https://mathsgenie.co.uk/features/videos","General mathematics skills, not 4PM1 mapped")],
 "English Language":[("Revision World · English Language","https://revisionworld.com/gcse-revision","General GCSE revision, verify route")],
 "English Literature":[("Oak National Academy · GCSE English Literature lesson sequences","https://www.thenational.academy/teachers/programmes/english-secondary-aqa/units?keystages=ks4&subject_categories=literature","Free teaching sequences for selected texts, AQA not International GCSE 4ET1"),
   ("Revision World · Literature","https://revisionworld.com/gcse-revision","General GCSE revision, not a verified set text")],
 "English as a Second Language":[("Pearson · ESL learning materials","https://www.pearson.com/international-schools/british-curriculum/secondary-curriculum/International-GCSE/english-as-a-second-language.html","May require book or paid access")],
 "History":[("Seneca · Free Pearson Edexcel IGCSE History learning courses","https://senecalearning.com/en-gb/blog/free-edexcel-history-igcse-revision/","Free self-check revision for several 4HI1 options; some site features need an account"),
   ("Revision World · History","https://revisionworld.com/gcse-revision","UK GCSE overviews, verify Pearson IGCSE options")],
 "Geography":[("Oak National Academy · GCSE Geography lessons","https://www.thenational.academy/teachers/programmes/geography-secondary-aqa/units?keystages=ks4","Sequenced UK GCSE geography lessons and quizzes, cross-check 4XGE1 modular specification"),
   ("Revision World · Geography","https://revisionworld.com/gcse-revision","General GCSE revision, verify fieldwork and IGCSE content")],
 "Business Studies":[("GCSE-ready · Pearson Edexcel International GCSE Business 4BS1 lessons","https://gcse-ready.org/learn/business/igcse/","Free topic-by-topic 4BS1 lessons with worked examples and quizzes; check provider accuracy independently"),
   ("Revision World · Business","https://revisionworld.com/gcse-revision","General GCSE revision, not automatically 4BS1 matched")],
 "French":[("Revision World · French","https://revisionworld.com/gcse-revision","GCSE language skills, verify IGCSE topics")],
 "Spanish":[("Revision World · Spanish","https://revisionworld.com/gcse-revision","GCSE language skills, verify IGCSE topics")],
 "Computer Science":[("Teach io · Edexcel 1CP2 resource directory","https://teachio.co.uk/teacher-resources/","Free and paid resources, filter by 1CP2")],
 "Psychology":[("Revision World · Psychology","https://revisionworld.com/gcse-revision","General GCSE revision, verify AQA 8182")],
 "Music":[("Pearson · Music exemplars with commentary","https://qualifications.pearson.com/en/qualifications/edexcel-gcses/music-2016/exemplar-library.html","Original board performance, composition and appraisal exemplars")],
 "Drama":[("Revision World · Drama","https://revisionworld.com/gcse-revision","General GCSE revision; practical components not auto-marked")],
 "Design & Technology":[("Revision World · D&T","https://revisionworld.com/gcse-revision","General GCSE theory; NEA needs teacher oversight")],
 "Food Preparation & Nutrition":[("Revision World · Food and Nutrition","https://revisionworld.com/gcse-revision","Theory and practical technique; safety remains paramount")],
 "Physical Education":[("Revision World · PE","https://revisionworld.com/gcse-revision","General GCSE revision")],
 "Combined Science":[
   ("PMT · AQA Biology notes and topic questions","https://www.physicsandmathstutor.com/biology-revision/gcse-aqa/","AQA GCSE biology index; check Trilogy versus Separate content"),
   ("PMT · AQA Chemistry notes and topic questions","https://www.physicsandmathstutor.com/chemistry-revision/gcse-aqa/","AQA GCSE chemistry index; check Trilogy versus Separate content"),
   ("PMT · AQA Physics notes and topic questions","https://www.physicsandmathstutor.com/physics-revision/gcse-aqa/","AQA GCSE physics index; check Trilogy versus Separate content"),
   ("Cognito · GCSE science videos and quizzes","https://go.cognitoedu.org/gcse","Choose AQA and course/tier; some features require login"),
 ],
 "Separate Sciences":[
   ("PMT · AQA Biology","https://www.physicsandmathstutor.com/biology-revision/gcse-aqa/","AQA Biology, check 8461"),
   ("PMT · AQA Chemistry","https://www.physicsandmathstutor.com/chemistry-revision/gcse-aqa/","AQA Chemistry, check 8462"),
   ("PMT · AQA Physics","https://www.physicsandmathstutor.com/physics-revision/gcse-aqa/","AQA Physics, check 8463"),
 ],
 "BTEC Information Technology":[("Pearson · BTEC IT student-book units","https://qualifications.pearson.com/en/qualifications/btec-international-level-2/student-book-information-technology.html","Unit listing and optional paid student book"),
   ("MDN · Web development learning pathway","https://developer.mozilla.org/en-US/docs/Learn_web_development","Free HTML, CSS and web development skills with practice tasks; not a Pearson assessed unit")],
}
# Subject-specific verified official sections: only when a recognisable
# topic token is present in the title/teaching-map snippet. These are
# curriculum references and should NOT be called a validated micro-spec match.
TOPIC_REFERENCES = [
 ("Food Preparation & Nutrition",("food science","heat transfer","cooking methods"),
  "AQA 8585 · Food science",
  "https://www.aqa.org.uk/subjects/food-preparation-and-nutrition/gcse/food-preparation-and-nutrition-8585/specification/subject-content/food-science"),
 ("Food Preparation & Nutrition",("food safety","food poisoning","bacterial contamination"),
  "AQA 8585 · Food safety",
  "https://www.aqa.org.uk/subjects/food-preparation-and-nutrition/gcse/food-preparation-and-nutrition-8585/specification/subject-content/food-safety"),
 ("Food Preparation & Nutrition",("nutrition","macronutrients","diet and health"),
  "AQA 8585 · Food, nutrition and health",
  "https://www.aqa.org.uk/subjects/food-preparation-and-nutrition/gcse/food-preparation-and-nutrition-8585/specification/subject-content/food-nutrition-and-health"),
 ("Design & Technology",("designing and making","prototype","investigating user needs"),
  "AQA 8552 · Designing and making principles",
  "https://www.aqa.org.uk/subjects/design-and-technology/gcse/design-and-technology-8552/specification/subject-content/designing-and-making-principles"),
 ("Drama",("understanding drama","dramatic techniques","analysing performances"),
  "AQA 8261 · Understanding drama",
  "https://www.aqa.org.uk/subjects/drama/gcse/drama-8261/specification/subject-content/understanding-drama"),
 ("BTEC Information Technology",("website development","html","web development"),
  "MDN · Website development: core tutorials and practice",
  "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core"),
 ("Computer Science",("programming in python","python programming","algorithms"),
  "Oak National Academy · GCSE computing lessons and practical projects",
  "https://www.thenational.academy/teachers/programmes/computing-secondary-aqa/units?threads=programming"),
 ("Psychology",("memory","perception","development","research methods","social influence"),
  "AQA 8182 · Subject and paper overview",
  "https://www.aqa.org.uk/subjects/psychology/gcse/psychology-8182/specification/specification-at-a-glance"),
 ("Combined Science",("cell biology","organisation","ecology","bioenergetics","inheritance"),
  "PMT · AQA Biology topic index",
  "https://www.physicsandmathstutor.com/biology-revision/gcse-aqa/"),
 ("Combined Science",("atomic structure","bonding","quantitative chemistry","organic chemistry","rate of reaction"),
  "PMT · AQA Chemistry topic index",
  "https://www.physicsandmathstutor.com/chemistry-revision/gcse-aqa/"),
 ("Combined Science",("electricity","forces","waves","particle model","magnetism","energy"),
  "PMT · AQA Physics topic index",
  "https://www.physicsandmathstutor.com/physics-revision/gcse-aqa/"),
]

# Verified individual AQA GCSE science topic pages, traced from PMT's
# published board-specific index, November 2026. Each page includes notes and
# topic exercises; some exercises are separate-only and must be checked.
PMT_TOPIC_PAGES = [
 ("Biology","Cell biology","https://www.physicsandmathstutor.com/biology-revision/gcse-aqa/cell-biology/"),
 ("Biology","Organisation","https://www.physicsandmathstutor.com/biology-revision/gcse-aqa/organisation/"),
 ("Biology","Infection and response","https://www.physicsandmathstutor.com/biology-revision/gcse-aqa/infection-and-response/"),
 ("Biology","Bioenergetics","https://www.physicsandmathstutor.com/biology-revision/gcse-aqa/bioenergetics/"),
 ("Biology","Homeostasis and response","https://www.physicsandmathstutor.com/biology-revision/gcse-aqa/homeostasis-and-response/"),
 ("Biology","Inheritance, variation and evolution","https://www.physicsandmathstutor.com/biology-revision/gcse-aqa/inheritance-variation-evolution/"),
 ("Biology","Ecology","https://www.physicsandmathstutor.com/biology-revision/gcse-aqa/ecology/"),
 ("Chemistry","Atomic structure and the periodic table","https://www.physicsandmathstutor.com/chemistry-revision/gcse-aqa/atomic-structure-and-periodic-table"),
 ("Chemistry","Bonding, structure and properties of matter","https://www.physicsandmathstutor.com/chemistry-revision/gcse-aqa/bonding-structure-properties-of-matter/"),
 ("Chemistry","Quantitative chemistry","https://www.physicsandmathstutor.com/chemistry-revision/gcse-aqa/quantitative-chemistry/"),
 ("Chemistry","Chemical changes","https://www.physicsandmathstutor.com/chemistry-revision/gcse-aqa/chemical-changes/"),
 ("Chemistry","Energy changes","https://www.physicsandmathstutor.com/chemistry-revision/gcse-aqa/energy-changes/"),
 ("Chemistry","The rate and extent of chemical change","https://www.physicsandmathstutor.com/chemistry-revision/gcse-aqa/rate-and-extent-of-chemical-change/"),
 ("Chemistry","Organic chemistry","https://www.physicsandmathstutor.com/chemistry-revision/gcse-aqa/organic-chemistry/"),
 ("Chemistry","Chemical analysis","https://www.physicsandmathstutor.com/chemistry-revision/gcse-aqa/chemical-analysis/"),
 ("Chemistry","Chemistry of the atmosphere","https://www.physicsandmathstutor.com/chemistry-revision/gcse-aqa/chemistry-of-atmosphere/"),
 ("Chemistry","Using resources","https://www.physicsandmathstutor.com/chemistry-revision/gcse-aqa/using-resources/"),
 ("Physics","Energy","https://www.physicsandmathstutor.com/physics-revision/gcse-aqa/energy/"),
 ("Physics","Electricity","https://www.physicsandmathstutor.com/physics-revision/gcse-aqa/electricity/"),
 ("Physics","Particle model of matter","https://www.physicsandmathstutor.com/physics-revision/gcse-aqa/particle-model-of-matter/"),
 ("Physics","Atomic structure","https://www.physicsandmathstutor.com/physics-revision/gcse-aqa/atomic-structure/"),
 ("Physics","Forces","https://www.physicsandmathstutor.com/physics-revision/gcse-aqa/forces/"),
 ("Physics","Waves","https://www.physicsandmathstutor.com/physics-revision/gcse-aqa/waves/"),
 ("Physics","Magnetism and electromagnetism","https://www.physicsandmathstutor.com/physics-revision/gcse-aqa/magnetism-and-electromagnetism/"),
 ("Physics","Space physics","https://www.physicsandmathstutor.com/physics-revision/gcse-aqa/space-physics/"),
]

def pmt_topic_resources(subject, topic, area=""):
    if subject not in ("Combined Science","Separate Sciences"):
        return []
    key=re.sub(r"[^a-z0-9]+"," ",str(topic).casefold()).strip()
    aliases={"bonding structure and the properties of matter":"bonding structure and properties of matter",
             "bonding":"bonding structure and properties of matter",
             "magnetism":"magnetism and electromagnetism",
             "particle model":"particle model of matter",
             "atomic structure and periodic table":"atomic structure and the periodic table",
             "the rate and extent of chemical changes":"the rate and extent of chemical change"}
    key=aliases.get(key,key)
    # 'Atomic structure' is both a Chemistry and Physics concept. Without a
    # discipline selected, a source page from just one science is misleading.
    if key=="atomic structure" and not any(
            x in str(area).casefold() for x in ("biology","chemistry","physics")):
        return []
    candidates=[]
    for science,title,url in PMT_TOPIC_PAGES:
        standard=re.sub(r"[^a-z0-9]+"," ",title.casefold()).strip()
        if standard!=key:
            continue
        # If this is a science subject section, check its discipline. If the
        # title is ambiguous and no science section exists, do not guess.
        area_key=str(area).casefold()
        known=[x for x in ("biology","chemistry","physics") if x in area_key]
        if known and science.casefold() not in known:
            continue
        candidates.append((science,title,url))
    if len(candidates)!=1:
        return []
    science,title,url=candidates[0]
    if subject=="Combined Science" and science=="Physics" and title=="Space physics":
        return [] # AQA Trilogy excludes the Separate-only space physics topic.
    return [{"title":"PMT · "+science+" · "+title+" · notes, flashcards, topic questions",
             "url":url,"provider":"Physics & Maths Tutor","kind":"direct_topic",
             "note":"Verified AQA GCSE topic page. Check Foundation/Higher and Separate-only labels; not a copied course resource."}]

def _normal(v):
    return re.sub(r"\s+"," ",str(v or "").casefold()).strip()

SEPARATE_SCIENCE_SPECS = [
    {"title":"AQA Biology · 8461 official specification",
     "url":"https://www.aqa.org.uk/subjects/biology/gcse/biology-8461/specification"},
    {"title":"AQA Chemistry · 8462 official specification",
     "url":"https://www.aqa.org.uk/subjects/chemistry/gcse/chemistry-8462/specification"},
    {"title":"AQA Physics · 8463 official specification",
     "url":"https://www.aqa.org.uk/subjects/physics/gcse/physics-8463/specification"},
]

def qualification_reference(course):
    """Exact code match only, except the separately identified three AQA sciences."""
    name=course.get("name","")
    if name=="Separate Sciences":
        return None  # Separate qualifications: 8461, 8462 and 8463, not one spec.
    result=OFFICIAL.get(name)
    if not result:
        return None
    code,url=result
    if code != str(course.get("code","")).strip():
        return None
    return {"title":"Official qualification and specification · "+code,
            "url":url,"provider":"Exam board","kind":"official",
            "note":"Official specification overview. Confirm taught options and assessment route."}

def directory_resources(subject):
    return [
        {"title":title,"url":url,"provider":title.split(" · ")[0],
         "kind":"directory","note":note}
        for title,url,note in DIRECTORIES.get(subject,[])]

def topic_references(subject,topic,source="",area=""):
    """Narrow keyword matches only; title labelled *index*, not exact lesson."""
    text=_normal(topic)
    # A school topic's source may be an entire term: avoid matching every
    # incidental mention. Only topic title may trigger student links.
    results=[]; seen=set()
    chosen_science=next((x for x in ("biology","chemistry","physics")
                         if x in str(area).casefold()),"")
    for name,needles,title,url in TOPIC_REFERENCES:
        if name!=subject or not any(n in text for n in needles) or url in seen:
            continue
        # Broad science index links are not substitutes for exact lesson pages.
        # A Chemistry lesson called "Energy changes" must NEVER receive
        # the Physics Energy catalogue simply because they share a word.
        if subject in ("Combined Science","Separate Sciences") and "PMT" in title:
            target=next((x for x in ("biology","chemistry","physics")
                         if x in title.casefold()),"")
            if not chosen_science or chosen_science!=target:
                continue
        seen.add(url)
        results.append({"title":title,"url":url,"provider":title.split(" · ")[0],
            "kind":"topic_reference",
            "note":"Relevant specification section or topic index, not a checked one-to-one lesson mapping."})
    direct=pmt_topic_resources(subject,topic,area)
    return direct+[row for row in results if row["url"] not in {d["url"] for d in direct}]

def metadata_for_ai(course,topic):
    """Small safe source metadata, NOT webpage text or unverified learning facts."""
    entry=qualification_reference(course)
    if not entry:
        return ""
    return ("Official course reference only (not fetched by model): "
        +entry["title"]+"; "+entry["url"]
        +". Source status: code recorded in DBSJP course catalogue and subject-level awarding-body page identified; precise DBSJP "
        "taught subtopic, unit option and examination component not yet audited. "
        "Do not claim to have read the external website or cite its text.")
