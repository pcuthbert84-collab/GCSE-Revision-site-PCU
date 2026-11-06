# DBSJP Revision Hub V4.16 — Five Academic Review Cycles

This release is based on V4.15 and retains V4.14 DBSJP branding, V4.13 Learn/Exam routes, Mathematics and Corbettmaths, subject specifications, Gemini fallbacks and the Academic Quality Manager. It was built exclusively on `v4-16-five-review-cycles` and not merged into production `main`.

## Cycle 1 — Accuracy of cross-subject matches

**Review finding:** V4.15's Science keywords could recommend a Physics index for the Chemistry topic *Energy changes*, or treat a broad *Atomic structure* title as unambiguous.

**Changes:** Filter general PMT indexes by selected science; refuse ambiguous atomic structure matches; distinguish links to indexed collections from exact lessons.

**Re-review:** Regression tests now cover the wrong-discipline and ambiguous title scenarios. More exact school-map matching was needed and became cycle 2.

## Cycle 2 — More useful exact-topic resources

**Review finding:** The school's actual titles include `Y10 · Biology: Bioenergetics`, not only `Bioenergetics`. V4.15's simple matching missed them. Business 4BS1 links were mainly course-level.

**Changes:** Parse explicit Year/discipline prefixes without fuzzy matching; add 13 independently discovered, direct Edexcel International GCSE Business 4BS1 lesson pages (e.g. market research, break-even, cash flow, location, motivation, exchange rates). Do not import provider text as authoritative knowledge.

**Re-review:** Tests for actual school-map titles, discipline conflicts, correct 4BS1 code and refusal of broad business blocks.

## Cycle 3 — Qualification and assessment validity

**Review finding:** An exported curriculum map duplicated some English Language/Literature rows. Literature's generic 30-mark essay choice obscured genuine differences between unseen poetry, anthology and modern prose.

**Changes:** Hide clearly misfiled map rows, retaining original source files unchanged. Differentiate Literature 4ET1 unseen poetry (20 practice marks), anthology poetry (30), modern prose (40), and separate informal named-text writing workshops where the entered route is not verified. Add exact-code check before inserting course-level specification scope in Gemini prompts; keep provisional marks separate from official examiner grades.

**Re-review:** Tests cover mixed English records, correct 4ET1 mode selection and wrong-code blocks. Confirm set-text/coursework route before official examination-style claims.

## Cycle 4 — Teaching relevance and usability

**Review finding:** Actual exact lessons were buried inside a large resource-directory expander, and students could not report incorrect subject-library links. Mixed Science timetable blocks could send unrelated Science topics into Gemini's prompt.

**Changes:** Show exact-matched teaching and practice resources first; move generic directories/official specification links behind a separate expander; provide a student link-reporting control that saves session reports for the existing academic export. For Science maps, restrict the AI's school teaching evidence to the specific Biology/Chemistry/Physics skill rather than adjacent disciplines in the same block.

**Re-review:** New tests cover mixed Biology/Chemistry/Physics teaching blocks, existing scope and direct resource mapping.

## Cycle 5 — Real automated execution and resilience

**Review finding:** Earlier releases had code-only checks because the ChatGPT-local Python environment returned ClientError. The first real GitHub Actions run located two defects, and a concurrent merge of `main` into the working branch had overwritten two reviewed modules and some tests.

**Changes:** Add branch-scoped GitHub Actions CI (Python 3.11, package install, compileall and complete pytest suite), restore reviewed modules/tests, fix faulty regex escaping and the Business Year prefix, and add a headless Streamlit student-home startup smoke test.

**Re-review:** The branch is intended to be accepted only when the latest GitHub Actions run is green. CI evidence is at:
https://github.com/pcuthbert84-collab/GCSE-Revision-site-PCU/actions

## Academic limitations (not hidden)

- Not every subject is matched to every specification sub-point; only independently confirmed exact links appear as topic matches. Larger directories are labelled general.
- Exam question rubrics for extended writing remain *indicative*, not examiner marks. Teacher-marked benchmarking across subjects is still needed.
- Gemini does not scrape or ingest entire third-party websites; the curated qualification summaries and verified links are metadata for safer scope.
- Paid/licensed provider content is not copied into the repository.
- DBSJP's selected English texts/routes, BTEC units, History options and regional exam papers must still be confirmed by departmental leads.
- External images and logos may need hosting updates if the existing image provider removes them.

## Deployment

1. Download the ZIP of branch `v4-16-five-review-cycles` and extract.
2. Review the latest **green** CI workflow. Test a Science topic, a 4BS1 topic, English 4ET1 modes and one Gemini guide + question.
3. Update your GitHub `main` only after checking the staging site and any unrelated changes made directly to `main`. In particular, do not overwrite concurrent edits without comparing them.
4. Streamlit uses the unchanged `app.py` entrypoint and existing Secrets.

The V4.16 work has not changed the deployed application.
