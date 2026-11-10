You are building the Transport OCR Model: ACKN's stack and UI, new document type (bus luggage/parcel receipts).

FIRST, read `E:\OCR Transport Model\spec\TRANSPORT_SPEC.md` completely. It is the source of truth. If this prompt and the spec disagree, the spec wins. Do not re-ask anything the spec already decides.

Work in `E:\OCR Transport Model`. References are READ-ONLY: `E:\ACKN OCR model` (main base) and `E:\CONSIGNOR MODEL` (only to port missing hardening fixes). Never modify either.

======== HARD RULES (apply to every step) ========
1. Secrets: ask me for the Mongo URL and Groq keys ONLY when first needed (Loop 1, step 1.4). Write them only to the git-ignored `.env`. Never print them, log them, commit them, or put them in any report.
2. Databases: use only `docintel_transport` (and `*_test` names in tests). NEVER touch `ackn_AI_model` or `docintel_cons_cons`. Deletes only by exact id, never by pattern.
3. No UI restyle. Same look as ACKN. Only remove / rename items and change words.
4. Tests per feature: at most 4-5 receipts. Do NOT run the full backend suite. Run only tests for modules you touched. Real-browser checks for every UI change.
5. No hard-coding from the test images (no receipt numbers, names, amounts in logic). It must work on unseen receipts.
6. Git: commit after EACH finished feature. Push at the end of each loop. Never force-push. Never commit `.env`, venv, node_modules, `.run`, logs, `testing data`.
7. Challenge, do not guess. If something blocks you or the reference code contradicts the spec, stop and tell me in 3 lines with your recommendation. Do not invent requirements.
8. Test users are prefixed `zz_tr_` and deleted by exact id at the end of each loop.

======== PROGRESS FILE (survives context compaction) ========
Create `LOOP_LOG.md` at the repo root first. It is a checklist of every feature below (IDs 1.1 ... 3.9). After each feature's commit, tick it and write the commit hash and one line of result. At the start of every new step, and after any context compaction, RE-READ `LOOP_LOG.md` and the spec. Never redo a ticked feature.

