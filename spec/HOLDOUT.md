# Holdout receipts needed (T3)

The accuracy numbers in `spec/accuracy_report.md` are measured on the 18 unique receipts in
`spec/ground_truth.json` - 15 Baba Travels receipts from one operator and 3 Pawan Travels
receipts from one sender. The prompt (`backend/app/features/ocr/prompts/transport_receipt.j2`)
was tuned by looking at these same 18 receipts. That makes every number in the report a measure
of fit to this one small, narrow set, not a measure of how the model does on a receipt it has
never influenced in any way.

An earlier "unseen receipt" check also reused one of the two already-seen duplicate photos
(Pawan GR 28625), so it was not actually testing an unseen receipt either.

## What is needed

At least **10 NEW receipts** that were:
- **Never looked at** while writing or tuning the prompt, the extraction post-processing, or the
  ground truth file.
- From **operators other than Pawan Travels and Baba Travels** where possible, and/or from
  **different senders/consignors** than the 3 Pawan receipts already in the set - the current
  set is one operator's layout times 15 photos plus one sender's layout times 3 photos; a
  genuine holdout test needs layout and handwriting variety the model hasn't seen.
- Real photos (not scans), since that's the real use case - phone camera photos with normal
  lighting/background variation, not retouched.

## How to use them

1. Add the new receipts to a SEPARATE ground-truth file (e.g. `spec/holdout_ground_truth.json`,
   same shape as `spec/ground_truth.json`), written by looking at the images ONCE, honestly, with
   no reference to current code behavior.
2. Run the existing pipeline against them exactly as-is - no prompt changes allowed afterward
   based on what the holdout run shows, or it stops being a holdout.
3. Score with `spec/score.py --ground-truth spec/holdout_ground_truth.json --results <csv>`.
4. Report the holdout numbers (strict/lenient/false-value rate) ALONGSIDE the tuned-set numbers,
   never instead of them, and be explicit that a drop between the two is expected and normal -
   that gap IS the honest measure of how well this generalizes.

No holdout result is invented or estimated anywhere in this repo. This file only states what is
needed; the report says plainly that this step has not been done yet.
