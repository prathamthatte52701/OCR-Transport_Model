# Transport OCR

**Transport receipt document intelligence.** Upload a bus luggage/parcel receipt (photo or PDF,
page 1 only), and Transport OCR reads the receipt fields for you and lets you check and correct
them — operator, receipt number, date, route, consignor/consignee, packages, and money fields.

It's a Windows desktop-style tool built for one office PC: private per-user accounts (active
immediately on signup, no approval step), an admin panel for support and oversight, and a
built-in chat between users and admins. The app itself runs only on that PC and is not published
on the internet. Two online services are used: MongoDB Atlas stores the data, and Groq receives
the page's OCR text to extract the fields (never the image itself).

## At a glance

**Upload** a receipt → **check** the extracted fields beside the original photo → **edit** if
anything's wrong, with full correction history.

- Single upload, or bulk up to 5 receipts per request
- Review page with the original photo always in view, per-field edit + correction history
- Warnings for anything that looks unusual (missing/implausible date, GSTIN format, amount
  mismatches, possible duplicate) — never blocks, just flags
- Documents list: search by receipt number/operator/consignor/consignee, filter by date range,
  status, needs-review
- A built-in chat between each user and the admins

## Contents

- [Field list](#field-list)
- [Warnings](#warnings)
- [Accuracy](#accuracy)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Ports](#ports)
- [Maintenance scripts](#maintenance-scripts)
- [Backups](#backups)
- [Logs](#logs)
- [Security notes](#security-notes)

## Field list

27 fields, flat (no nested objects), empty string when a field isn't printed on the receipt.

**Core** (shown on the review page even when blank): operator name, operator GSTIN, receipt
number, date, destination place, consignee name, consignor name, package count, payment mode,
total amount, prepared by.

**Optional** (hidden when blank): time, origin place, delivery address, consignor GSTIN/phone,
consignee GSTIN/phone, package description, freight, delivery charge, demurrage, SGST, CGST,
IGST, amount in words, remark.

## Warnings

Shown on the review page as a position + a short reason, never blocking:

1. Receipt number missing
2. Date missing or implausible (more than 1 day in the future, or more than 5 years in the past)
3. Total amount missing
4. A GSTIN that's present doesn't match the standard 15-character format
5. Total doesn't match freight + delivery charge + demurrage (only when those are present)
6. Total doesn't match the amount written in words (only when amount-in-words is present)
7. A receipt number, consignor phone, or consignee phone looks incomplete (shape check)
8. Possible duplicate: another document with the same operator + receipt number + date already
   exists for this user

## Accuracy

Measured against 18 unique hand-verified receipts (`spec/ground_truth.json`), scored two ways:
strict (exact match after trimming/case) and lenient (ignores punctuation/spacing, common OCR
digit/letter confusions on numeric fields, date-format differences). Full breakdown, every
mismatch, and the fixes applied are in `spec/accuracy_report.md` — these numbers are copied from
there exactly, not rounded up.

| | Overall strict | Overall lenient | Core strict | Core lenient | Optional strict | Optional lenient |
|---|---|---|---|---|---|---|
| Run A (one-by-one) | 52.2% | 56.4% | 49.3% | 49.3% | 58.6% | 71.7% |
| Run B (bulk of 5) | 56.7% | 60.9% | 53.1% | 53.1% | 64.6% | 77.8% |

**Honest assessment**: this is a working engine, not a finished one. The single biggest fix
applied during development (see the accuracy report) was disabling a photo-preprocessing step
that was destroying OCR quality on Baba Travels receipts rather than improving it — fixing that
alone roughly doubled core accuracy. Remaining weak spots: `date` and `receipt_number` on some
Baba Travels photos, traced to a genuine PaddleOCR text-detection miss on certain header lines
(verified not a preprocessing artifact), and the two-copy slip layout, which still extracts
mostly blank due to overprint and residual watermark noise. Neither is fixable with a per-image
hack without risking overfitting to this specific test set.

## Quick start

```bash
# Backend
cd backend
py -3.12 -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env      # fill MONGO_URI, GROQ_API_KEYS, JWT_SECRET, ADMIN_1_*/ADMIN_2_*
venv\Scripts\python.exe -m app.scripts.seed_admin
venv\Scripts\python.exe -m uvicorn app.main:app --port 2000

# Frontend (new terminal)
cd frontend && npm install && npm run dev

# Admin (new terminal)
cd admin && npm install && npm run dev
```

Or use the bat scripts from the repo root: `setup.bat` (one-time: venv, deps, both `npm
install`s), `start.bat` (starts all three in titled windows, PID files in `.run/`), `stop.bat`
(stops all three cleanly by PID).

Sign up at the frontend URL below — accounts are active immediately. Sign in to admin with the
identity set in `ADMIN_1_EMAIL`/`ADMIN_1_PASSWORD`.

## Configuration

All backend config lives in `backend/.env` (never committed — see `.env.example` for the names
only, no real values). Required: `MONGO_URI`, `JWT_SECRET` (32+ chars). Optional: `GROQ_API_KEYS`
(comma-separated, round-robined on failure), `GROQ_MODEL`, `GROQ_REASONING_EFFORT` (default
`low`), `GROQ_MAX_TOKENS` (default 3000, ceiling 8000), `MONGO_DB_NAME` (default
`docintel_transport`), `FRONTEND_ORIGIN`/`ADMIN_ORIGIN`, `ADMIN_1_NAME`/`ADMIN_1_EMAIL`/
`ADMIN_1_PASSWORD` and the same for `ADMIN_2_*` (seed-only, used once by `seed_admin`, then only
the bcrypt hash persists), `ENABLE_DOCS` (exposes `/docs`/`/redoc`, off by default everywhere).

## Ports

| App | Port |
|---|---|
| Backend (FastAPI) | 2000 |
| Frontend (user app) | 3000 |
| Admin app | 4000 |

## Maintenance scripts

Run from `backend/` with the venv active.

| Script | What it does |
|---|---|
| `app.scripts.seed_admin` | Idempotent - seeds the two admin accounts from `.env`. |
| `app.scripts.reset_admin_password` | Sets a temporary password for an admin account. |
| `app.scripts.wipe_all_except_admins --db <name>` | Dry-run by default; `--apply --i-have-a-backup` wipes every non-admin user and all their data. `--db` must equal the configured `MONGO_DB_NAME`, no exceptions. |
| `app.scripts.cleanup_orphan_corrections --db <name>` | Dry-run by default; `--apply` removes correction-history rows whose document no longer exists. |

Admin panel also has: purge a user's documents by month or date range, delete a single user,
a global nuke (typed confirmation + password), global chat delete, and an orphaned-files list
with retry.

## Backups

This app has no built-in backup job. Before running any destructive maintenance script, take a
manual MongoDB dump:

```bash
mongodump --uri="<your MONGO_URI>" --db=docintel_transport --out=./backup-YYYY-MM-DD
```

## Logs

Backend logs to stdout (and `backend/logs/` when redirected by `start.bat`). No document image
or OCR text is ever written to a log line — only field names, status codes, and error classes.

## Security notes

- Every document/chat query is scoped to the owning user's id; cross-user access 404s (never
  leaks existence via a different status code).
- Admin access to another user's data is audit-logged (who, what, when).
- JWT + `tokenVersion` revocation: changing or resetting a password invalidates every other
  issued token immediately, not just on expiry.
- Signup and login are both rate-limited per IP; login additionally rate-limits per email.
- `.env`, `venv/`, `node_modules/`, `.run/`, logs, and `testing data/` are all git-ignored. Only
  `.env.example` (names, no values) is committed.
- No secrets, no real document data, and no personal identifiers have been committed to this
  repository's git history (checked directly, not assumed).
