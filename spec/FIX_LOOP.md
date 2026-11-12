TRANSPORT OCR - FIX LOOP (master prompt)

REPO: prathamthatte52701/OCR-Transport_Model, branch master. Folder E:\OCR Transport Model.
Ports 2000/3000/4000. Live DB docintel_transport. Test DB docintel_transport_test.
Read first, then re-read after ANY context compaction: CLAUDE.md, LOOP_LOG.md,
spec/TRANSPORT_SPEC.md, spec/accuracy_report.md, and this prompt (save it as spec/FIX_LOOP.md).

RULES (strict, never break)
- Simple English in all messages to me. Short. Bullets.
- ONE commit per feature, message style "fix: ..." / "feat: ..." / "docs: ...", professional.
  Push at the end of every loop. Tick LOOP_LOG.md (new section "Fix Loop") after every commit.
- Every feature goes through: write the bug test first (must FAIL on current code) -> fix ->
  brutal test (real inputs, edge inputs) -> break test (try to break the fix on purpose) ->
  refine -> commit. Show the failing-then-passing proof in LOOP_LOG.
- Live tests: real files from "testing data/", max 4-5 documents per feature, on docintel_transport
  (owner permission given). Test users must start with zz_tr_. When the feature test ends, DELETE by
  exact id: test users, their documents, GridFS files, corrections, audit logs. Confirm zero left.
- NEVER touch ackn_AI_model or docintel_cons_cons. NEVER commit .env or secrets. Secrets stay in
  Claude Code only. Never hard-code receipt values in code or prompt.
- DO NOT restyle or redesign the UI. Only ADD elements, using classes already used in the app
  (amber warning style such as border-amber-800/50 bg-amber-900/15 text-amber-300). Owner redoes UI later.
- Use parallel sub-agents ONLY for mini-phases that touch different files. Merge, then run all tests.
- If a fix needs a product decision or a UI redesign: do NOT guess. Write it in LOOP_LOG under
  "Needs owner decision" and move on.
- Report honestly: strict and lenient numbers both. No fake success.

ISSUE LIST (verify each one first: reproduce, then fix)
 I1  Backend warnings (doc.warnings, isDuplicate) are never rendered in user app or admin.
 I2  warnings.py total check ignores sgst/cgst/igst -> false "Total does not match".
 I3  Amounts "Rs. 500", "Rs.500", "500/-", "Rs 500/-", "Only" are not cleaned (correct_amount_format).
 I4  Dates "5/11/2026", "05/11/26", "5-11-2026" are blanked and the raw value is lost.
 I5  Blank optional fields are hidden (receiptFieldsFor) so cannot be edited; check_request blocks
     empty value so a wrong value cannot be cleared; CorrectionModal maxLength=40 but backend allows 300.
 I6  Duplicate check is case-sensitive ("Baba Travels" vs "BABA TRAVELS").
 I7  pipeline.py: cut_from_background now only means "photo was rotated", so rotated photos skip all
     preprocessing. Leftover from the disabled paper-crop step.
 I8  conftest.py default test DB is ackn_AI_model_test and safe_to_drop() requires "ackn_" prefix.
 I9  User-visible ACKN wording: "acknowledgement" in Dashboard.jsx (alt + empty text), DocumentList.jsx.
 I10 _clean_text_field: NaN / Infinity raises, a float like 500.5 is dropped.
 I11 Google leftovers: frontend/.env.example VITE_GOOGLE_CLIENT_ID, admin EditUserModal googleUser
     logic, reset_admin_password.py Google branch, stale Excel/workbook/ACKN comments and docstrings.
 I12 Prompt says "exactly these 26 values" but lists 27 (code has 27). README/CLAUDE/LOG say 26.
 I13 Login per-email limiter counts successful logins and can lock out an account (DoS).
 I14 documents list: ?page=0 falls into the unbounded legacy full-list mode.
 I15 needsReview filter only checks *NeedsReview flags, ignores missing receipt/date/total and isDuplicate.
 I16 upload_limit.py guards POST only and lets a negative Content-Length pass (Consignor repo has the fix).
 T1  Baba receipts get invented freight (copied from Amount) and deliveryAddress (copied from
     "Delivery At", same as toPlace). Proof: spec/results.csv vs ground_truth.json, 19 false values
     in Run A. score.py ignores fields whose truth is blank, so it cannot see this.
 T2  Prompt contains test answers: real operator GSTIN literal and the "Ve Commercila" misspelling.
 T3  "Unseen" check was not unseen (Pawan GR28625 dup is the same receipt). Data is 15 Baba from one
     operator + 3 Pawan from one sender. Images are gitignored so runs cannot be reproduced by others.
 T4  Deskew runs on full un-cropped photos (paper crop disabled) and may rotate wrongly. UNVERIFIED.

