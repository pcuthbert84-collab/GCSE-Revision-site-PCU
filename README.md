# DBSJP Revision Hub — Multi-subject prototype V2

A free-to-run Streamlit revision prototype based on the **DBSJP Key Stage 4 Options Booklet 2026–27**.

## What's included

- 28 DBSJP GCSE, IGCSE, BTEC and school-curriculum pathways, with 250+ selectable *booklet-level* themes.
- Subject → area → topic → **Revise** or **Test myself**.
- Mathematics: confirmed Pearson Edexcel International GCSE Mathematics A **4MA1 Higher Tier**, including four working parameterised maths skills with exact-answer SymPy marking, hints, optional second attempt and worked solution.
- Other subjects: original, free, **self-assessed** retrieval practice prompts for every listed theme. No false claims of automatic grades without an AI key.
- Optional Gemini API integration to write **original** questions and provide **indicative** feedback. No paid account is necessary to run offline practice.
- Adaptive difficulty suggestions, topic-level progress, second-attempt/skipped tracking, JSON export/import.
- Official exam-board past-paper *links*, not scraped or reproduced paper contents.
- Simple course catalogue and clear verification warnings.

**IMPORTANT:** This is a substantial **framework with broad coverage**, not a claim that all 28 awarding-body specifications, thousands of exact syllabus points, videos and exam-style marking rubrics are already authenticated. Most non-Mathematics topics come from the school booklet or a provisional teaching overview. Course codes and topic-level links must be verified before claiming exact exam-board alignment. In particular, BTEC options may depend on the school's chosen units. See `courses/catalog.py`.

## Deploy to existing Streamlit app

1. Download and extract the zip.
2. Upload/replace the **contents of `dbsjp_revision_hub/`** in your existing GitHub repository. Keep `app.py` **at the repository root** alongside `requirements.txt`, `courses/` and `engine/`.
3. In Streamlit Community Cloud set main file `app.py`. Commit changes; Streamlit automatically redeploys.
4. No API key is required for Mathematics testing or self-assessed offline questions in the other subjects.

### Optional Gemini (free tier, subject to eligibility and quotas)

In Streamlit **App settings → Secrets**, set:

```toml
GEMINI_API_KEY = "your-key-here"
GEMINI_MODEL = "gemini-2.5-flash-lite"
```

The selected model must be supported by your own free API allocation. If that model becomes unavailable, change the model setting. **No automatic paid API fallback is implemented**. No identifying user data are passed by the app in AI prompts, but student answers *are* sent for marking when enabled. Verify the AI provider's data practices, school rules, and child privacy/safeguarding requirements **before real student use**. Free API eligibility and quotas are not guaranteed.

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Run tests:

```bash
python -m pytest -q
```

## Very important limitations

- **No real student registration, parental login, private database or multi-user isolation yet.** The site is for demonstration and testing with non-identifying dummy answers only. Current progress lives in Streamlit session state and is lost when the session ends unless exported. Do not use with personal or sensitive student information.
- AI responses are fallible; the current generation engine performs structural checks, **not** independent examiner-level content verification. Mathematics has a much stronger deterministic path for four skills only.
- Offline prompts outside those four Mathematics skills are **retrieval activities for self-checking**, not authentic past-paper questions, and are not marked automatically.
- The subject list includes some booklet pathways that are not GCSEs, such as Islamic Education, and distinguishes BTEC from examined GCSE routes.
- Official past-paper content is not copied or fed to AI by this app. Source links are general qualification directories where exact paper links have not yet been manually approved.
- Administrator area is an information catalogue, **not** secured management. It cannot currently publish or approve questions.
- Do not over-interpret progress statuses. Mathematically checked answers have a provisional status only with enough attempts; offline/AI practice is recorded but does not confer verified mastery.

## Architecture

- `app.py`: multi-subject Streamlit UI, revision, testing and progress.
- `courses/catalog.py`: all school-booklet pathways and theme outlines, with provenance notes.
- `courses/maths_4ma1.py`: Mathematics specification topics and 4 active skills.
- `engine/questions.py`: deterministic original maths question templates.
- `engine/marking.py`: mathematical final-answer marking.
- `engine/offline.py`: free, general self-check prompts for all other subjects.
- `engine/ai.py`: optional original question generation and indicative feedback.
- `engine/progress.py`: original Mathematics progress helpers retained for compatibility.

## Next milestones

1. Validate all awarding body codes/specification versions and comprehensive topic trees with departments.
2. Add thoroughly verified, topic-specific revision notes and curated resources.
3. Expand high-quality deterministic Maths and Science templates.
4. Add secure invitation-only login, linked parent accounts, row-level data protection and persistent private storage.
5. Implement administrator approval workflows, moderated test cases, and stronger verification for AI generation.
