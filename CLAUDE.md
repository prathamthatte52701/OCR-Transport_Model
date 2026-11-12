# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

Transport OCR — reads bus luggage/parcel receipts (photo or PDF page 1) from two operators
(Pawan Travels, Baba Travels) and extracts a flat 26-field schema (operator, receipt number,
date, consignor/consignee, packages, money fields). Per-user auth, manual field correction with
history, bulk upload (up to 5), admin panel with cross-user CRUD + telemetry. Forked from
"ACKN OCR Model" (a Tax Invoice/Delivery Challan extractor) — same stack and architecture,
different document type and field schema. See `spec/TRANSPORT_SPEC.md` for the full product spec
and `LOOP_LOG.md` for what's been built so far.

## Commands

### Backend

```bash
cd backend
./venv/Scripts/activate                                     # Windows
pip install -r requirements-dev.txt
cp .env.example .env                                         # fill MONGO_URI, GROQ_API_KEYS, JWT_SECRET, etc.

./venv/Scripts/python.exe -m uvicorn app.main:app --port 2000 --reload
./venv/Scripts/python.exe -m app.scripts.seed_admin           # idempotent, seeds 2 admin accounts
```

Tests: `pytest app` from `backend/`. `conftest.py` forces a `_test`-suffixed database and a
test-only `JWT_SECRET` before settings load, and aborts if the DB name doesn't end in `_test`.
Provides `db`, `client` (ASGI, no server), `make_user` fixtures. **Run only the tests for
modules you touched plus `app/core` and auth once** — do not run the full suite on every change
(it's slow against the real test database). OCR tests specifically: run 2-5 at a time, never
the whole `app/features/ocr` folder.

### Frontend / Admin

```bash
cd frontend && npm install && npm run dev     # http://localhost:3000
cd admin && npm install && npm run dev        # http://localhost:4000
npm run build
```

Both proxy `/api` to the backend on port 2000 (see each app's `vite.config.js`).

## Required env vars (`backend/.env`)

`MONGO_URI` and `JWT_SECRET` (>=32 chars) required, app exits at import time if missing.
`GROQ_API_KEYS` (comma-separated, round-robined on failure). `GROQ_REASONING_EFFORT` defaults
to `low` and `GROQ_MAX_TOKENS` to 3000 (ceiling 8000) — deliberately low-reasoning/high-token,
tuned for a 26-field JSON answer rather than deep disambiguation; don't raise reasoning effort
without checking token budget math first (reasoning tokens draw from the same budget as the
answer). `ADMIN_1_*`/`ADMIN_2_*` seed-only admin identities.

## Architecture

### Field schema (the core thing that differs from ACKN)

Single source of truth: `backend/app/features/ocr/extraction.py`. `CORE_FIELDS` (11, always
shown) + `OPTIONAL_FIELDS` (16, hidden when blank) = `EXTRACTION_VALUE_FIELDS`. Every value is a
plain string, empty when absent (never `None`). `EXTRACTION_FLAG_FIELDS` are the `*NeedsReview`/
`*AutoCorrected` booleans. There is only ONE document type now (`DOCUMENT_TYPE = "Transport
Receipt"`, fixed, never user-chosen) — don't reintroduce a type picker.

Frontend mirrors this in `frontend/src/utils/receiptFields.js` (`RECEIPT_FIELDS`) — keep the two
in sync if you add/remove a field. Admin's flat field list lives directly in
`AdminDocumentsPage.jsx`.

### OCR pipeline

`documents/router.py` → `ocr/pipeline.py::process_document` → `ocr/page_normalize.py` (photo
rotation fix only — paper-crop is disabled, see below) → `ocr/preprocessing.py` (full-page
quality-gated cleanup) → `ocr/paddle_runner.py::run_ocr` → `ocr/ai_extraction.py::extract_header`
(Groq, single prompt `prompts/transport_receipt.j2` covers both operator layouts) →
`ocr/extraction.py` (pure-Python post-processing: confusion-map correction on numeric fields,
GSTIN/phone shape flags, a packageCount/packageDescription split fallback).

**OCRs the FULL page**, not a header crop (unlike ACKN) — `crop_header()` is a pass-through at
`FULL_PAGE_RATIO = 1.0`. Receipt fields (operator, route, parties, money) run edge to edge.

**`page_normalize.py`'s paper-crop/warp step (`find_paper`/`_warp_to_page`) is deliberately
disabled** - read the long comment in `normalize_photo()` before re-enabling it. It was built for
ACKN's header-crop-only pipeline (a wrong guess there just missed the header); measured on a real
Baba Travels photo, it was cutting away real content under full-page OCR (verified: identical
OCR with zero preprocessing read every label cleanly; the warped-and-cropped version read almost
nothing). Only rotation-fix (upside-down/sideways detection) remains active.

**A single process-wide OCR lock** serializes every OCR call (one job at a time) — bulk uploads
process strictly sequentially, by design, same as ACKN.

**Known OCR limit, not a bug**: PaddleOCR's text *detection* model sometimes produces no bounding
box at all for a specific header line on some Baba Travels photos (verified not a preprocessing
artifact — identical with zero preprocessing; tested raising `text_det_limit_side_len` to 3200
with no improvement). This explains most of the remaining `date`/`receipt_number` misses on hard
photos. Don't chase this with per-image hacks.

### Warnings and duplicate detection

`documents/warnings.py::compute_warnings()` — pure function, recomputed on every read (never
stored), covers spec section 7 items 1-7 including an Indian-English amount-in-words parser.
`documents/duplicate.py` — same operator+receiptNumber+date duplicate check, computed once at
processing time and on relevant-field correction, stored as `isDuplicate` (warn only, never
blocks).

### Frontend/Admin

Same stack as ACKN (React Router v7, TanStack Query, Zustand). No UI restyle policy is still in
effect for this phase — only field/text changes, same look.

## Known gotchas

- **Bytecode cache can serve stale code after editing a `.py` file during a dev session** — if a
  fix doesn't seem to take effect after a backend restart, clear `__pycache__` directories
  first (`find app -name __pycache__ -exec rm -rf {} +`) before assuming the bug is elsewhere.
  This cost real debugging time once already.
- **Jinja prompt templates auto-reload** (`FileSystemLoader` default), so editing
  `prompts/transport_receipt.j2` takes effect on the next request without a restart. Python code
  changes (extraction.py, pipeline.py, preprocessing.py, page_normalize.py) need a backend
  restart.
- Local-only app, one Windows PC, no hosted deployment.
- `backend/requirements.txt` has a `--extra-index-url` pin for paddlepaddle's CPU wheels — don't
  remove it.