LOOP 1 - BACKEND CORRECTNESS  (sub-agents allowed: A=extraction+json_parsing, B=warnings+duplicate,
        C=documents router+correction_rules, D=core (upload_limit, rate_limit, conftest))
 1.1 [I3,I4,I10] extraction.py + json_parsing.py
     - One shared amount cleaner (strip Rs/Rs./RS/INR/currency, commas, "/-", "Only", spaces) used by
       correct_amount_format AND warnings._to_number. Keep the confusion map only after cleaning.
       Guard: never turn a word like "OD" into "00" (only apply the map when most chars are digits).
     - Dates: accept 1-2 digit day/month and 2 digit year (YY -> 20YY only if inside the plausibility
       window), separators . / - and spaces. If still not parseable, KEEP the trimmed raw text in "date"
       with dateNeedsReview=True (as printed, matches docstring). Check every reader of "date"
       (sort, month filter, duplicate, zip name, correction_rules, date_window) still works.
     - _clean_text_field: floats -> str without crashing (500.5 -> "500.5"; 500.0 -> "500"),
       NaN/Infinity -> empty + log. parse_extraction_json: reject NaN/Infinity constants so the one retry
       in extract_header runs.
     - Unit tests for every example in I3/I4/I10 plus break cases.
 1.2 [I2] warnings.py: expected total = freight + deliveryCharge + demurrage + sgst + cgst + igst
     (only parts that are present). Test: freight 100 + sgst 2.5 + cgst 2.5 = total 105 gives NO
     warning; total 110 gives the warning. Pawan 0/0/0 taxes still fine.
 1.3 [I6] duplicate.py: match operatorName + receiptNumber case-insensitive, trimmed, inner spaces
     collapsed (use Mongo collation strength 2 or a normalised compare - choose, justify in log).
     Test BABA TRAVELS vs Baba Travels and "P98506" vs "p98506 ".
 1.4 [I14,I15] documents/router.py: page present (even 0) = paged mode, clamp to >=1.
     needsReview = any *NeedsReview flag OR isDuplicate OR (processed AND missing receiptNumber/date/
     totalAmount). Say clearly in the docstring that total-mismatch is not filterable (computed on read).
 1.5 [I5-backend] correction_rules.py: allow an empty value to CLEAR a field (all 27 fields), store "",
     reset its NeedsReview/AutoCorrected flags, write the corrections row, refresh duplicate flag when
     operatorName/receiptNumber/date changes. Non-empty rules stay strict. Same change in the admin
     correction route (shared helper). Tests: user route + admin route + 409 race still works.
 1.6 [I7] pipeline.py: remove the "skip preprocessing when rotated" rule. Verify with a real photo and a
     synthetic rotated copy of it (4-5 docs max) that OCR text is not worse. If worse, keep the skip but
     rename the variable and fix the comment to say what it really means. Log the numbers.
 1.7 [I8] conftest.py: default test DB docintel_transport_test, env var TEST_MONGO_DB_NAME,
     safe_to_drop prefix "docintel_transport_". Update test_conftest_drop_guard.py. Prove the old ACKN
     name is now REFUSED.
 1.8 [I16] upload_limit.py: also guard PATCH; negative Content-Length = 413/400 malformed. Test it.
 1.9 [I13] rate_limit.py + auth/router.py: per-email limiter keyed on email + client IP; count FAILED
     logins only (check with limiter.test(), hit on failure). Tests: 20 bad tries lock that email+IP,
     a success does not count, another IP is not locked, per-IP slowapi limit unchanged.
 END OF LOOP 1: full backend pytest on docintel_transport_test, ruff/lint if configured. Push.

LOOP 2 - PROMPT, GUARDS AND HONEST MEASUREMENT  (do in order, one agent at a time; they share files)
 2.1 [T1,T2,I12] transport_receipt.j2
     - Baba "Delivery At" goes ONLY to toPlace. deliveryAddress only from Pawan "Del.Add." (explicit).
     - freight on Baba only when a "Fright" label exists; a lone "Amount" is totalAmount only.
     - Remove every real value used as an example (operator GSTIN literal, "Ve Commercila", real names,
       real route cities). Use obvious fake shapes (e.g. 27ABCDE1234F1Z5, "Sample Traders").
     - Field count: render it from code (len(EXTRACTION_VALUE_FIELDS)) so prompt, code and docs cannot
       drift. Fix 26 -> 27 in README, CLAUDE.md, config.py comment, LOOP_LOG note.
 2.2 [T1] deterministic guards in extraction.py, ONLY if measured useful on the 20 images:
     toPlace == deliveryAddress (case-insensitive) -> clear deliveryAddress. freight == totalAmount with
     no other charge on a Baba receipt -> decide with data. Gate: false values go down AND no true value
     is lost. Otherwise do not add the guard and say so.
 2.3 [T1,T3] spec/score.py + test_score.py: add false-value metric (truth blank, prediction not blank):
     count, rate, top fields. Score per UNIQUE receipt for duplicate pairs (do not count a pair twice).
     Report it next to strict/lenient. Unit tests.
 2.4 Re-run accuracy once (Run A one-by-one, Run B bulk of 5) on docintel_transport, update
     spec/results.csv, mismatches_*.csv, spec/accuracy_report.md. Show before/after for: overall,
     core, optional strict+lenient, false-value count, worst fields. Honest. Clean zz_tr_ data by exact id.
 2.5 [T3] In accuracy_report.md add a "Limits of this test" section: dataset is 15 Baba (one operator) +
     3 Pawan (one sender), "unseen" check reused a duplicate, images are not in git. Add
     spec/HOLDOUT.md telling the owner exactly what to add (>=10 NEW receipts, other operators/senders,
     never used for prompt tuning). Do not invent a holdout result.
 END OF LOOP 2: backend tests green. Push.