======== PER-FEATURE CYCLE (every feature) ========
BUILD -> BRUTAL TEST (normal use, real data) -> BREAK TEST (bad input, empty, huge, wrong type, repeated clicks, expired token, other user's data) -> REFINE -> COMMIT.
Use parallel sub-agents only for truly independent work (different files / different apps). Tell each sub-agent its exact file scope and tell it not to commit; you review and commit.

======================================================
LOOP 1 — FOUNDATION (ACKN copy, strip, rename)
======================================================
1.1 Pre-checks. Confirm both reference folders exist. Confirm `E:\OCR Transport Model\testing data` has 20 images and `spec\` exists. Run `git ls-remote https://github.com/prathamthatte52701/OCR-Transport_Model`; the repo must be empty (stop and tell me if not).
1.2 Copy ACKN into the folder with robocopy WITHOUT `/MIR` and WITHOUT `/PURGE` (never delete `spec` or `testing data`). Exclude: `.git`, `venv`, `node_modules`, `.env`, `.run`, `__pycache__`, `.claude`, `ackn testing data`, `ackn-wt-*`, `graphify-out`, `backend/logs`, `backend/exports`, `LOOP_LOG.md`. Copy `CLAUDE.md`, `SKILLS.md`, `ANALYSIS.md`, `docs`, `design-ref` as a base; rewrite them for transport in step 3.8 (do not leave ACKN wording).
1.3 Rename identity: DB `docintel_transport`; ports 2000 / 3000 / 4000 everywhere (backend config, vite configs, CORS origins, proxy targets, bat scripts, README, `.env.example`, tests); package names, page titles, app name, bat window titles, log file names. Then grep the whole repo (excluding `testing data`) for leftovers: `ackn_AI_model`, `docintel_cons_cons`, `ACKN`, `ackn`, `8000`, `5174`, `5175`, `9000`, `6001`, `7000`, `CONSIGNOR`. Fix every real hit. Report the grep result. Commit.
1.4 Environment: create `.gitignore` additions (`.env`, `.run`, `testing data`, `backend/logs`, `spec/*.tmp`), create `.env.example` only (no real values). Now ask me for the Mongo URL and Groq key(s) and write `.env`. Create venv, install `requirements.txt`, `npm install` for frontend and admin. Verify the backend boots on 2000 and both apps build. `git init`, set remote, first commit, push `main`. (Check remote still empty right before push.)
1.5 Remove Excel completely: backend `excel` feature and its tests, routes (`/workbooks*`, `/workbook/download`, `/new-excel-file`, `/export-history*`, `/exports`, `/bulk-save`, `/{doc_id}/save`), exports folder logic, Excel libraries from `requirements.txt` if unused elsewhere, user pages ExportHistory, admin page Workbooks, nav items, dashboard widgets that reference Excel, README mentions. Commit.
1.6 Remove approval and Google: states pending/rejected/revoked, routes approve/reject/revoke, Approvals admin page, pending-approvals dashboard box, RejectReasonModal, ApprovedWelcomeDialog, Google route and `GoogleSignInButton`, Google deps/env keys. Signup makes the user active immediately and logs them in as ACKN does after a normal signup. Keep the signup rate limit. Delete `migrate_user_status`. Commit.
1.7 Remove the Save step: a receipt is final after OCR. Remove the Save button/flow and "saved" status. Edits still go to correction history. Reprocess, delete, delete file stay. Commit.
1.8 Scripts: keep seed_admin, reset_admin_password, wipe_all_except_admins, cleanup_orphan_corrections (with their tests, fixed for the removals). Delete migrate_user_status, find_duplicate_workbooks, strip_confidence, reset_database and their tests. Commit.
1.9 Hardening gap check. Diff ACKN-copy against `E:\CONSIGNOR MODEL` (read-only) for these items and port ONLY what is missing, each as its own commit with a test: login with over-long email returns the generic 401 (and password length cap); email max length 254; config treats blank/whitespace env values correctly and a blank `MONGO_URI` fails fast; rate-limit key safety (per-client key, `test_rate_limit_key`); chat clear-all counts only wrong passwords and uses a per-key lock without leaking lock entries (do NOT copy the unbounded `_clear_all_locks` dict; clean it up); opt-in `CHECK_INSTALLED_PINS=1` pins test and exact pins in `requirements.txt`; the admin nav layout fix (fits at 1100 / 1280 / 1400 and 375 px); setup.bat / start.bat / stop.bat style with window titles and PID files in `.run`; CI workflow `.github/workflows/ci.yml`. Report a table: item | present in ACKN? | ported?
1.10 Fix tests broken by 1.5-1.9. Run only: `app/core` tests, auth tests, and the tests of modules you touched. Then a real-browser smoke: signup (user active at once), login, upload page loads, dashboard loads, admin login, admin Users page, admin nav at 4 widths. Delete `zz_tr_` users by exact id.
1.11 Push. Tick `LOOP_LOG.md`. Print a 10-line Loop 1 report (what changed, what failed and was fixed, anything I must decide).

======================================================
LOOP 2 — TRANSPORT ENGINE
======================================================
Start by reading how ACKN's `ocr` and `documents` features work (pipeline, prompts, schema, post-processing, confidence, warnings, list/search code, frontend pages). Keep ACKN's architecture. Change only the document type.

2.1 Schema and model. Replace ACKN's extracted fields with the flat field list in spec section 5 (empty string when absent). Update the Mongo document shape, API schemas, validators, correction-history, and the frontend field config. Core vs optional flag per field. Commit.
2.2 Preprocessing. Keep ACKN's photo clean-up. Tune for the red BABA TRAVELS watermark (reduce watermark interference before OCR). Detect a two-copy slip (two receipts side by side) and use the LEFT copy only. Test on 4-5 receipts including one Baba watermark receipt and the two-copy slip. Commit.
2.3 Extraction. Update the PaddleOCR + Groq extraction for the new fields. The prompt must handle both operator layouts (Pawan labels; Baba labels incl. `Receipt No`, `To`, `Mobile No`, `Delivery At`, `Detail`, `Consigner's details`, `Payment Mode`, `Fright/Delivery/Demarage` variant). Rules: extract text exactly as printed; do not correct spelling of names; keep `0000000000`; two dates -> the date next to the receipt number; amounts as plain numbers; empty string when absent. Add deterministic post-processing (trim, digit/letter confusions in numeric fields only, GSTIN uppercase and format check, date normalisation to one format, phone digits). Commit.
2.4 Confidence and needs-review for the new fields, using ACKN's mechanism. Commit.
2.5 Warnings per spec section 7, items 1-7, including the merged "looks incomplete" shape checks. One warning per problem. Show only position + short reason. Commit.
2.6 Duplicate warning (operator + receipt number + date): warn, never block. Test with the two receipts that were photographed twice. Commit.
2.7 Upload API: single upload and bulk up to 5 per request; JPG/PNG/PDF (page 1 only), 5 MB each; clear errors for wrong type, too large, 6th file, empty file, corrupt image. Status / reprocess / restart recovery still work. Commit.
2.8 Frontend (no restyle): review page shows the new fields with edit + correction history + confidence flags + warnings; documents list columns and search (receipt number / operator / consignor / consignee), date-range / status / needs-review filters, sort, paging, URL filters; "View All Details" with transport columns and sorting; single "download original" (replaces part1/part2); ZIP download unchanged; dashboard and training card numbers; My Activity; Help page text rewritten for transport. Commit per sub-feature. Real-browser check each.
2.9 Admin: document list and detail show the new fields; Logs, Orphaned files (retry), Password requests, Maintenance (purge by month AND date range, nuke user, global nuke, global chat delete) all still work after the field change. Commit.
2.10 Live check on 5 receipts (one Pawan, two Baba incl. watermark, the two-copy slip, one with GST fields) through the real UI, single and one bulk of 5. Show me the extracted values next to what you read from the image for each. Fix real bugs only. Delete `zz_tr_` users by exact id. Push. Tick `LOOP_LOG.md`. Print a 10-line Loop 2 report.

======================================================
LOOP 3 — PROOF AND POLISH
======================================================
3.1 Ground truth. Read each of the 20 images yourself (view the image) and write `spec/ground_truth.json` for the 18 unique receipts (the two duplicate photos share one truth). Use the exact spec field names; empty string when absent; text exactly as printed. In your report list 5 truth values that I should spot-check against the photos (file name + field + your value). Commit.
3.2 Scoring script `spec/score.py`: strict (exact after trimming spaces and case) and lenient (ignore punctuation/spacing, common OCR letter/digit swaps, date format). Per field, per receipt, split core vs optional. Unit-test the scorer on tiny synthetic cases first. Commit.
3.3 Run A: upload all 20 images ONE BY ONE through the real API/UI. Run B: bulk batches of 5 (4 requests). Save raw results to `spec/results.csv`. Commit.
3.4 Report `spec/accuracy_report.md`: markdown tables for both runs: overall strict / lenient; core vs optional; per-field table; worst 5 fields; list of every mismatch (receipt | field | truth | OCR). Do not inflate. Say honestly what the numbers mean.
3.5 Fix loop, max 3 rounds: find systematic causes (preprocessing, prompt, post-processing), fix them, re-run the affected runs, update the report with a before/after table. No per-image hacks, no hard-coded values. Stop early if strict core accuracy is stable. Commit each round.
3.6 Unseen-receipt sanity: take 3 receipts you have NOT used for any prompt tuning (pick by file name, say which) and show their results separately, to expose overfitting.
3.7 Final hardening verification: re-test login limits, over-long inputs, other-user data isolation (user A cannot read user B's document by id), admin audit log entry on admin access, bulk limit 5, 5 MB limit, expired token, no `.env` or secrets in git (`git log -p` grep for the Mongo host and the key prefixes), no leftover ACKN / CONSIGNOR names, ports only 2000 / 3000 / 4000.
3.8 Docs and scripts: rewrite `CLAUDE.md`, `SKILLS.md`, `ANALYSIS.md`, `docs`, `design-ref` notes for transport (fresh, short, accurate). Write a full README: what it does, features, screenshots-free quick start, setup / start / stop bat usage, ports, env keys (names only), field list, warnings, accuracy numbers copied exactly from the report (strict AND lenient, core vs optional), maintenance scripts table, backups (`mongodump`), logs, security notes. README numbers must match the report; no overclaims. Update setup.bat / start.bat / stop.bat (titles, ports 2000/3000/4000, PID files in `.run`). Make sure CI (`ci.yml`) runs and name the exact tests it runs. Commit each.
3.9 Cleanup: delete all `zz_tr_` users and test data by exact id on `docintel_transport`. Confirm `git status` clean, `.env` ignored. Push. Tick `LOOP_LOG.md`.

======================================================
FINAL REPORT (end of everything, max 25 lines)
======================================================
- Commit list (hash + message) per loop.
- Accuracy table (strict / lenient, core / optional, Run A and Run B) and the 5 truth values I must spot-check.
- What you could not verify and why.
- The next likely problem or weak point you see (one to three items).
- Anything I must do myself (for example: rotate keys later, review the five truth values).
