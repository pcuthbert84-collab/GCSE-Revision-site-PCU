"""Curated ORIGINAL teaching guidance from DBSJP departmental resource review.

Not a transcript of uploads, not an examination-board mark scheme and not an
automatic endorsement of third-party explanations. Select by explicit evidence
of topic and subject only. Historical assertions and quotations are deliberately
not imported without independent approval.
"""
import re

ENGLISH_TEACHING = (
    "DBSJP lesson progression: recall prior knowledge; clarify character/plot "
    "or poem meaning; choose a defensible interpretive claim; select precise "
    "textual evidence; analyse a writer's word, form or structural choice; "
    "develop effects and relevant contextual implications; revisit and refine "
    "the argument. Use PETAL as OPTIONAL temporary scaffolding, never as a "
    "mandatory mark-scheme requirement. Model the movement from simple "
    "observation to specific, developed interpretation. Show alternatives "
    "where supported, and reward sustained analysis rather than named devices "
    "or sophisticated vocabulary alone. For unseen poetry, supply an ORIGINAL "
    "short extract; for set texts, do not invent quotations or scene locations. "
    "Do not reproduce extended uploaded model answers."
)
HISTORY_TEACHING = (
    "DBSJP lesson progression: accurate factual retrieval; chronological "
    "placement; selection of specific evidence; explain HOW and WHY a cause "
    "led to an event or consequence; compare evidence and interpretations; "
    "make and justify an evaluative judgement. Do not confuse description "
    "with explanation. For source questions teach the distinction between "
    "what a source says, what can be inferred, its provenance, and relevant "
    "contextual knowledge. Keep 6-mark comparison, 8-mark two-effects and "
    "16-mark evaluation tasks distinct and only use the format when supported "
    "by the current course component. An exam-style source stimulus must be "
    "clearly marked ORIGINAL or use a properly permissioned genuine source. "
    "A 16-mark answer should weigh competing factors and justify a judgement; "
    "do not grant full credit for fact-dumping or writing a conclusion alone."
)
ENGLISH_TOPICS = {
    "romeo and juliet": (
        "Approved pedagogical focus: changes in character relationships and "
        "agency, gender roles, family conflict, dramatic juxtaposition, "
        "the contrast between love and violence, and alternative readings "
        "of authority and responsibility. Ground every claimed quotation "
        "and act/scene reference in an independently checked play text."
    ),
    "of mice and men": (
        "Approved pedagogical focus: move from knowledge of a scene or "
        "character to short textual evidence, analysis of language and "
        "structure, then connections to marginalisation, loneliness, "
        "power and historical setting. Students may justify competing "
        "readings; an illustrative teacher interpretation is not a fact."
    ),
    "poetry": (
        "Approved pedagogical focus: identify the speaker and initial "
        "meaning, analyse precise vocabulary and structure, consider "
        "shifts in tone and alternative interpretations, then form "
        "supported comparisons. Vocabulary is taught for precise meaning, "
        "not credited merely because advanced terms are used."
    ),
}
HISTORY_TOPICS = {
    "medicine": (
        "Scope: Changes in Medicine 1848-1948. Teach change and "
        "continuity in pain control, infection, blood loss, public "
        "health, wartime treatment, and scientific understanding. "
        "Distinguish chronology and qualified impact; verify all "
        "dates, people and quantified claims before teaching them. "
        "Do NOT repeat the source error dating Queen Victoria's "
        "chloroform childbirth to 1852."
    ),
    "usa 1918": (
        "Scope: USA 1918-1941. Consider beneficiaries and exclusions "
        "from economic and social change, causes and effects of "
        "Prohibition, Depression and the New Deal. Evaluation needs "
        "specific evidence rather than a list of named programmes."
    ),
    "civil rights": (
        "Scope: A Divided Union, USA 1945-1974. Differentiate "
        "campaign causes, forms of protest, consequences and "
        "perspectives; identify dates and provenance precisely. "
        "Check broad generalisations and avoid presenting later "
        "events as automatic consequences of Watergate."
    ),
    "watergate": (
        "Scope: Watergate, 1972-1974. Nixon resigned rather than "
        "being impeached by a full House vote. Do not describe "
        "the 1973 War Powers Resolution as a direct legislative "
        "result of Watergate. Verify all precise claims separately."
    ),
}
def _normal(text):
    return re.sub(r"\s+", " ", (text or "").lower()).strip()

def teaching_context(course, topic, area=""):
    """Return relevant guidance only; no whole-school data or unverified quote bank."""
    name=_normal(course.get("name",""))
    subject="english" if name.startswith("english") else "history" if name=="history" else ""
    if not subject:
        return ""
    title=_normal(topic.get("title",""))
    area=_normal(area)
    school=_normal(topic.get("source",""))[:1600]
    combined=" ".join((title,area,school))
    if subject=="english":
        base=ENGLISH_TEACHING
        relevant=[]
        for term,text in ENGLISH_TOPICS.items():
            if term in combined or (term=="poetry" and any(
                k in combined for k in ("poem","sonnet","anthology","verse","tyger","war photographer","remember"))):
                relevant.append(text)
        # No named set-text context for broad English headings: pedagogical guidance only.
    else:
        base=HISTORY_TEACHING
        relevant=[]
        for term,text in HISTORY_TOPICS.items():
            if term in combined or (term=="usa 1918" and ("1918" in combined and "1941" in combined)):
                relevant.append(text)
    return (
        "TEACHER-REVIEWED PEDAGOGICAL GUIDANCE (not a verified examiner rubric): "
        +base+" "+" ".join(relevant[:2])
        +" Authority order: official specification and approved academic corrections "
        "take priority; school material informs teaching method only. "
        "Do not fabricate historical facts or quotations from this guidance."
    )[:3200]
