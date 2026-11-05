# V4.3: Gemini 503 resilience update

The revision-guide generator now requests smaller output, automatically attempts one compact mini-guide after temporary Gemini 5xx failures, and displays an accurate message if Google continues returning HTTP 503. A new **AI connection test → 4. Test compact revision guide** isolates the lower-output path. These changes cannot guarantee availability when Google's service is overloaded. Any retry consumes additional request allowance. Do not change your private API key.

# DBSJP Revision Hub — V4.2 (content-first testing prototype)

## What's in V4

- DBSJP Level 2 subject catalogue, excluding Arabic and Islamic Education and all Level 3 courses.
- BTEC Sport: HYP4 only. Additional Level 2 entries include International GCSE Further Mathematics, ESL, BTEC Music and Applied Science.
- Current school Year 10/11 teaching-map topics are drawn from the supplied 21 curriculum files where relevant; booklet topics are available as a second navigation layer. Uploaded school maps are source documents, not guaranteed examination-board micro-specifications.
- Revise: existing authored content where available; otherwise generate focused, original, structured revision guidance on demand using Gemini, including a worked example and retrieval checks.
- Test: generate original, self-contained questions on demand, with rubrics, written responses, feedback, optional second attempt and a model solution. No permanent question database.
- Maths: four offline parameterised SymPy-checked question families (quadratic formula, factorisation, percentages, ratio). Valid alternative methods are not penalised just because they differ from the exemplar. The percentage/ratio checker now also gives limited, conservative provisional method credit for verified intermediate arithmetic; this is not full GCSE method marking. On-demand AI questions use **provisional** marking, not exact SymPy marking.
- No accounts, student dashboards, progress database or student-identifying prompts. A session-only testing issues log can be exported as JSON.

## Deploy for free (GitHub → Streamlit Community Cloud)

1. Create or use a **private GitHub repository**. Upload the contents of this folder, keeping `app.py` at the repo root. The folders `courses/` and `engine/` must remain intact.
2. On [Streamlit Community Cloud](https://share.streamlit.io/), deploy with main file `app.py`.
3. In the app's settings open **Secrets** and paste (with your own private API key):

   ```toml
   GEMINI_API_KEY = "YOUR_PRIVATE_KEY_HERE"
   GEMINI_MODEL = "gemini-2.5-flash-lite"
   ```

   **Never share your key in chat and never commit it to GitHub.** See official [Streamlit secrets documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).
4. Keep your Gemini project on the **free tier** with **no paid billing**. A single API project allowance is shared across all visitors. The application has a 65-request **per-browser-session** safety cap; this is not a global usage enforcement mechanism. Large-scale/public release needs strong authentication, server-side quotas and an appropriate privacy review.
5. If AI calls fail, existing local Maths and authored practice activities remain available where provided. Unprepared topics honestly state that they need Gemini.

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tests

```bash
python -m pytest -q
```

## Important academic / safeguarding limitations

- **Not examination-board endorsed**. Qualification codes were supplied by the school, but detailed specification-point alignment for most courses requires expert review. A school map's teaching plan is not a full official qualification specification. Some BTEC programme codes/course-size mapping require another internal check.
- **AI is fallible**: revision notes, original question generation and assessment may contain errors. Written/extended answers receive **indicative** marks. When confidence is low, the app must not silently record a wrong mark. More rigorous mathematics method marking is not yet examiner-equivalent.
- **Copyright**: only original questions are generated. Official past papers are linked, not reproduced or submitted to Gemini for processing without permission.
- **Privacy**: the free Gemini API may use submitted content to improve Google's products. During this trusted-testing phase, use anonymised or fictional student work. The app does not intentionally send personal identifiers, but students must not type them into answers. Do not roll out publicly to school pupils without a data-protection and safeguarding review.
- **Free tier**: model quotas and pricing can change. Confirm the model is eligible for your project's Free tier. Keep billing disabled; the application itself does not force the project into a free billing state.

## Suggested test sequence

1. Mathematics → School curriculum or course index → Percentages → try `80 x 0.2 = 16\n80 + 16 = 96` when asked to increase 80 by 20% (note that random local questions use random numbers).
2. Mathematics → Quadratic equations → solve using a valid different method.
3. Science → a taught Year 10 topic → generate revision guide → inspect scientific accuracy.
4. English Literature → taught topic → generate practice question → submit a valid alternative explanation and inspect provisional marking.
5. History / Geography → select taught topics → verify not asking about other options.
6. BTEC → try a skill-practice question. The generator must not pretend the task is an actual internally assessed assignment.
7. Switch subjects while a question is in progress; the old question should reset.
8. Remove the Gemini key locally; check that fallback messages are clear.

### Diagnosing Gemini integration

Version 4.1 adds **AI connection test** in the Streamlit sidebar. Use **Check model availability** to confirm the configured model appears for the API project, then **Test model and JSON response** to make one small generation call. These tests consume a small amount of free API quota. Error messages now show a safe HTTP status and category without exposing the API key or the submitted content. Do not publish Streamlit Secrets. If model-list succeeds but JSON test fails, inspect the displayed HTTP code; 429 usually indicates quota, 404 model availability and 403 access restrictions.


### V4.2: Longer revision-guide generation fix

- Prior V4/V4.1 used the same small error message for large-output issues and could reject valid responses when extra prose, code fences or fields were missing. V4.2 uses concise, explicit revision-guide schema instructions, larger output room, a robust JSON-object parser and safe messages naming which section failed.
- HTTP 500, 502, 503, 504 and timeouts are retried once (a short pause); 429 quota responses are **not retried**. Each network request may count against the shared free-tier quota.
- **AI connection test → 3. Test complete revision guide** exercises the actual revision generation, not just a tiny `{status: ok}` JSON call. Keep the Gemini Secrets key unchanged if the small test succeeds.
- Long content can still fail due to model capacity or truncation. No errors are silently converted to marks or invented revision facts.
