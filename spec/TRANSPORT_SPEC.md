# TRANSPORT OCR MODEL — SPEC (locked decisions)

Read this fully before touching code. Every line was decided by the owner (Pratham). Do not re-ask.

## 1. What we are building
- A web app that reads **bus luggage / parcel receipts** (photos) and extracts structured fields.
- Same tech, same UI, same architecture as ACKN. Only the document type changes.
- One receipt = one uploaded file = one document record. No pairs, no Part 1 / Part 2, no tables, no line items.

## 2. Reference and locations
- Reference repo: https://github.com/prathamthatte52701/OCR-ACKN-MODEL
- Reference folder (READ-ONLY): `E:\ACKN OCR model`
- Second reference (READ-ONLY, only to port missing hardening fixes): `E:\CONSIGNOR MODEL`
- New project folder: `E:\OCR Transport Model`
- New repo: https://github.com/prathamthatte52701/OCR-Transport_Model (must be empty before first push; check with `git ls-remote`; never force-push)
- Test images: `E:\OCR Transport Model\testing data` (20 JPEG files, git-ignored)
- Spec + ground truth + reports live in `E:\OCR Transport Model\spec\` (this file lives there)

## 3. Names, ports, DB
- Database: `docintel_transport` (fresh). Use a new DB name on the same Atlas cluster.
- Ports: backend **2000**, user app **3000**, admin app **4000**.
- NEVER touch databases `ackn_AI_model` or `docintel_cons_cons`.
- Owner pastes the Mongo URL and Groq API keys into Claude Code only. Write them only to the git-ignored `.env`. Never print them, never commit them, never put them in any report.
- Tests run only on `*_test` databases or `docintel_transport`; deletes only by exact id. Never wipe by pattern.

## 4. The test images (what they really contain)
- 20 JPEGs = 18 unique receipts. Two receipts were photographed twice (Baba P98506 and Pawan GR 28625).
- Two operators:
  - **Pawan Travels** (blue ink): Gr No, Dt + time, To, C'nor / C'nee names with GST No and Ph, Tot.Qnty, Pkg.Mode-Contains, Freight Mode (Paid), SGST/CGST/IGST, Tot.Amt, amount in words, Remark, Del.Add., For, Prepared By.
  - **Baba Travels** (red ink): Receipt No (like P98506 or 186,798), Date, Receiver "To", Mobile No (usually 0000000000), Delivery At, Detail ("N Parcel"), Consigner's details (usually "Self"), Amount, Payment Mode (Paid), operator GST 23AHQPS8492M1ZA, name in brackets at bottom. Big BABA TRAVELS watermark behind the text.
- Special cases:
  - One Baba two-copy slip (P8851): read the LEFT copy only.
  - Baba variant 186,798 has Fright / Delivery / Demarage fields.
  - P98828 shows "5-Mar-25" and "10/03/2025" (two dates): use the date next to the receipt number, add a warning.
  - Receiver name spelling varies ("Ve Commercila", "Ve Commerical", "Orlicon Blazer"). Extract what is printed. Do NOT auto-correct or normalise names.
  - Dates are mostly Jan–Mar 2025; Pawan and 3 Baba receipts are in 2026.
- NEVER hard-code anything from these images (no operator-specific strings in logic beyond layout hints in prompts, no receipt numbers, no names). The model must work on receipts we have not seen.

## 5. Fields (flat; empty string when absent)
- Operator: operator_name, operator_gstin
- Receipt: receipt_number (GR no), date, time
- Route: from_place, to_place (to / delivery at), delivery_address
- Consignor: consignor_name, consignor_gstin, consignor_phone
- Consignee: consignee_name, consignee_gstin, consignee_phone
- Parcels: package_count, package_description
- Money: payment_mode, freight, delivery_charge, demurrage, sgst, cgst, igst, total_amount, amount_in_words
- Other: remark, prepared_by
- **Core set** (on most receipts): operator_name, operator_gstin, receipt_number, date, to_place, consignee_name, consignor_name, package_count, payment_mode, total_amount, prepared_by.
- Everything else is **optional**. Accuracy reports always split core vs optional.
- Phone `0000000000` is kept exactly as printed; phone checks accept it.

## 6. Upload rules
- Single upload, and bulk up to **5 receipts per request**.
- JPG / PNG / PDF (page 1 only), max 5 MB each.
- Photo clean-up (deskew, contrast, etc.) kept from ACKN and tuned for the Baba watermark.
- Status, reprocess, restart recovery kept.

## 7. Review, confidence, warnings
- Review page: edit any field, correction history kept (as in ACKN).
- No Save step. A receipt is final when OCR finishes. Edits go to correction history. Reprocess stays.
- Per-field confidence flags + "needs review" filter (as in ACKN).
- Warnings show only position + short reason. New warning set:
  1. receipt number missing
  2. date missing or odd (plausibility window reused from ACKN)
  3. total amount missing
  4. GSTIN format wrong (only when a GSTIN is present)
  5. total ≠ freight + delivery charge + demurrage (only when those exist)
  6. total ≠ amount in words (only when words exist)
  7. phone / receipt-number "looks incomplete" shape check (merged here, one warning per problem, no duplicates)
  8. duplicate: same operator + receipt number + date already exists (WARN, do not block)
- Two-date receipts: use the date next to the receipt number, add a warning.

## 8. Lists, search, downloads
- Documents list: search by receipt number / operator / consignor / consignee; filters: date range, status, needs-review; sort; paging; URL filters kept.
- "View All Details" page kept: sortable table with the transport fields as columns.
- Downloads: single "download original" route (replaces part1/part2), ZIP of many (max 30 docs / 100 MB), delete document, delete file only, delete all.
- Dashboard, training card, My Activity, Help (text rewritten for transport) kept.

## 9. Accounts and admin
- Signup makes the user active immediately (NO admin approval). Signup rate limit kept.
- Removed: pending / rejected / revoked states, approve / reject / revoke routes, approval pages and dialogs, migrate_user_status.
- Google sign-in: removed.
- Admin temporary password reset kept. Delete-user only for abusive users. 7-day tokens kept. Admin access to user data is audit-logged.
- Profile, admin profile, change-password, forgot / set-new password pages kept.
- Admin pages kept: Dashboard (minus pending-approvals box), Users, User detail, Password requests, Documents, Document detail, Activity / audit log, Logs, Orphaned files (with retry), Maintenance danger zone (purge by month AND by date range, nuke user, global nuke, global chat delete).
- Admin pages removed: Approvals, Workbooks.

## 10. Chat (kept as in ACKN)
- 1000 chars, 15-min edit, unread badge, colour setting, "Insert today's summary".
- Chat files: JPG/PNG/WebP 2 MB, PDF 3 MB, 30-day expiry, 75 MB cap.

## 11. Removed completely
- Excel: export, Export History, Workbooks, new-excel-file, bulk-save, save, exports folder, workbook download routes, excel feature module and its tests.
- Google sign-in, approval flow, Part 2 / pair logic (if any trace is found).

## 12. Scripts
- Keep: seed_admin, reset_admin_password, wipe_all_except_admins (needs `--db`, plus `--apply --i-have-a-backup`), cleanup_orphan_corrections (`--db`, dry run default, `--apply`).
- Drop: migrate_user_status, find_duplicate_workbooks, strip_confidence, reset_database.

## 13. UI rule
- Do NOT restyle or redesign the UI. Same look as ACKN. Only remove / rename items and change words. Owner will redo the UI of all projects later.

## 14. Testing rules
- Per-feature tests use at most 4–5 receipts (hard cap). Keep tests quick.
- Do NOT run the full backend test suite. Run only tests for modules you touched, plus the app/core and auth tests once in Loop 1.
- Real-browser checks for UI changes (login, upload, review, list, admin). Admin nav checked at 1100 / 1280 / 1400 and 375 px widths.
- Exception: Loop 3 accuracy run uses all 20 images (one-by-one) and bulk batches of 5.
- Every test user is prefixed `zz_tr_` and deleted by exact id at the end of each loop.

## 15. Accuracy loop (Loop 3)
- Claude Code reads each image itself and writes ground truth (`spec/ground_truth.json`). The two duplicate photos share one truth.
- Owner spot-checks about 5 truth values (list them in the report for him).
- Run A: one-by-one. Run B: bulk of 5.
- Report table (markdown, `spec/accuracy_report.md`): per field and per receipt, **strict** (exact after trimming spaces / case) and **lenient** (ignores punctuation, spacing, common OCR letter/digit swaps, date format), split **core vs optional**.
- Fix loop: up to 3 rounds. Fix only systematic causes (preprocessing, prompt, post-processing). No per-image hacks, no hard-coded values.
- Never inflate scores: report strict and lenient honestly. Name the worst fields.

## 16. Git rules
- Commit after each finished feature (small, clear message). Push at the end of each loop.
- `.env`, `venv`, `node_modules`, `.run`, `__pycache__`, `testing data`, logs, exports = git-ignored. Provide `.env.example` only.
- Never force-push. Never commit secrets.