LOOP 3 - FRONTEND + ADMIN  (sub-agents allowed: A=frontend pages, B=admin, C=cleanup/wording)
 3.1 [I1] Show doc.warnings (de-duplicate by message) as an amber box on DocumentDetailPage and on the
     UploadPage review card; show a small attention badge on the My Documents card when warnings exist
     (same rule as backend needsReview). Do the same in admin AdminDocumentsPage detail/row.
     Port the pattern from OCR-CONSIGNOR-CONSIGNEE-BILL-AI frontend (DocumentDetailPage reviewWarnings box,
     lib/needsAttention.js) but with Transport data (warnings = [{field,message}]) and existing classes.
 3.2 [I5-frontend] receiptFields.js: add an option so detail page + upload review card show ALL 27 fields
     ("Not available" + Edit for blank ones). Tables/ViewAll/MyActivity keep hiding blanks.
     Admin document edit gets the same: every field editable.
 3.3 [I5] CorrectionModal (user) and the admin edit modal: maxLength 300 (match backend), allow saving
     an empty value = "Clear value" (clear wording, no restyle), show the backend error text.
 3.4 [I9,I11] Replace every user-visible "acknowledgement" wording with receipt wording. Remove Google
     leftovers (.env.example VITE_GOOGLE_CLIENT_ID, EditUserModal googleUser code, reset_admin_password.py
     Google branch + its test). Clean stale Excel/workbook/ACKN comments and docstrings across backend and
     frontend (comments only, no behaviour change). Final grep proof: zero hits for
     acknowledg|workbook|google|excel|ackn outside spec/, ANALYSIS.md, LOOP_LOG.md, git history.
 REAL BROWSER CHECK (use your browser tools, 4-5 docs max, test user zz_tr_*):
   upload a Baba + a Pawan receipt; see the warnings box; upload the same receipt twice and see the
   duplicate warning; edit a blank optional field; clear a wrong field; type a 150-character remark;
   admin edits a user's document field. Admin nav still fine at 1400, 1280, 1100, 375 px.
   Screenshots in spec/screenshots_fixloop/ only if small. Clean zz_tr_ data by exact id.
 END OF LOOP 3: frontend + admin lint, build, node tests green. Push.

LOOP 4 - AUDIT OF FILES NOT YET REVIEWED  (3 read-only sub-agents in parallel, then fix one by one)
 Read line by line and look for REAL bugs only: backend/app/features/admin/router.py,
 purge_service.py, chat/service.py, chat/files.py, chat/router.py, ocr/paddle_runner.py,
 ocr/row_assembly.py, app/scripts/*, admin/src pages, frontend/src hooks.
 Also [T4]: with real photos that still have background, measure deskew on/off (OCR text quality, 4-5 docs).
 Change preprocessing ONLY if proven worse. Otherwise write the result in LOOP_LOG.
 For every confirmed bug: failing test -> fix -> brutal -> break -> commit (one commit each).
 Unsure items go to "Needs owner decision". Report a table: file, bug, proof, fixed yes/no.

LOOP 5 - DOCS AND FINAL PROOF
 5.1 README.md: update to match the code: 27 fields, warnings list (with the tax fix), needs-review rule,
     clear-a-field and edit-every-field behaviour, test DB name and env var, accuracy numbers copied
     EXACTLY from the new accuracy_report.md (strict + lenient + false-value count), honest limits,
     scripts, backups. CLAUDE.md, ANALYSIS.md, SKILLS.md fixed to match. spec/FIX_LOOP.md kept.
 5.2 Final proof: full backend pytest, frontend + admin lint/build/node tests, git status clean,
     .env ignored (root and backend), grep proof for leftovers, no zz_tr_ users or orphan files left in
     docintel_transport (show the count), git log of this loop.
 5.3 Final report to me (simple English, bullets): issue table I1..T4 with status (fixed / not fixed /
     needs owner decision) + commit hash, before/after numbers, what is still weak, what I must do:
     rotate Atlas password + Groq keys, add holdout receipts, confirm the Baba "Fright" line on one photo.

START NOW with Loop 1. Say one line what you are doing, then work. Do not ask me questions unless a
decision is truly mine (list them at the end instead).
