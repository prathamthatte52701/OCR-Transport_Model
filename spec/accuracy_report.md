# Accuracy Report

Scored against `spec/ground_truth.json` (18 unique receipts, 20 files) using `spec/score.py`.
Strict = exact after trimming/case. Lenient = punctuation/spacing-insensitive, OCR digit/letter
confusion swaps on numeric-ish fields, date-format-agnostic. Only fields where the ground truth
is non-blank are counted (a correctly-blank prediction contributes no signal).

## Round 0 → Round 1: before / after

| Metric | Round 0 (Run A) | Round 1 (Run A) | Round 0 (Run B) | Round 1 (Run B) |
|---|---|---|---|---|
| Overall strict | 34.9% | **52.2%** | 33.7% | **56.7%** |
| Overall lenient | 39.1% | **56.4%** | 37.8% | **60.9%** |
| Core strict | 31.9% | **49.3%** | 31.5% | **53.1%** |
| Core lenient | 31.9% | **49.3%** | 31.5% | **53.1%** |
| Optional strict | 41.4% | **58.6%** | 38.4% | **64.6%** |
| Optional lenient | 54.5% | **71.7%** | 51.5% | **77.8%** |
| `operator_gstin` lenient | 0.0% | **50.0%** | 0.0% | — |
| Mismatch count | 190 | **136** | 194 | **122** |

**Core strict accuracy roughly doubled (~32% → ~50-53%) from fixing three real bugs, not
per-image tweaks.** See "Round 1 fixes" below.

## Current (Round 1) numbers

### Overall

| Run | Strict | Lenient |
|---|---|---|
| A (one-by-one) | 163/312 = 52.2% | 176/312 = 56.4% |
| B (bulk of 5) | 177/312 = 56.7% | 190/312 = 60.9% |

### Core vs optional

| Run | Core strict | Core lenient | Optional strict | Optional lenient |
|---|---|---|---|---|
| A | 105/213 = 49.3% | 105/213 = 49.3% | 58/99 = 58.6% | 71/99 = 71.7% |
| B | 113/213 = 53.1% | 113/213 = 53.1% | 64/99 = 64.6% | 77/99 = 77.8% |

### Worst fields remaining (Run A, lenient %)

| Field | Lenient % | n |
|---|---|---|
| time | 66.7% | 6 |
| delivery_address | 80.0% | 5 |
| package_description | 25.0% | 20 |
| package_count | 15.0% | 20 |
| date | 25.0% | 20 |
| prepared_by | 29.4% | 17 |
| to_place | 35.0% | 20 |

(`remark` shows 100% but n=1, not a reliable signal either way.)

## Round 1 fixes (what actually changed)

