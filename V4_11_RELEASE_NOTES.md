# DBSJP Revision Hub V4.11 – English and History Teaching Knowledge

This is a safe, additive update to the working Streamlit source, prepared on a separate branch. It does not change the production `main` branch.

## Implementation
- `engine/academic_teaching.py`: original, curated pedagogical guidance derived from the reviewed English and History departmental materials.
- `engine/v4_ai.py`: inserts the appropriate guidance in the course/topic payload for both revision-guide generation and question generation, and adds subject-specific context to marking feedback.
- `tests/test_academic_teaching.py`: additional regression tests.

## Academic boundaries
- Do not treat uploaded material as automatically verified factual truth.
- Do not invent literary quotations or historical sources.
- Teacher scaffold PETAL is optional, not an examination-board scoring requirement.
- Treat 6-, 8- and 16-mark History skills distinctly and check the exact course/component before implying official mark allocation.
- Approved academic corrections remain the administrator's source of truth.
- No uploaded copyrighted documents have been copied into the source package.
- V4.10 files, Gemini model fallback, Mathematics questions and Corbettmaths features are retained.

## Testing
The tests are included but could not be executed in this session because local Python/container execution returned a platform ClientError. Please run `python -m unittest discover -s tests` before merging into `main`; the changes are NOT claimed to have passed runtime tests.

## Deployment
Download the separate branch archive. Keep `main` in production until the tests and an isolated Streamlit test confirm guide generation, question generation and feedback. After validation, merge the branch into `main`.
