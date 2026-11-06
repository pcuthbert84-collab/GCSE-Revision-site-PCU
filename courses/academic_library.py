"""V4.11 curated teaching patterns, derived from DBSJP English and History uploads.

This is an editorial *pedagogy* library, not a store of approved quotations,
historical fact claims, copied exemplars or official exam-board mark schemes.
No third-party PDF/PowerPoint text is reproduced. Topic labels are matched
conservatively; unrelated courses never receive these patterns.
"""
import re

LIBRARY = (
    {
        "id": "eng_literature_shakespeare",
        "subject": "English Literature",
        "terms": ("romeo and juliet", "romeo", "juliet", "capulet", "mercutio", "friar", "tybalt"),
        "approach": "Begin with accurate scene/character knowledge. Model an arguable interpretation, select a verified short textual reference, analyse Shakespeare's language or dramatic construction, then explain how an interpretation develops across the play. Contrast a defensible alternative reading where helpful.",
        "assessment": "Assess relevance to the precise question, accuracy of event/textual reference, explanation of writer's methods, development of argument and supported alternative readings. Do not insist on one character judgement.",
        "checks": "Verify the wording and act/scene of every quotation against the play before presenting it as a quotation. Treat third-party character profiles as interpretation examples, NOT ground truth. Do not invent the prescribed assessment objectives or assessed component.",
        "sources": ("DBSJP Romeo and Juliet teaching/coursework resources", "PMT Romeo and Juliet character, theme and overview resources (external, unverified claims filtered)"),
    },
    {
        "id": "eng_literature_poetry",
        "subject": "English Literature",
        "terms": ("poetry", "poem", "war photographer", "the tyger", "remember", "unseen"),
        "approach": "Progress from literal meaning and speaker to an interpretation grounded in precise language, form and structural choices. Model how an observation develops into an explained interpretation, and allow more than one supportable reading.",
        "assessment": "Reward supported interpretations and analysis of effects, not a device-name checklist. Where comparison is required, make connections between poems within the argument.",
        "checks": "Do not fabricate lines or attribute original practice lines to an anthology poem. Never assert which anthology poems are prescribed unless the selected curriculum evidence confirms it.",
        "sources": ("DBSJP poetry lessons and knowledge organiser",),
    },
    {
        "id": "eng_literature_prose",
        "subject": "English Literature",
        "terms": ("of mice and men", "crooks", "steinbeck", "loneliness"),
        "approach": "Use a progression of retrieval, inference, well-selected textual evidence, close analysis, and a link back to the wider interpretation. Model how to move beyond description and improve a paragraph without handing over a memorised essay.",
        "assessment": "Value a precise argument, accurate reference, explained language choices and development beyond summary. Support alternatives where evidenced.",
        "checks": "Verify character events and quotations before including them as facts. Do not reproduce classroom model essays verbatim.",
        "sources": ("DBSJP Of Mice and Men department lessons",),
    },
    {
        "id": "hist_medicine",
        "subject": "History",
        "terms": ("medicine", "surgery", "chloroform", "public health", "penicillin", "anaesthetic", "antiseptic", "aseptic"),
        "approach": "Build chronology and precise contextual vocabulary first. Compare pain, infection and blood loss across periods, then practise why change occurred, what limits persisted and which development was most significant. Model a causal chain rather than a list of names or dates.",
        "assessment": "For two-difference tasks, explain two distinct accurate comparisons with evidence. For evaluation tasks, balance factors and defend a judgement supported by precise examples. Only use the correct mark total and structure when supported by the selected paper specification.",
        "checks": "Do not import approximate surgical mortality statistics or dates from handouts without corroboration. Known correction: Queen Victoria's chloroform childbirth example relates to 1853, not 1852. Distinguish historical background from an examined requirement.",
        "sources": ("DBSJP surgery guided readings, 1848-1948", "Medicine revision slides and department model answers"),
    },
    {
        "id": "hist_us_civil",
        "subject": "History",
        "terms": ("civil rights", "civil protest", "vietnam", "women's movement", "womens movement", "student protest", "watergate", "divided union"),
        "approach": "Start with a dated, sourced sequence of developments and distinct causes, aims, methods and consequences. Use original source-analysis tasks to practise what the source states, what can be inferred, what supports the inference, and what contextual knowledge adds. Evaluate relative significance with a clear judgement.",
        "assessment": "Reward precise historical knowledge, justified interpretation, relevant evidence, explanation of causation/consequences and consideration of limitations or alternative views. Treat 16-mark classroom exemplars as structure demonstrations, not official marks.",
        "checks": "Correct the Watergate handout: Nixon resigned in August 1974 and was not impeached by the Senate. The 1973 War Powers Resolution was principally a Vietnam-era restriction, not a direct consequence of Watergate. Do not invent historical extracts.",
        "sources": ("DBSJP Vietnam, women's movement, student protest and Watergate lessons and exemplars",),
    },
    {
        "id": "hist_usa_1920",
        "subject": "History",
        "terms": ("usa 1918", "usa 1920", "america 1920", "1920s", "new deal", "prohibition", "roaring twenties", "economic boom", "great depression"),
        "approach": "Establish chronology, causes and consequences, then contrast who benefited and who did not. For an extract and sources, explicitly separate the extract's interpretation, each source's claims and the student's contextual knowledge. Model signposting and a sustained balanced judgement.",
        "assessment": "Assess source selection, accurate contextual support, explanation of agreement/disagreement and a logically justified overall judgement. Do not equate long answers with high-level responses.",
        "checks": "Source-dependent questions require the source text supplied within the prompt. Never fabricate quotations or assert a classroom worksheet is an official exam question.",
        "sources": ("DBSJP USA Paper 2 revision lessons", "Prohibition essay masterclass and USA model answers"),
    },
    {
        "id": "hist_germany",
        "subject": "History",
        "terms": ("germany", "weimar", "nazi", "versailles", "spartacist", "kapp putsch", "stresemann"),
        "approach": "Model chronological contextualisation, an inference supported by a specific supplied source detail, comparison of differing historical interpretations and explanation of how evidence supports each conclusion. Extend through causal and significance questions.",
        "assessment": "Award credit for explicit inference with evidence and explained comparison, not only identifying names, events or opinions.",
        "checks": "Distinguish contemporary primary sources from later historians' interpretations; do not generate invented primary sources labelled genuine.",
        "sources": ("DBSJP Treaty of Versailles and Germany TIF challenge activities",),
    },
)