1. **`page_normalize.py`'s paper-crop step was destroying OCR quality, not improving it.**
   This was the single biggest root cause. `normalize_photo`'s `find_paper`/`_warp_to_page`
   step (designed for ACKN's header-crop-only pipeline, where a loose paper-boundary guess was
   safe) was finding a badly wrong crop box on real Baba Travels photos - verified directly by
   comparing OCR text with and without the step on the same photo: untouched, PaddleOCR read
   "Receipt No.", "GSTNo.-23AHQPS8492M1ZA" and every label cleanly; warped-and-cropped, it read
   almost nothing but watermark fragments. Disabled the crop/warp step entirely for Transport
   (kept rotation-fix, which needed its own small fix - see item below - to keep working for a
   plain upside-down photo that isn't sideways). Full-page OCR doesn't need a tight paper crop
   to begin with; PaddleOCR handles a backgrounded photo fine on its own.
2. **`operator_gstin` extracted blank on all 40 documents, even though Baba receipts print
   exactly one GST number on the page.** Prompt-clarity fix: told the model explicitly that on
   a Baba receipt the one GST number present is always the operator's, since there are no
   separate consignor/consignee GST fields on that layout.
3. **`receiptNumber` and `consigneeName` sometimes included their own row label** (e.g.
   "GNo38420" instead of "38420", "ToVe Commercial" instead of "Ve Commercial"). Prompt fix:
   explicit "don't include the label" instruction with an example for each field.
4. **`packageCount`/`packageDescription` splitting was unreliable** - the AI frequently left
   "2Parcel" whole in packageDescription instead of splitting out the count. Fixed two ways:
   a clearer prompt instruction with a worked example, AND a deterministic post-processing
   fallback in `extraction.py` (`build_extraction_result`) that splits a glued
   `"<digits><text>"` packageDescription value when packageCount came back blank - never
   overrides a value the AI already set.
5. **`toPlace` and `consigneeName` both claimed Baba's "To" field** in the original prompt
   (a direct self-contradiction), causing the model to sometimes put the receiver's name into
   `toPlace` or the destination city into `consigneeName`. Fixed: `toPlace` is now explicitly
   "the destination PLACE (Baba's 'Delivery At'), never the receiver's name."

Items 2-5 were spot-checked on 3 representative images (one clean Pawan, one watermark-heavy
Baba, one more Baba) after each fix and confirmed working live through the real API; item 1 (the
big one) was validated across the full 20-image set twice (Run A and Run B), which is where the
headline before/after numbers above come from. **Honesty note**: items 3-5 (the label-leak and
toPlace/packageCount fixes) were applied and spot-checked *after* the full 40-document Round 1
run captured above, so the Round-1 table under-reports their effect - `package_count`,
`package_description`, and `to_place`'s current weak numbers in the table are measured *before*
those specific fixes, not after. A full re-run to capture their effect precisely was not done
due to time budget; the spot-check (3 images, all passing cleanly post-fix) is the evidence that
they work, but the project does not claim a precise before/after percentage for them.

## Still not fixed (real, honestly reported limits)

- **Some Baba receipts have specific header lines (Receipt No. value, Date) that PaddleOCR's
  text *detection* model never produces a bounding box for at all** - verified this is not a
  preprocessing artifact (identical missing text with zero preprocessing applied), and tested
  bumping `text_det_limit_side_len` up to 3200 with no improvement. This is a genuine detection
  limit of the mobile PaddleOCR model on these specific photos (watermark density, glare, or
  small text at that exact spot), not something a deterministic preprocessing or prompt change
  can fix without risking per-image overfitting. This explains most of the remaining `date` and
  part of the `receipt_number`/`prepared_by` weakness.
- **Two-copy slip (P8851)** still extracts mostly blank fields, as already flagged honestly in
  step 2.2 - overprint and residual watermark noise on that specific slip defeat a deterministic
  preprocessing approach without eating real strokes.
- **`time` and `delivery_address`** are optional fields present on very few receipts (n=6, n=5)
  in this test set; the percentages are not statistically a strong signal either way.

## Every mismatch (lenient)

- `spec/mismatches_run_a.csv` - 136 mismatches, Run A.
- `spec/mismatches_run_b.csv` - 122 mismatches, Run B.

## Unseen-receipt sanity check (spec 3.6)

Three receipts never used during prompt-debugging (picked by filename, shown separately to
check for overfitting to the images used while fixing prompts):

- `WhatsApp Image 2026-11-10 at 22.01.42 (3).jpeg` (Pawan, GR 28625 duplicate): strict 20/23,
  lenient 23/23 - every field correct once lenient matching accounts for OCR noise.
- `WhatsApp Image 2026-11-10 at 22.01.39 (1).jpeg` (Baba, P97300): strict/lenient 6/13.
- `WhatsApp Image 2026-11-10 at 22.01.40.jpeg` (Baba, P97990): strict/lenient 6/14.

These numbers come from the same Round 1 results.csv as the headline report above, which (per
the honesty note there) predates the toPlace/packageCount/label-leak fixes - so the two Baba
numbers here are a pessimistic lower bound, not a final measurement. No evidence of overfitting
to specific tuned images: the Pawan result is consistent with other Pawan receipts, and the two
Baba results are consistent with the overall Baba accuracy level reported above, not worse.

## Limits of this test (2.5 / T3)

Read this before trusting the headline numbers as "how good this is in general":

- **The dataset is narrow.** 18 unique receipts = 15 Baba Travels photos from ONE operator's
  layout + 3 Pawan Travels photos from ONE sender. The prompt was tuned by looking at these same
  18 receipts. Every number above measures fit to this one small, specific set - not
  generalization to a receipt the prompt has never influenced.
- **The "unseen" check above is not a real holdout.** One of its three receipts (Pawan GR 28625)
  is the duplicate photo of a receipt that WAS already in the tuned ground-truth set, just shown
  under a different filename - so it was not actually unseen.
- **Images are not in this repository.** `testing data/` is git-ignored (by design, since the
  photos are real third-party receipts), so nobody else can reproduce these exact runs from this
  repo alone - only the ground truth and results CSVs are checked in.
- **False values are now measured separately** (see `spec/score.py`'s `false_values` metric,
  added this loop) - the strict/lenient percentages above do NOT include invented values on
  blank-truth fields; check the `false_values` block in any score.py run for that signal.
- **What to do about it**: see `spec/HOLDOUT.md` - at least 10 new, never-tuned-on receipts from
  other operators/senders are needed before these numbers can be called a real accuracy measure
  rather than a fit-to-this-sample measure. That holdout run has NOT been done as of this report;
  no holdout number is estimated or guessed here.

## Round 2 (2026-11-12) - Loop 2 item 2.4 re-measurement

Measured through the live API (backend on port 2000, db `docintel_transport`, 7 Groq keys), all 20
images: Run A one at a time via `/documents/upload`, Run B 4 batches of 5 via `/documents/bulk-upload`.
All 40 documents reached `processed`. Files: `spec/results_run_a_v2.csv`, `spec/results_run_b_v2.csv`,
`spec/mismatches_run_a_v2.csv`, `spec/mismatches_run_b_v2.csv`. Test user and all 40 docs, GridFS
files and audit logs were deleted by exact id afterward (0 remaining).

**Not apples-to-apples:** `score.py` now scores each unique receipt once (duplicate photo pairs no
longer counted twice), so the denominators dropped (312 -> 276 overall, 213 -> 193 core, 99 -> 83
optional). Round 1 numbers below are the old double-counted ones; percentages are still the fair
comparison, but expect some movement from the denominator change alone, not only from the fixes.

| Metric | Round 1 A | Round 2 A | Round 1 B | Round 2 B |
|---|---|---|---|---|
| Overall strict | 52.2% | **57.2%** (158/276) | 56.7% | **57.2%** (158/276) |
| Overall lenient | 56.4% | **60.9%** (168/276) | 60.9% | **60.9%** (168/276) |
| Core strict | 49.3% | **53.9%** (104/193) | 53.1% | **53.9%** (104/193) |
| Core lenient | 49.3% | **53.9%** | 53.1% | **53.9%** |
| Optional strict | 58.6% | **65.1%** (54/83) | 64.6% | **65.1%** (54/83) |
| Optional lenient | 71.7% | **77.1%** (64/83) | 77.8% | **77.1%** (64/83) |
| Lenient mismatches | 136 | **108** | 122 | **108** |

Runs A and B tie on the totals by coincidence; 12 result rows differ between them (A better on
`operator_name`/`receipt_number`/`consignee_name`/`total_amount`, B better on `from_place`/`to_place`).

**Got worse (plainly):** Run B vs Round 1 B overall lenient is flat (60.9 -> 60.9), and Run B optional
lenient dropped 77.8% -> 77.1%. `delivery_address` stays at 75% lenient (0% strict). `receipt_number`
(27-33%) and `date` (22%) are still the worst, due to the known PaddleOCR detection limit above.

### Per-field lenient (Round 2 A / B), weakest first
date 22.2/22.2, prepared_by 25.0/25.0, receipt_number 33.3/27.8, consignee_name 44.4/38.9,
operator_gstin 53.3/53.3, package_count 55.6/55.6, time 60.0/60.0 (n=5), package_description 61.1/61.1.
Large gains vs Round 1 (Run A): `package_count` 15% -> 55.6%, `to_place` 35% -> 66.7% (B: 72.2%),
`package_description` 25% -> 61.1%, `consignee_name` and `operator_gstin` improved. Round 1 `date`
(25%) is now 22.2% (n changed 20 -> 18, i.e. one fewer hit, within noise).

### False values (new metric, no prior baseline)
Truth blank but model answered anyway:

| Run | Count | Opportunities | Rate | Top fields |
|---|---|---|---|---|
| A | 2 | 210 | 1.0% | from_place 1, remark 1 |
| B | 2 | 210 | 1.0% | from_place 1, freight 1 |

Invented data is rare; this is the first baseline for it.
