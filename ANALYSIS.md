# Pivot Analysis — ACKN OCR Model → Transport OCR Model

Source read directly: `E:\ACKN OCR model` (backend/frontend/admin, read-only reference) and,
for a few hardening fixes, `E:\CONSIGNOR MODEL` (read-only reference). Full requirements in
`spec/TRANSPORT_SPEC.md`; build order and progress in `LOOP_LOG.md`.

## What stayed the same

Stack, architecture, auth model (JWT + tokenVersion revocation), per-user data isolation
convention, OCR pipeline shape (preprocess → PaddleOCR → Groq extraction → deterministic
post-processing), chat feature, admin panel shape, correction-history mechanism, no-UI-restyle
policy.

## What changed

- **Document type**: ACKN's two types (Tax Invoice, Delivery Challan) with 2-4 extracted fields
  each → Transport's single type (a bus luggage/parcel receipt) with a flat 27-field schema
  covering two different operator layouts (Pawan Travels, Baba Travels). See
  `backend/app/features/ocr/extraction.py` for the field list.
- **OCR scope**: ACKN OCRs only the top ~30% header crop. Transport OCRs the FULL page, since
  receipt fields (operator, route, consignor/consignee, money table, signature) run edge to
  edge. `crop_header()` is now a pass-through.
- **Removed entirely**: Excel export/workbooks, the admin-approval signup gate (signup is
  active immediately now), Google sign-in, the "Save" step (a document is final once OCR
  finishes).
- **Added**: a warnings mechanism (`documents/warnings.py`) and a duplicate-receipt check
  (`documents/duplicate.py`) — neither existed in ACKN, which had no per-field warning concept
  beyond a boolean needs-review flag.
- **Identity**: DB `docintel_transport`, ports 2000/3000/4000 (was 8000/5174/5175).

## Real bugs found and fixed during the port (not pre-existing, specific to this port)

Documented in full in `spec/accuracy_report.md`. The big one: `page_normalize.py`'s paper-crop
step, safe under ACKN's header-crop-only pipeline, was measurably destroying OCR quality once
the pipeline switched to full-page OCR — disabled for Transport.