def _normalise(value):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', (value or '').lower())).strip()

def matched_patterns(subject, topic, area='', limit=2):
    """Only high-confidence lexical topic matches within the *correct* subject.

    School maps often contain a broad year/block heading. Do not use the full
    document body for matching or it can spuriously attach unrelated units.
    """
    if subject not in ('English Literature', 'History'):
        return []
    label = _normalise(' '.join((topic or '', area or '')))
    scored = []
    for entry in LIBRARY:
        if entry['subject'] != subject:
            continue
        hits = [term for term in entry['terms'] if _normalise(term) in label]
        if hits:
            scored.append((max(map(len, hits)), entry))
    return [item for _, item in sorted(scored, key=lambda pair: -pair[0])[:limit]]

def academic_context(subject, topic, area=''):
    matches = matched_patterns(subject, topic, area)
    if not matches:
        return None
    return {
        'status': 'editorial teaching guidance; NOT a verified official specification or examiner mark scheme',
        'patterns': [
            {k: record[k] for k in ('id', 'approach', 'assessment', 'checks', 'sources')}
            for record in matches
        ],
        'boundaries': (
            'Apply teaching/assessment approaches only where the selected question requires them. '
            'This library does not certify quotations, dates, mark-scheme levels or unit coverage. '
            'The current school topic and genuine assessment component take priority.'
        )
    }
