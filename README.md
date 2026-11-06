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


### V4.4: upstream 503 protection
Keep your current `GEMINI_API_KEY` and `GEMINI_MODEL`. Optionally add:

```toml
GEMINI_FALLBACK_MODEL = "gemini-3.1-flash-lite"
```

When and only when the configured primary model returns a transient upstream
HTTP 500/502/503/504 or timeout, the app attempts a second, separately documented
free-tier model. It does **not** switch for quota (429), auth (401/403), invalid
requests or invalid JSON. The fallback is not a guarantee of availability and
requests still use the project's free quota. Do not enable paid billing. The AI
diagnostics page offers an independent test of the fallback model.

## V4.5 — academically grounded generation and feedback

- The generation engine sends a privacy-minimised extract (up to 2,200 characters) of the *selected* DBSJP school curriculum map, instead of the previous 350-character excerpt. When only a broad booklet/index heading is available, it marks that distinction in the model input. The extract is untrusted data, never instructions.
- Prompts now require measurable, topic-specific learning outcomes, concrete explanations, legitimate worked examples, and accurate misconceptions. Course codes alone do not establish the exact assessment requirements or micro-specification. No invented set-text quotations, BTEC assignments, historical facts or exam-board endorsements.
- Mini and normal revision guides must include genuine subject-specific learning objectives; vague stock outcomes and very short knowledge points fail validation. No generic outcomes are silently invented by the fallback parser.
- Generated questions are original, self-contained, restricted to the selected topic and include marking criteria with a valid mark total. Hints must not reveal answers.
- AI assessment explicitly accepts valid alternate methods/interpretations and supported partial credit. Scores remain indicative, and uncertain interpretations should be flagged for review rather than confidently marked wrong.
- The working free-tier Gemini primary / backup model logic and diagnostic tools are unchanged. No API secrets are stored in the repository.

This improves guardrails; it **does not** independently verify every generated scientific, historical or subject-specific statement or guarantee examiner-equivalent marks. Continue testing with anonymised learner answers and report questionable examples.

## V4.6 — Direct topic-specific links and permanent academic correction management

### What is new

- Removed the generic AQA/Pearson/BBC homepages and Google-search links from **Revise**. This section now shows only hand-checked, directly linked resources for the selected topic (initial seed collection) or administrator-approved exact-topic links. Where no matching approved resource exists, it **says so** instead of making up links.
- Students and testers can report inaccurate revision guides and broken/mismatched resources as well as question and marking errors. Issue reports remain session-only until exported or used to create an approved academic rule.
- **Academic Quality Manager** (no student accounts): password-gated admin page to review reports, approve correction rules with the exact intended scope (specific topic / one subject / all subjects), add checked links for individual topics, archive outdated items, and export data for major ChatGPT-assisted code improvements.
- Approved instructions are appended to the **next** Gemini study-guide, question-generation and marking requests. They do not alter Google's model weights, and cannot guarantee the model obeys them perfectly. Existing session-cached guides are cleared in the current browser after an admin approves a rule. A later testing pass should turn significant errors into permanent Python regression tests.
- Every approved rule/link has an audit record and can be archived. The GitHub Contents API commits the JSON to `data/academic_quality.json`, so approvals persist across Streamlit restarts and redeployments once configured.
- Existing V4.5 Gemini primary/backup settings remain unchanged. Free-only Gemini usage constraints still apply.

### Important: configure permanent saves using your existing PRIVATE GitHub repo

GitHub already hosts this Streamlit project, so **no Supabase or paid database is required** for these non-student academic rules. The app will **not claim success or persist changes** until the following is configured.

1. Ensure the GitHub repository holding this project is **private**. The file `data/academic_quality.json` is a non-secret configuration/audit file, but reviewer notes should still be anonymised. Do not store identifiable student responses here.
2. In GitHub select **Settings (account) → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**, or visit [GitHub personal access tokens](https://github.com/settings/personal-access-tokens). Set **Repository access → Only select repositories** and choose **only the Revision Hub repository**. Set **Repository permissions → Contents → Read and write**. Do not grant administration or workflow permissions. Use an expiry and rotate it when needed. Copy the token privately once.
3. On Streamlit Community Cloud open your app **Manage app → Settings → Secrets** and append to the existing Gemini entries:

   ```toml
   QUALITY_GITHUB_REPO = "your-github-username/your-private-repo-name"
   QUALITY_GITHUB_BRANCH = "main"
   QUALITY_GITHUB_TOKEN = "YOUR_FINE_GRAINED_TOKEN"
   QUALITY_ADMIN_PASSWORD = "YOUR_LONG_UNIQUE_ADMIN_PASSWORD"
   ```

   The branch must match the actual GitHub deployment branch, usually `main`. **Do not post or commit any of these secret values.** A strong unique administrator password is important. This prototype has only a simple password gate, not a production-grade role/access system.
4. Save and restart Streamlit if necessary. Open **Academic Quality Manager**, unlock it with the administrator password, and verify that the green message says **Permanent review storage connected**. If not, read the error: invalid credentials, wrong repo name, blocked branch, or insufficient GitHub permissions are common causes.
5. Test by approving a non-sensitive sample correction for a specific topic, and ensure `data/academic_quality.json` is updated in GitHub. Reload the website and confirm the correction is present. Archive the test rule afterward.

### How reviewing works

- A tester flags a question or guide. The report is not automatically trusted or learned.
- An authorised reviewer checks the actual subject material and drafts a correction such as *“Accept both the percentage multiplier method and calculating the increase separately, when both steps are valid.”*
- The reviewer chooses the scope. A topic rule only applies to exactly matching **subject and topic text**; a subject rule applies to the whole subject; a global rule applies across all subjects. Narrow scopes are safer.
- Once saved to GitHub, applicable approved instructions are passed to later Gemini calls. **This is persistent prompting, not model retraining.** For real code-engine errors, export the data and bring the example to ChatGPT to improve Python logic and tests.
- Links can only be added from the listed education-provider allowlist and must point to a direct lesson/video/worksheet, not a homepage or search-results page. The reviewer must verify correct content and free access manually before clicking Approve. A working HTTP address alone does not establish curriculum fit.

### Security and limitations

- This prototype **does not implement student accounts**. The administrator password is a simple gate appropriate only for a trusted pilot; for a public school launch, use proper administrator authentication, abuse protections and access controls.
- GitHub token and password live in **Streamlit Secrets**, never in GitHub code or in the app's UI. GitHub requests are server-side, HTTPS-only, and use the previous file SHA to avoid clobbering concurrent changes.
- Approved site resources are a deliberately small verified starter set, **not** comprehensive links for every one of the hundreds of school topics. Unverified topics show no external links. Continue adding exact-topic links as you verify them.
- A direct link may become unavailable or move later. Report broken links, and archive them in Academic Quality Manager. The link is not continuously monitored by a crawler.
- If GitHub persistence is not configured, the page explains that saving is unavailable. The app's existing study/test features still work.
- The mathematics deterministic checker and existing Gemini 503 fallback remain available; approved rules improve future AI prompts but are not a substitute for domain-specific validation.

### V4.6 automated checks

```bash
python -m pytest -q
```

Checks cover strict direct-link matching, refusal of generic/search URLs, rule scope, archived rules, GitHub save failure without Secrets, API data roundtrip, and the prior marking/AI tests.
