# LOOP_LOG — Transport OCR Model

Checklist of every feature. Tick after commit. Re-read this + spec at start of every step and after any context compaction. Never redo a ticked feature.

## Loop 1 — Foundation
- [x] 1.1 Pre-checks (refs exist, 20 images, spec dir, remote empty) — no commit needed
- [x] 1.2 Robocopy ACKN base into repo — d612416
- [x] 1.3 Rename identity (DB docintel_transport, ports 2000/3000/4000, grep leftovers) — d612416
- [x] 1.4 Env setup (.gitignore, .env.example, .env, venv, npm install, first push) — d612416, 629b1d1
- [x] 1.5 Remove Excel feature completely — pending commit. Known fallout for 1.10: backend test_admin_audit.py, test_ui_aggregates.py, documents/test_isolation.py, ocr/test_date_needs_review.py, core/test_indexes.py reference deleted excel code; scripts/find_duplicate_workbooks.py + its test still import deleted excel_service (dropped in 1.8 anyway); `exported` field left on documents schema/correction (harmless, Excel-era leftover, consider stripping later)
- [x] 1.6 Remove approval flow + Google sign-in — pending commit. Known fallout for 1.10: backend tests test_admin_vs_admin, test_dashboard_stats, test_ui_aggregates, test_password_requests_admin, test_field_limits (google token test), test_wipe_all_except_admins, chat/test_chat_permissions, documents/test_isolation, test_password_requests, chat/test_chat_service all reference removed approval/pending/Google logic. Admin UI still labels active users "Approved" (status value kept as "approved" string, cosmetic only — consider relabel in UI pass).
- [x] 1.7 Remove Save step — satisfied by 1.5 (c63464c): ACKN's "Save" button was save-to-Excel; no separate "saved" document status existed. Verified clean, no new commit needed.
- [x] 1.8 Scripts: keep/drop per spec section 12 — pending commit. Kept: seed_admin, reset_admin_password, wipe_all_except_admins (+test_wipe_password_requests), cleanup_orphan_corrections. Dropped: find_duplicate_workbooks, strip_confidence, reset_database (migrate_user_status already gone in 1.6).
- [x] 1.9 Hardening gap check vs CONSIGNOR MODEL — pending commit. Ported: login over-long email -> generic 401 (schemas.py + router.py + test_email_length.py), rate-limit key spoof test (copied verbatim), chat clear-all only-wrong-passwords-count + bounded per-key lock pool (not an unbounded dict, avoiding CONSIGNOR's own leak), opt-in CHECK_INSTALLED_PINS test. CI workflow explicitly skipped per owner's order. Config (item 3) and email-254 (item 2) already correct in Transport, no port needed. Admin nav (item 7) no CSS fix to port (different design). Bat scripts (item 8) marginal polish only, not ported. All new/changed tests pass: 39 passed, 1 skipped.
- [x] 1.10 Fix broken tests + browser smoke — NOTE: this work was done (all known fallout fixed, 162 tests passed individually, 9/9 browser smoke checks passed) but the commit was skipped before Loop 2 started on owner's "don't stop" order. These file changes got bundled into the Loop 2 backend commit instead of their own commit — functionally complete, just a process/commit-granularity slip, documented here for the record.
- [x] 1.11 Loop 1 report — see commit log below and final report at end of session.

## Loop 2 — Transport Engine
- [x] 2.1 Schema/model (flat fields, core/optional) — backend/app/features/ocr/extraction.py: CORE_FIELDS (11) + OPTIONAL_FIELDS (16) = 26 camelCase fields, empty string when absent
- [x] 2.2 Preprocessing (watermark, two-copy slip) — crop_left_copy() detects+crops the two-copy slip (confirmed file: "WhatsApp Image 2026-11-10 at 22.01.34 (3).jpeg"), red-ink-page branch for Baba watermark (partial improvement, residual watermark noise remains — deterministic limit, documented)
- [x] 2.3 Extraction (prompt, post-processing) — transport_receipt.j2 prompt (both operator layouts), GSTIN/phone/amount shape validation + confusion-map correction in extraction.py
- [x] 2.4 Confidence / needs-review — *NeedsReview flags (date, receiptNumber, 3x GSTIN, 2x phone), *AutoCorrected flags (date + 8 amount fields)
- [x] 2.5 Warnings (items 1-7) — backend/app/features/documents/warnings.py: compute_warnings() pure function + words_to_number() Indian-English amount parser, 8 unit tests
- [x] 2.6 Duplicate warning (item 8) — backend/app/features/documents/duplicate.py: check_duplicate/refresh_duplicate_flag, wired into pipeline.py success path + correction endpoint, 6 unit tests
- [x] 2.7 Upload API (single + bulk 5) — MAX_BULK_FILES=5, MAX_DOWNLOAD_ALL_IDS=30, PDF must be exactly 1 page, documentType removed from upload forms entirely
- [x] 2.8 Frontend pages (review/list/details/downloads/dashboard/activity/help) — shared frontend/src/utils/receiptFields.js field-list constant used across DocumentDetailPage/UploadPage/DocumentsViewAllPage/MyActivityPage; needs-review filter added to DocumentsPage
- [x] 2.9 Admin pages updated for new fields — flat FIELDS list in AdminDocumentsPage, documentsByType chart removed, stale Excel/workbook text cleaned up
- [ ] 2.10 Live check 5 receipts + Loop 2 report

## Loop 3 — Proof and Polish
- [ ] 3.1 Ground truth (spec/ground_truth.json)
- [ ] 3.2 Scoring script (spec/score.py) + unit tests
- [ ] 3.3 Run A (one-by-one) + Run B (bulk 5) -> spec/results.csv
- [ ] 3.4 Accuracy report (spec/accuracy_report.md)
- [ ] 3.5 Fix loop (max 3 rounds)
- [ ] 3.6 Unseen-receipt sanity check (3 receipts)
- [ ] 3.7 Final hardening verification
- [ ] 3.8 Docs/scripts rewrite + README
- [ ] 3.9 Cleanup (zz_tr_ users, git status clean, push)

## Commit log
(hash — message — one-line result, appended as features land)
- d612416 — bootstrap Transport OCR Model from ACKN base — copy + identity rename (DB/ports/titles/keys), .gitignore fixed
- 629b1d1 — fix origin defaults to 3000/4000 — backend/.env written with real secrets, venv+npm installs verified, backend boots on :2000 (Mongo connected, 7 Groq keys loaded), frontend+admin build clean, pushed to origin/master
- c63464c — remove Excel feature completely (backend/frontend/admin) — workbook routes, export-history, Save/bulk-save UI, openpyxl dep, dashboard widgets all gone; known test fallout listed above for 1.10
- 95de921 — remove approval flow + Google sign-in — signup auto-logs-in active user now; Approvals/RejectReasonModal/ApprovedWelcomeDialog/GoogleSignInButton deleted; known test fallout listed above for 1.10
- fa1be9a — drop scripts not needed for Transport — find_duplicate_workbooks, strip_confidence, reset_database + tests removed
- 3209e26 — port hardening fixes from CONSIGNOR MODEL — login over-long-email 401, rate-limit key test, chat clear-all lock fix, opt-in pins test. 39 passed, 1 skipped.
