# Accuracy Report — Round 0 (before fixes)

Scored against `spec/ground_truth.json` (18 unique receipts, 20 files) using `spec/score.py`.
Strict = exact after trimming/case. Lenient = punctuation/spacing-insensitive, OCR digit/letter
confusion swaps on numeric-ish fields, date-format-agnostic. Only fields where the ground truth
is non-blank are counted (a correctly-blank prediction contributes no signal).

**Honest summary: these numbers are not good.** Round 0 exists to show the real starting point
before any fix round, not to flatter the engine. See "What went wrong" below for root causes
found during this round — they are addressed in the fix loop (3.5).

## Overall

| Run | Strict | Lenient |
|---|---|---|
| A (one-by-one) | 109/312 = 34.9% | 122/312 = 39.1% |
| B (bulk of 5) | 105/312 = 33.7% | 118/312 = 37.8% |

## Core vs optional

| Run | Core strict | Core lenient | Optional strict | Optional lenient |
|---|---|---|---|---|
| A | 68/213 = 31.9% | 68/213 = 31.9% | 41/99 = 41.4% | 54/99 = 54.5% |
| B | 67/213 = 31.5% | 67/213 = 31.5% | 38/99 = 38.4% | 51/99 = 51.5% |

## Worst 5 fields (Run A, by lenient %)

| Field | Lenient % | Strict % | n |
|---|---|---|---|
| operator_gstin | 0.0% | 0.0% | 16 |
| delivery_charge | 0.0% | 0.0% | 1 |
| demurrage | 0.0% | 0.0% | 1 |
| time | 66.7% | 0.0% | 6 |
| delivery_address | 80.0% | 0.0% | 5 |

(delivery_charge/demurrage have n=1 - only the single "186,798" Fright/Delivery/Demarage
receipt has these fields non-blank, so this is not yet a reliable signal either way.)

## Per-field accuracy (Run A, lenient %, sorted worst to best)

| Field | n | Lenient % |
|---|---|---|
| operator_gstin | 16 | 0.0% |
| delivery_charge | 1 | 0.0% |
| demurrage | 1 | 0.0% |
| package_description | 20 | 25.0% |
| consignee_name | 20 | 20.0% |
| package_count | 20 | 20.0% |
| prepared_by | 17 | 23.5% |
| date | 20 | 25.0% |
| consignor_name | 20 | 25.0% |
| consignee_phone | 19 | 26.3% |
| consignor_phone | 13 | 30.8% |
| total_amount | 20 | 30.0% |
| time | 6 | 66.7% |
| payment_mode | 20 | 45.0% |
| operator_name | 20 | 50.0% |
| receipt_number | 20 | 50.0% |
| to_place | 20 | 55.0% |
| from_place | 4 | 75.0% |
| freight | 5 | 80.0% |
| delivery_address | 5 | 80.0% |
| remark | 1 | 100.0% |
| consignor_gstin | 4 | 100.0% |
| consignee_gstin | 4 | 100.0% |
| sgst | 4 | 100.0% |
| cgst | 4 | 100.0% |
| igst | 4 | 100.0% |
| amount_in_words | 4 | 100.0% (A) / 50.0% (B) |

## What went wrong (root causes, to fix in 3.5)

1. **`operator_gstin` is blank on every single one of 40 extractions (0%).** Inspected the raw
   output directly: every document, including clean Pawan receipts (where it's correctly blank
   in the ground truth too) AND Baba receipts (where "GST No. - 23AHQPS8492M1ZA" is clearly
   printed at the bottom of every Baba receipt). The model is not picking it up at all, even
   though it's unambiguous (Baba receipts print exactly one GST number on the whole page). This
   is a prompt-clarity problem: the current instruction says "the OPERATOR's own 15-character GST
   number (not the consignor's or consignee's)" without telling the model that on Baba receipts
   this is simply the *only* GST number present, with no explicit "Operator GST" label to latch
   onto. Fix candidate: clarify the prompt.

2. **Watermark text is leaking into unrelated fields on Baba receipts (the residual-noise limit
   already flagged honestly in step 2.2).** Example found in Run A's raw output for the Baba
   watermark receipt P98506: `consignor_name = "SBAEATRAVELS"` (a corrupted fragment of the
   repeated "BABA TRAVELS" watermark), `total_amount = "1000000"` (nonsense; truth is "200"),
   `from_place = "RABATN"` (watermark noise), `operator_name` blank (the real operator name got
   lost to the same noise). This explains much of the poor consignor_name/consignee_name/
   total_amount/date accuracy on Baba documents. Preprocessing (2.2) already reduced but did not
   eliminate watermark noise in the OCR text; the AI step needs an explicit instruction to
   recognize and discard repeated "BABA TRAVELS"-shaped noise rather than treating it as a field
   value.

3. **`package_count`/`package_description` splitting is unreliable.** Many Baba receipts show
   "Detail : N Parcel" as one OCR line; the model is not consistently splitting this into a
   numeric `packageCount` and a text `packageDescription`.

4. **`consignee_name` accuracy (20%) is partly a ground-truth mapping choice worth re-checking in
   the fix round**, not just an extraction bug: Baba's receiver name sits in a "To" field right
   below "Receiver's Detail", and OCR/watermark noise around that specific line may be worse than
   elsewhere on the page.

Items 1-3 are addressed in the Round 1 fix pass. Item 4 is noted for the fix-loop investigation,
not assumed to be ground-truth error without checking the actual OCR text first.

## Every mismatch (lenient), Run A

See `spec/mismatches_run_a.csv` for the full list of 190 mismatches (file, field, truth, ocr) -
kept alongside this report as the detailed evidence for the summary above.

## Every mismatch (lenient), Run B

See `spec/mismatches_run_b.csv` for the full list of 194 mismatches.
