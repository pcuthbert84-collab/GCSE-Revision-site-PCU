# DBSJP Revision Hub V4.15 — Exam-Code-Aware Subject Resource Atlas

Complete code package built as a separate GitHub branch. **Production main remains untouched**.

## Changes

- **New `courses/subject_resource_atlas.py`**:
  - Exam-code-aware official qualification links for current DBSJP GCSE/IGCSE/BTEC pathways, only when the course code matches. Three separate AQA Science specifications are handled distinctly.
  - 25 published AQA Biology, Chemistry and Physics topic pages on Physics & Maths Tutor, which include topic revision and practice collections. Exact title matching, discipline checks and Combined-only/Separate-only checks prevent misleading links.
  - Subject-specific public resource directories for English, History, Geography, Business, Maths, Computing, Food, Drama, languages, D&T, Science and vocational courses. Direct pages and directories are explicitly differentiated, and costs/login requirements mentioned where known.
  - Geography correctly identifies 4XGE1 modular cash-in with 4WGE1 and 4WGE2. Business 4BS1 uses the 2017 qualification; the new 2027 business syllabus is not silently substituted.
  - Includes free, qualification-specific revision sites such as GCSE-ready Pearson 4BS1, Seneca Pearson Edexcel IGCSE History, Oak National Academy KS4 English/Geography, MDN web development, Maths Genie and Cognito.
- **New `courses/specification_scopes.py`**: concise, original, qualification-aware subject overview for each available DBSJP course. Not copied specifications, not exhaustive specification-by-specification audits.
- **Updated `engine/v4_ai.py`**: includes a short, cautious qualification overview and links as *metadata* during lesson/question generation, to reduce incorrect syllabus or assessment-route assumptions. Gemini does not fetch or ingest the websites.
- **Updated `app.py`**: a visible expandable resource library on every subject/topic screen, with official qualification links, relevant matching topic pages, and other catalogues. Retains Corbettmaths, English/History academic teaching, Maths marking and DBSJP red/navy theme.
- **Updated `courses/v4_catalog.py`**: explicit warning about Pearson's modular Geography units.
- **New regression tests**: `tests/test_subject_resource_atlas_v415.py`, `tests/test_specification_scopes_v415.py`.
- **Detailed matrix**: `SUBJECT_RESOURCE_REVIEW_V415.md`.

## Limitations and next work

**V4.15 is the first substantial cross-subject resource and specification-mapping release**, not a fully verified micro-spec-to-lesson database for every subject. 25 PMT Science pages are direct-topic matches, while the other many subject resources are often catalogues rather than exact subtopic links. The already-existing Maths Corbettmaths feature remains the closest full indexed video/worksheet/exercise service.

Do not imply that externally hosted paid/subscription materials are free for all students; site access and URL reliability can change. The app links to sites but does not copy protected content or impersonate exam-board endorsement. Teacher-confirmed set texts, tiers, BTEC chosen units, English coursework/exam routes and History options are needed for rigorous alignment.

The *local* Python/container execution environment failed with ClientError again. GitHub branch/files were independently retrieved and checked, but the **runtime test suite could not be executed**. Do not deploy live until branch smoke-tested. The repository includes regression tests to run with `python -m pytest -q`.

## Suggested student-side smoke test

1. Choose **Combined Science → Biology → Cell biology** and confirm PMT direct topic page plus AQA official route and Cognito directory, with clear labels.
2. Choose **History**, inspect official Pearson 4HI1 and Seneca IGCSE learning resources.
3. Choose **Business Studies**, verify code 4BS1 links to the 2017 Pearson specification and 4BS1 free practice lessons.
4. Choose **Geography**, verify 4XGE1 modular route and official units, not linear 4GE1.
5. Choose **BTEC Information Technology → Website development**, check MDN reference appears only when the topic title matches.
6. Try an existing **Mathematics Standard Form** selection and verify Corbettmaths direct video/practice/textbook remain visible.
7. Test normal Gemini guide/question creation and feedback to ensure no regression.

## Deploy safely

Download the complete branch ZIP via GitHub. Do not merge to `main` until isolated Streamlit test or CI completes.
