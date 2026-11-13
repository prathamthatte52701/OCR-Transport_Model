# Full OCR test: actual vs OCR

**Every number below is on the DEV SET (the same 20 images used to tune the prompt) - dev set, optimistic. None of it shows generalization.**

Code snapshot measured: `6c5a50a merge: Task D (Baba deliveryAddress prompt wording fix) into master` (master; server loaded from it, no code or prompt changes during the run). Scoring via `spec/score.py` (`score_value`, `score_document`, `aggregate`). Aggregates count each of the 18 unique receipts once; for the 2 duplicate-photo receipts the first photo by filename is scored (same rule as score.py's CLI). Per-receipt tables, mismatches, false values and diffs cover ALL 20 files. In tables, `wrong` on a blank-truth cell means a false (invented) value.

## Worst 5 fields by strict accuracy, Run A (dev set, optimistic)

| field | n | strict % | lenient % |
|---|---|---|---|
| time | 5 | 0.0 | 60.0 |
| delivery_address | 4 | 0.0 | 75.0 |
| remark | 1 | 0.0 | 100.0 |
| prepared_by | 16 | 18.8 | 18.8 |
| date | 18 | 22.2 | 22.2 |

## Worst 5 fields by strict accuracy, Run B (dev set, optimistic)

| field | n | strict % | lenient % |
|---|---|---|---|
| time | 5 | 0.0 | 60.0 |
| delivery_address | 4 | 0.0 | 75.0 |
| remark | 1 | 0.0 | 100.0 |
| date | 18 | 22.2 | 22.2 |
| prepared_by | 16 | 25.0 | 25.0 |

## Headline (dev set, optimistic)

| scope | n | Run A strict % | Run A lenient % | Run B strict % | Run B lenient % |
|---|---|---|---|---|---|
| core | 193 | 54.9 | 54.9 | 53.4 | 53.4 |
| optional | 83 | 65.1 | 77.1 | 62.7 | 74.7 |
| overall | 276 | 58.0 | 61.6 | 56.2 | 59.8 |

## a. Per-receipt tables

18 unique receipts. **Two receipts have duplicate photos (Pawan GR28625 and Baba P98506)**: each shares one ground truth across two photos, and both photos' OCR results are shown (one table per photo, same Actual column).

### pawan_gr28625 - `WhatsApp Image 2026-11-10 at 22.01.33 (1).jpeg` (duplicate-pair photo)

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | PAWAN TRAVELS | PAWAN TRAVELS | PAWAN TRAVELS | strict | strict |
| operator_gstin |  |  |  | strict | strict |
| receipt_number | 28625 | 28625 | 28625 | strict | strict |
| date | 05/03/2026 | 05/03/2026 | 05/03/2026 | strict | strict |
| to_place | PUNE | PUNE | PUNE | strict | strict |
| consignee_name | VE COMMERCIAL VEHICLES | VE COMMERCIAL VEHICLES | VE COMMERCIAL VEHICLES | strict | strict |
| consignor_name | KLINGELBERG INDIA | KLINGELBERG INDIA | KLINGELBERG INDIA | strict | strict |
| package_count | 1 | 1 | 1 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 100 | 100 | 100 | strict | strict |
| prepared_by | PAWAN | PAWAN | PAWAN | strict | strict |
| time | 11:25 AM | 11:25AM | 11:25AM | lenient | lenient |
| from_place | INDORE | INDORE | Indore | strict | strict |
| delivery_address | MAYARAM JI 8087536777 | MAYARAM JI8087536777 | MAYARAM JI8087536777 | lenient | lenient |
| consignor_gstin | 27AAECK1993K1Z3 | 27AAECK1993K1Z3 | 27AAECK1993K1Z3 | strict | strict |
| consignor_phone | 8518888766 | 8518888766 | 8518888766 | strict | strict |
| consignee_gstin | 23AABCE9378F3ZI | 23AABCE9378F3ZI | 23AABCE9378F3ZI | strict | strict |
| consignee_phone | 8518888766 | 8518888766 | 8518888766 | strict | strict |
| package_description | PARCEL - PARCEL | PARCEL-PARCEL | PARCEL-PARCEL | lenient | lenient |
| freight | 100 | 100 | 100 | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst | 0 | 0 | 0 | strict | strict |
| cgst | 0 | 0 | 0 | strict | strict |
| igst | 0 | 0 | 0 | strict | strict |
| amount_in_words | Rupees One Hundred Only | Rupees One Hundred Only | Rupees One Hundred Only | strict | strict |
| remark |  |  |  | strict | strict |

### pawan_gr28625 - `WhatsApp Image 2026-11-10 at 22.01.42 (3).jpeg` (duplicate-pair photo)

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | PAWAN TRAVELS | PAWAN TRAVELS | PAWAN TRAVELS | strict | strict |
| operator_gstin |  |  |  | strict | strict |
| receipt_number | 28625 | 28625 | 28625 | strict | strict |
| date | 05/03/2026 | 05/03/2026 | 05/03/2026 | strict | strict |
| to_place | PUNE | PUNE | PUNE | strict | strict |
| consignee_name | VE COMMERCIAL VEHICLES | VE COMMERCIAL VEHICLES | VE COMMERCIAL VEHICLES | strict | strict |
| consignor_name | KLINGELBERG INDIA | KLINGELBERG INDIA | KLINGELBERG INDIA | strict | strict |
| package_count | 1 | 1 | 1 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 100 | 100 | 100 | strict | strict |
| prepared_by | PAWAN | PAWAN | PAWAN | strict | strict |
| time | 11:25 AM | 11:25AM | 11:25AM | lenient | lenient |
| from_place | INDORE | INDORE | Indore | strict | strict |
| delivery_address | MAYARAM JI 8087536777 | MAYARAM JI8087536777 | MAYARAM JI8087536777 | lenient | lenient |
| consignor_gstin | 27AAECK1993K1Z3 | 27AAECK1993K1Z3 | 27AAECK1993K1Z3 | strict | strict |
| consignor_phone | 8518888766 | 8518888766 | 8518888766 | strict | strict |
| consignee_gstin | 23AABCE9378F3ZI | 23AABCE9378F3ZI | 23AABCE9378F3ZI | strict | strict |
| consignee_phone | 8518888766 | 8518888766 | 8518888766 | strict | strict |
| package_description | PARCEL - PARCEL | PARCEL-PARCEL | PARCEL-PARCEL | lenient | lenient |
| freight | 100 | 100 | 100 | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst | 0 | 0 | 0 | strict | strict |
| cgst | 0 | 0 | 0 | strict | strict |
| igst | 0 | 0 | 0 | strict | strict |
| amount_in_words | Rupees One Hundred Only | Rupees One Hundred Only | One Hundred Only | strict | wrong |
| remark |  |  |  | strict | strict |

### pawan_gr41468 - `WhatsApp Image 2026-11-10 at 22.01.33 (2).jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | PAWAN TRAVELS | PAWAN TRAVELS | PAWAN TRAVELS | strict | strict |
| operator_gstin |  |  |  | strict | strict |
| receipt_number | 41468 | 41468 | 41468 | strict | strict |
| date | 16/05/2026 | 16/05/2026 | 16/05/2026 | strict | strict |
| to_place | PUNE | PUNE | PUNE | strict | strict |
| consignee_name | VE COMMERCIAL VEHICLES | VE COMMERCIAL VEHICLES | VE COMMERCIAL VEHICLES | strict | strict |
| consignor_name | KLINGELBERG INDIA | KLINGELBERG INDIA | KLINGELBERG INDIA | strict | strict |
| package_count | 2 |  |  | wrong | wrong |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 200 | 200 | 200 | strict | strict |
| prepared_by | PAWAN | PAWAN | PAWAN | strict | strict |
| time | 12:45 PM | 12:45PM | 12:45PM | lenient | lenient |
| from_place | INDORE | W DORE | W DORE | wrong | wrong |
| delivery_address | MAYARAM JI 8087536777 | MAYARAMJI8087536777 | MAYARAMJI8087536777 | lenient | lenient |
| consignor_gstin | 27AAECK1993K1Z3 | 27AAECK1993K1Z3 | 27AAECK1993K1Z3 | strict | strict |
| consignor_phone | 8518888766 | 8518888766 | 8518888766 | strict | strict |
| consignee_gstin | 23AABCE9378F3ZI | 23AABCE9378F3ZI | 23AABCE9378F3ZI | strict | strict |
| consignee_phone | 8518888766 | 8518888766 | 8518888766 | strict | strict |
| package_description | PARCEL - PARCEL | PARCEL-PARCEL | PARCEL-PARCEL | lenient | lenient |
| freight | 200 |  | 200 | wrong | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst | 0 | 0 | 0 | strict | strict |
| cgst | 0 | 0 | 0 | strict | strict |
| igst | 0 | 0 | 0 | strict | strict |
| amount_in_words | Rupees Two Hundred Only | Rupees Two Hundred Only | Rupees Two Hundred Only | strict | strict |
| remark | SAED VBOX | SAEDVBOX | SAEDVBOX | lenient | lenient |

### pawan_gr38420 - `WhatsApp Image 2026-11-10 at 22.01.33.jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | PAWAN TRAVELS | PAWAN TRAVELS | PAWAN TRAVELS | strict | strict |
| operator_gstin |  |  |  | strict | strict |
| receipt_number | 38420 | 38420 | 38420 | strict | strict |
| date | 29/04/2026 | 29/04/2026 | 29/04/2026 | strict | strict |
| to_place | PUNE | PUNE | PUNE | strict | strict |
| consignee_name | VE COMMERCIAL VEHICLES | VE COMMERCIAL VEHICLES | VE COMMERCIAL VEHICLES | strict | strict |
| consignor_name | KLINGELBERG INDIA | KLINGELBERG INDIA | KLINGELBERG INDIA | strict | strict |
| package_count | 2 | 2 | 2 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 200 | 200 | 200 | strict | strict |
| prepared_by | PAWAN | PAWAN | PAWAN | strict | strict |
| time | 10:04 AM | 10:04AM | 10:04AM | lenient | lenient |
| from_place | INDORE | INDORE | INDORE | strict | strict |
| delivery_address | MAYARAM JI 8087536777 | MAYARAMJI8087536777 | MAYARAMJI8087536777 | lenient | lenient |
| consignor_gstin | 27AAECK1993K1Z3 | 27AAECK1993K1Z3 | 27AAECK1993K1Z3 | strict | strict |
| consignor_phone | 8518888766 | 8518888766 | 8518888766 | strict | strict |
| consignee_gstin | 23AABCE9378F3ZI | 23AABCE9378F3ZI | 23AABCE9378F3ZI | strict | strict |
| consignee_phone | 8518888766 | 8518888766 | 8518888766 | strict | strict |
| package_description | PARCEL - PARCEL | PARCEL-PARCEL | PARCEL-PARCEL | lenient | lenient |
| freight | 200 | 200 | 200 | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst | 0 | 0 |  | strict | wrong |
| cgst | 0 | 0 | 0 | strict | strict |
| igst | 0 | 0 | 0 | strict | strict |
| amount_in_words | Rupees Two Hundred Only | Rupees Two Hundred Only | Rupees Two Hundred Only | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p8851_twocopy - `WhatsApp Image 2026-11-10 at 22.01.34 (3).jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA |  | 23AHQP8492M1ZA | wrong | wrong |
| receipt_number | P8851 |  |  | wrong | wrong |
| date | 21/04/2026 |  | 01/04/2026 | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercial | Ve Commercial | Ve Commercial | strict | strict |
| consignor_name | Self |  |  | wrong | wrong |
| package_count | 4 |  |  | wrong | wrong |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 400.00 | 400.00 | 400.00 | strict | strict |
| prepared_by | Shresth Sharma |  | Shresth Sharma | wrong | strict |
| time | 17:17:59 |  | 17:17 | wrong | wrong |
| from_place |  |  |  | strict | strict |
| delivery_address | Veer Travels Opp Vishva Hotel Ctm Cross Road |  |  | wrong | wrong |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone | 00 |  |  | wrong | wrong |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 00 | 00 |  | strict | wrong |
| package_description | Parcel |  |  | wrong | wrong |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

### baba_186798 - `WhatsApp Image 2026-11-10 at 22.01.34.jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | strict | strict |
| receipt_number | 186,798 |  |  | wrong | wrong |
| date | 01/06/2026 |  |  | wrong | wrong |
| to_place | Indore |  |  | wrong | wrong |
| consignee_name | Ve Commercial |  |  | wrong | wrong |
| consignor_name | oerlikon, Ahmedabad |  |  | wrong | wrong |
| package_count | 14 | 14 | 14 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 140.00 | 140.00 | 140.00 | strict | strict |
| prepared_by | Devshree Vern |  |  | wrong | wrong |
| time | 10:33:06 |  |  | wrong | wrong |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone |  |  |  | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 8878424014 |  |  | wrong | wrong |
| package_description | Parcel | Parcel | Parcel | strict | strict |
| freight | 0.00 | 0.00 | 0.00 | strict | strict |
| delivery_charge | 140.00 | 140.00 | 140.00 | strict | strict |
| demurrage | 0.00 | 0.00 | 0.00 | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p98250 - `WhatsApp Image 2026-11-10 at 22.01.37 (2).jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | BABA TRAVELS | BABA TRAVELS | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | strict | strict |
| receipt_number | P98250 |  |  | wrong | wrong |
| date | 15/02/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercial | AR | AR | wrong | wrong |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 6 | 2 | 2 | wrong | wrong |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 600.00 | 600.00 | 600.00 | strict | strict |
| prepared_by | Alok Sen |  |  | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone | 0000000000 |  |  | wrong | wrong |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 0000000000 | 0000000000 | 0000000000 | strict | strict |
| package_description | Parcel |  |  | wrong | wrong |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p98506 - `WhatsApp Image 2026-11-10 at 22.01.37.jpeg` (duplicate-pair photo)

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | Baba Travels | ELSLASA TRAVELS | strict | wrong |
| operator_gstin | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | strict | strict |
| receipt_number | P98506 |  |  | wrong | wrong |
| date | 25/02/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercial | Ve Commercial | Ve Commercial | strict | strict |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 2 | 2 | 2 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 200.00 | 200.00 | 200.00 | strict | strict |
| prepared_by |  |  |  | strict | strict |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone | 0000000000 | 0000000000 | 0000000000 | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 0000000000 | 0000000000 | 0000000000 | strict | strict |
| package_description | Parcel | Parcel | Parcel | strict | strict |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  | Subject to INDORE Jurisdictlon |  | wrong | strict |

### baba_p98506 - `WhatsApp Image 2026-11-10 at 22.01.40 (1).jpeg` (duplicate-pair photo)

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | BABA TRAVELS | BABA TRAVELS | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA |  |  | wrong | wrong |
| receipt_number | P98506 | OLSHASIAVEL | OLSHASIAVEL | wrong | wrong |
| date | 25/02/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercial |  |  | wrong | wrong |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 2 | 2 | 2 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 200.00 | 200.00 | 200.00 | strict | strict |
| prepared_by |  |  |  | strict | strict |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone | 0000000000 | 0000000000 | 0000000000 | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 0000000000 |  |  | wrong | wrong |
| package_description | Parcel | Parcel | Parcel | strict | strict |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p98755 - `WhatsApp Image 2026-11-10 at 22.01.38 (1).jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS |  |  | wrong | wrong |
| operator_gstin | 23AHQPS8492M1ZA |  |  | wrong | wrong |
| receipt_number | P98755 |  |  | wrong | wrong |
| date | 06/03/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad |  |  | wrong | wrong |
| consignee_name | Orlicon Blazer |  |  | wrong | wrong |
| consignor_name | Self |  |  | wrong | wrong |
| package_count | 7 |  |  | wrong | wrong |
| payment_mode | Paid |  |  | wrong | wrong |
| total_amount | 700.00 |  |  | wrong | wrong |
| prepared_by | Nitin Kothari |  |  | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone |  |  |  | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 0000000000 |  |  | wrong | wrong |
| package_description | Parcel |  |  | wrong | wrong |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p97394 - `WhatsApp Image 2026-11-10 at 22.01.38 (2).jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS |  | Baba Travels | wrong | strict |
| operator_gstin | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | strict | strict |
| receipt_number | P97394 | P97394 | P97394 | strict | strict |
| date | 16/01/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercial | ToVe Commercial | ToVe Commercial | wrong | wrong |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 3 | 3 | 3 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 300.00 | 300.00 | 300.00 | strict | strict |
| prepared_by |  |  |  | strict | strict |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone | 000000000 | 000000000 | 000000000 | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 0000000000 | 0000000000 | 0000000000 | strict | strict |
| package_description | Parcel | Parcel | Parcel | strict | strict |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p98010 - `WhatsApp Image 2026-11-10 at 22.01.38.jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | Baba Travels | BABA TRAVELS | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA |  |  | wrong | wrong |
| receipt_number | P98010 |  |  | wrong | wrong |
| date | 08/02/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercila | Ve Commercila | ToVe Commercila | strict | wrong |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 2 | 2 | 2 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 200.00 | 200.00 | 200.00 | strict | strict |
| prepared_by | Bobby |  |  | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone | 0000000000 |  | 0000000000 | wrong | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 0000000000 | 0000000000 | 0000000000 | strict | strict |
| package_description | Parcel | Parcel | Parcel | strict | strict |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p97300 - `WhatsApp Image 2026-11-10 at 22.01.39 (1).jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA |  |  | wrong | wrong |
| receipt_number | P97300 |  |  | wrong | wrong |
| date | 13/01/2025 | 13/01/2025 | 13/01/2025 | strict | strict |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercial | Commercial |  | wrong | wrong |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 4 | 4 | 4 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 400.00 |  |  | wrong | wrong |
| prepared_by | Rahul Sharma |  |  | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone |  |  |  | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 0000000000 | 0000000000 | 0000000000 | strict | strict |
| package_description | Parcel | Parcel | Parcel | strict | strict |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p97433 - `WhatsApp Image 2026-11-10 at 22.01.39.jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | strict | strict |
| receipt_number | P97433 |  |  | wrong | wrong |
| date | 17/01/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercial | Ve Commercial | Ve Commercial | strict | strict |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 4 | 4 | 4 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 400.00 | 400.00 | 400.00 | strict | strict |
| prepared_by | Alok Sen |  |  | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone | 0000000000 | 0000000000 | 0000000000 | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 0000000000 | 0000000000 | 0000000000 | strict | strict |
| package_description | Parcel | Parcel | Parcel | strict | strict |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p98635 - `WhatsApp Image 2026-11-10 at 22.01.40 (2).jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS |  |  | wrong | wrong |
| operator_gstin | 23AHQPS8492M1ZA |  |  | wrong | wrong |
| receipt_number | P98635 |  |  | wrong | wrong |
| date | 01/03/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad |  |  | wrong | wrong |
| consignee_name | Orlicon Blazer |  |  | wrong | wrong |
| consignor_name | Self |  |  | wrong | wrong |
| package_count | 5 |  |  | wrong | wrong |
| payment_mode | Paid |  |  | wrong | wrong |
| total_amount | 500.00 |  |  | wrong | wrong |
| prepared_by | Nitin Kothari |  |  | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone |  |  |  | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 0000000000 |  |  | wrong | wrong |
| package_description | Parcel |  |  | wrong | wrong |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p97990 - `WhatsApp Image 2026-11-10 at 22.01.40.jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | BABA TRAVELS | BABA TRAVELS | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | strict | strict |
| receipt_number | P97990 | 02/2025 | 02/2025 | wrong | wrong |
| date | 07/02/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commerical |  |  | wrong | wrong |
| consignor_name | Self |  |  | wrong | wrong |
| package_count | 8 |  |  | wrong | wrong |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 800.00 | 800.00 | 800.00 | strict | strict |
| prepared_by | Sagar Sharma |  |  | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone | 0000000000 |  |  | wrong | wrong |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 0000000000 | 0000000000 |  | strict | wrong |
| package_description | Parcel |  |  | wrong | wrong |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p98347 - `WhatsApp Image 2026-11-10 at 22.01.41 (1).jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | strict | strict |
| receipt_number | P98347 | P98347 | P98347 | strict | strict |
| date | 19/02/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercial | Ve Commercial | Ve Commercial | strict | strict |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 4 | 4 | 4 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 400.00 | 400.00 | 400.00 | strict | strict |
| prepared_by | Rahul Sharma |  |  | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone | 0000000000 | 0000000000 | 0000000000 | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 0000000000 | 0000000000 | 0000000000 | strict | strict |
| package_description | Parcel | Parcel | Parcel | strict | strict |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p98828 - `WhatsApp Image 2026-11-10 at 22.01.41 (2).jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | BABA TRAVELS |  | strict | wrong |
| operator_gstin | 23AHQPS8492M1ZA |  |  | wrong | wrong |
| receipt_number | P98828 | 703/202 |  | wrong | wrong |
| date | 10/03/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad |  |  | wrong | wrong |
| consignee_name | Ve Commercial |  |  | wrong | wrong |
| consignor_name | Self |  |  | wrong | wrong |
| package_count | 10 | 10 |  | strict | wrong |
| payment_mode | Paid | Paid |  | strict | wrong |
| total_amount | 1000.00 | 0.00 |  | wrong | wrong |
| prepared_by | Rahul Sharma |  |  | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone |  |  |  | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone |  |  |  | strict | strict |
| package_description | Parcel | Parcel |  | strict | wrong |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p97829 - `WhatsApp Image 2026-11-10 at 22.01.41.jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | BABA TRAVELS | BABA TRAVELS | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | strict | strict |
| receipt_number | P97829 | B.0.27 | B.0.27 | wrong | wrong |
| date | 01/02/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercial |  |  | wrong | wrong |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 5 | 5 | 5 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 500.00 | 500.00 | 500.00 | strict | strict |
| prepared_by | Alok Sen |  |  | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  |  | INDORE | strict | wrong |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone |  |  |  | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 0000000000 | 0000000000 | 0000000000 | strict | strict |
| package_description | Parcel | Parcel | Parcel | strict | strict |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p98595 - `WhatsApp Image 2026-11-10 at 22.01.54 (2).jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA |  |  | wrong | wrong |
| receipt_number | P98595 |  |  | wrong | wrong |
| date | 28/02/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad |  |  | wrong | wrong |
| consignee_name | Orlicon Blazer |  |  | wrong | wrong |
| consignor_name | Self |  |  | wrong | wrong |
| package_count | 3 |  |  | wrong | wrong |
| payment_mode | Paid |  |  | wrong | wrong |
| total_amount | 300.00 |  |  | wrong | wrong |
| prepared_by | Nitin Kothari |  |  | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone |  |  |  | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 0000000000 |  |  | wrong | wrong |
| package_description | Parcel |  |  | wrong | wrong |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  |  |  | strict | strict |

## b. Per-field summary (dev set, optimistic)

| field | n | A strict % | A lenient % | B strict % | B lenient % |
|---|---|---|---|---|---|
| operator_name | 18 | 83.3 | 83.3 | 77.8 | 77.8 |
| operator_gstin | 15 | 53.3 | 53.3 | 53.3 | 53.3 |
| receipt_number | 18 | 27.8 | 27.8 | 27.8 | 27.8 |
| date | 18 | 22.2 | 22.2 | 22.2 | 22.2 |
| to_place | 18 | 72.2 | 72.2 | 72.2 | 72.2 |
| consignee_name | 18 | 44.4 | 44.4 | 38.9 | 38.9 |
| consignor_name | 18 | 61.1 | 61.1 | 61.1 | 61.1 |
| package_count | 18 | 61.1 | 61.1 | 55.6 | 55.6 |
| payment_mode | 18 | 83.3 | 83.3 | 77.8 | 77.8 |
| total_amount | 18 | 72.2 | 72.2 | 72.2 | 72.2 |
| prepared_by | 16 | 18.8 | 18.8 | 25.0 | 25.0 |
| time | 5 | 0.0 | 60.0 | 0.0 | 60.0 |
| from_place | 3 | 66.7 | 66.7 | 66.7 | 66.7 |
| delivery_address | 4 | 0.0 | 75.0 | 0.0 | 75.0 |
| consignor_gstin | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| consignor_phone | 11 | 63.6 | 63.6 | 72.7 | 72.7 |
| consignee_gstin | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| consignee_phone | 17 | 76.5 | 76.5 | 64.7 | 64.7 |
| package_description | 18 | 50.0 | 66.7 | 44.4 | 61.1 |
| freight | 4 | 75.0 | 75.0 | 100.0 | 100.0 |
| delivery_charge | 1 | 100.0 | 100.0 | 100.0 | 100.0 |
| demurrage | 1 | 100.0 | 100.0 | 100.0 | 100.0 |
| sgst | 3 | 100.0 | 100.0 | 66.7 | 66.7 |
| cgst | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| igst | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| amount_in_words | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| remark | 1 | 0.0 | 100.0 | 0.0 | 100.0 |

## c. Core vs optional (dev set, optimistic)

| scope | Run | n | strict | lenient | strict % | lenient % |
|---|---|---|---|---|---|---|
| core | A | 193 | 106 | 106 | 54.9 | 54.9 |
| core | B | 193 | 103 | 103 | 53.4 | 53.4 |
| optional | A | 83 | 54 | 64 | 65.1 | 77.1 |
| optional | B | 83 | 52 | 62 | 62.7 | 74.7 |
| overall | A | 276 | 160 | 170 | 58.0 | 61.6 |
| overall | B | 276 | 155 | 165 | 56.2 | 59.8 |

Run A false values (18 scored receipts): 1/210 blank-truth cells (0.5%)

Run B false values (18 scored receipts): 1/210 blank-truth cells (0.5%)

## d. Mismatches only (lenient-wrong, truth non-blank; all 20 files, both runs)

Cause is a heuristic, not verified against raw OCR text: blank -> missing; text similarity >= 0.75 -> OCR misread; otherwise AI wrong / unclear.

| receipt | photo | run | field | actual | OCR | probable cause |
|---|---|---|---|---|---|---|
| pawan_gr28625 |  22.01.42 (3).jpeg | B | amount_in_words | Rupees One Hundred Only | One Hundred Only | OCR misread (near match) |
| pawan_gr41468 |  22.01.33 (2).jpeg | A | package_count | 2 |  | missing (blank) |
| pawan_gr41468 |  22.01.33 (2).jpeg | B | package_count | 2 |  | missing (blank) |
| pawan_gr41468 |  22.01.33 (2).jpeg | A | from_place | INDORE | W DORE | AI wrong / wrong source line (unclear) |
| pawan_gr41468 |  22.01.33 (2).jpeg | B | from_place | INDORE | W DORE | AI wrong / wrong source line (unclear) |
| pawan_gr41468 |  22.01.33 (2).jpeg | A | freight | 200 |  | missing (blank) |
| pawan_gr38420 | 0 at 22.01.33.jpeg | B | sgst | 0 |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | operator_gstin | 23AHQPS8492M1ZA | 23AHQP8492M1ZA | OCR misread (near match) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | receipt_number | P8851 |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | receipt_number | P8851 |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | date | 21/04/2026 |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | date | 21/04/2026 | 01/04/2026 | OCR misread (near match) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | consignor_name | Self |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | consignor_name | Self |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | package_count | 4 |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | package_count | 4 |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | prepared_by | Shresth Sharma |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | time | 17:17:59 |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | time | 17:17:59 | 17:17 | OCR misread (near match) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | delivery_address | Veer Travels Opp Vishva Hotel Ctm Cross Road |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | delivery_address | Veer Travels Opp Vishva Hotel Ctm Cross Road |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | consignor_phone | 00 |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | consignor_phone | 00 |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | consignee_phone | 00 |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | package_description | Parcel |  | missing (blank) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | package_description | Parcel |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | A | receipt_number | 186,798 |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | B | receipt_number | 186,798 |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | A | date | 01/06/2026 |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | B | date | 01/06/2026 |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | A | to_place | Indore |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | B | to_place | Indore |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | A | consignee_name | Ve Commercial |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | B | consignee_name | Ve Commercial |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | A | consignor_name | oerlikon, Ahmedabad |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | B | consignor_name | oerlikon, Ahmedabad |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | A | prepared_by | Devshree Vern |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | B | prepared_by | Devshree Vern |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | A | time | 10:33:06 |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | B | time | 10:33:06 |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | A | consignee_phone | 8878424014 |  | missing (blank) |
| baba_186798 | 0 at 22.01.34.jpeg | B | consignee_phone | 8878424014 |  | missing (blank) |
| baba_p98250 |  22.01.37 (2).jpeg | A | receipt_number | P98250 |  | missing (blank) |
| baba_p98250 |  22.01.37 (2).jpeg | B | receipt_number | P98250 |  | missing (blank) |
| baba_p98250 |  22.01.37 (2).jpeg | A | date | 15/02/2025 |  | missing (blank) |
| baba_p98250 |  22.01.37 (2).jpeg | B | date | 15/02/2025 |  | missing (blank) |
| baba_p98250 |  22.01.37 (2).jpeg | A | consignee_name | Ve Commercial | AR | AI wrong / wrong source line (unclear) |
| baba_p98250 |  22.01.37 (2).jpeg | B | consignee_name | Ve Commercial | AR | AI wrong / wrong source line (unclear) |
| baba_p98250 |  22.01.37 (2).jpeg | A | package_count | 6 | 2 | AI wrong / wrong source line (unclear) |
| baba_p98250 |  22.01.37 (2).jpeg | B | package_count | 6 | 2 | AI wrong / wrong source line (unclear) |
| baba_p98250 |  22.01.37 (2).jpeg | A | prepared_by | Alok Sen |  | missing (blank) |
| baba_p98250 |  22.01.37 (2).jpeg | B | prepared_by | Alok Sen |  | missing (blank) |
| baba_p98250 |  22.01.37 (2).jpeg | A | consignor_phone | 0000000000 |  | missing (blank) |
| baba_p98250 |  22.01.37 (2).jpeg | B | consignor_phone | 0000000000 |  | missing (blank) |
| baba_p98250 |  22.01.37 (2).jpeg | A | package_description | Parcel |  | missing (blank) |
| baba_p98250 |  22.01.37 (2).jpeg | B | package_description | Parcel |  | missing (blank) |
| baba_p98506 | 0 at 22.01.37.jpeg | B | operator_name | BABA TRAVELS | ELSLASA TRAVELS | AI wrong / wrong source line (unclear) |
| baba_p98506 | 0 at 22.01.37.jpeg | A | receipt_number | P98506 |  | missing (blank) |
| baba_p98506 | 0 at 22.01.37.jpeg | B | receipt_number | P98506 |  | missing (blank) |
| baba_p98506 | 0 at 22.01.37.jpeg | A | date | 25/02/2025 |  | missing (blank) |
| baba_p98506 | 0 at 22.01.37.jpeg | B | date | 25/02/2025 |  | missing (blank) |
| baba_p98506 |  22.01.40 (1).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p98506 |  22.01.40 (1).jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p98506 |  22.01.40 (1).jpeg | A | receipt_number | P98506 | OLSHASIAVEL | AI wrong / wrong source line (unclear) |
| baba_p98506 |  22.01.40 (1).jpeg | B | receipt_number | P98506 | OLSHASIAVEL | AI wrong / wrong source line (unclear) |
| baba_p98506 |  22.01.40 (1).jpeg | A | date | 25/02/2025 |  | missing (blank) |
| baba_p98506 |  22.01.40 (1).jpeg | B | date | 25/02/2025 |  | missing (blank) |
| baba_p98506 |  22.01.40 (1).jpeg | A | consignee_name | Ve Commercial |  | missing (blank) |
| baba_p98506 |  22.01.40 (1).jpeg | B | consignee_name | Ve Commercial |  | missing (blank) |
| baba_p98506 |  22.01.40 (1).jpeg | A | consignee_phone | 0000000000 |  | missing (blank) |
| baba_p98506 |  22.01.40 (1).jpeg | B | consignee_phone | 0000000000 |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | A | operator_name | BABA TRAVELS |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | B | operator_name | BABA TRAVELS |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | A | receipt_number | P98755 |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | B | receipt_number | P98755 |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | A | date | 06/03/2025 |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | B | date | 06/03/2025 |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | A | to_place | Ahmedabad |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | B | to_place | Ahmedabad |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | A | consignee_name | Orlicon Blazer |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | B | consignee_name | Orlicon Blazer |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | A | consignor_name | Self |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | B | consignor_name | Self |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | A | package_count | 7 |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | B | package_count | 7 |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | A | payment_mode | Paid |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | B | payment_mode | Paid |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | A | total_amount | 700.00 |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | B | total_amount | 700.00 |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | A | prepared_by | Nitin Kothari |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | B | prepared_by | Nitin Kothari |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | A | consignee_phone | 0000000000 |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | B | consignee_phone | 0000000000 |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | A | package_description | Parcel |  | missing (blank) |
| baba_p98755 |  22.01.38 (1).jpeg | B | package_description | Parcel |  | missing (blank) |
| baba_p97394 |  22.01.38 (2).jpeg | A | operator_name | BABA TRAVELS |  | missing (blank) |
| baba_p97394 |  22.01.38 (2).jpeg | A | date | 16/01/2025 |  | missing (blank) |
| baba_p97394 |  22.01.38 (2).jpeg | B | date | 16/01/2025 |  | missing (blank) |
| baba_p97394 |  22.01.38 (2).jpeg | A | consignee_name | Ve Commercial | ToVe Commercial | OCR misread (near match) |
| baba_p97394 |  22.01.38 (2).jpeg | B | consignee_name | Ve Commercial | ToVe Commercial | OCR misread (near match) |
| baba_p98010 | 0 at 22.01.38.jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p98010 | 0 at 22.01.38.jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p98010 | 0 at 22.01.38.jpeg | A | receipt_number | P98010 |  | missing (blank) |
| baba_p98010 | 0 at 22.01.38.jpeg | B | receipt_number | P98010 |  | missing (blank) |
| baba_p98010 | 0 at 22.01.38.jpeg | A | date | 08/02/2025 |  | missing (blank) |
| baba_p98010 | 0 at 22.01.38.jpeg | B | date | 08/02/2025 |  | missing (blank) |
| baba_p98010 | 0 at 22.01.38.jpeg | B | consignee_name | Ve Commercila | ToVe Commercila | OCR misread (near match) |
| baba_p98010 | 0 at 22.01.38.jpeg | A | prepared_by | Bobby |  | missing (blank) |
| baba_p98010 | 0 at 22.01.38.jpeg | B | prepared_by | Bobby |  | missing (blank) |
| baba_p98010 | 0 at 22.01.38.jpeg | A | consignor_phone | 0000000000 |  | missing (blank) |
| baba_p97300 |  22.01.39 (1).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p97300 |  22.01.39 (1).jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p97300 |  22.01.39 (1).jpeg | A | receipt_number | P97300 |  | missing (blank) |
| baba_p97300 |  22.01.39 (1).jpeg | B | receipt_number | P97300 |  | missing (blank) |
| baba_p97300 |  22.01.39 (1).jpeg | A | consignee_name | Ve Commercial | Commercial | OCR misread (near match) |
| baba_p97300 |  22.01.39 (1).jpeg | B | consignee_name | Ve Commercial |  | missing (blank) |
| baba_p97300 |  22.01.39 (1).jpeg | A | total_amount | 400.00 |  | missing (blank) |
| baba_p97300 |  22.01.39 (1).jpeg | B | total_amount | 400.00 |  | missing (blank) |
| baba_p97300 |  22.01.39 (1).jpeg | A | prepared_by | Rahul Sharma |  | missing (blank) |
| baba_p97300 |  22.01.39 (1).jpeg | B | prepared_by | Rahul Sharma |  | missing (blank) |
| baba_p97433 | 0 at 22.01.39.jpeg | A | receipt_number | P97433 |  | missing (blank) |
| baba_p97433 | 0 at 22.01.39.jpeg | B | receipt_number | P97433 |  | missing (blank) |
| baba_p97433 | 0 at 22.01.39.jpeg | A | date | 17/01/2025 |  | missing (blank) |
| baba_p97433 | 0 at 22.01.39.jpeg | B | date | 17/01/2025 |  | missing (blank) |
| baba_p97433 | 0 at 22.01.39.jpeg | A | prepared_by | Alok Sen |  | missing (blank) |
| baba_p97433 | 0 at 22.01.39.jpeg | B | prepared_by | Alok Sen |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | A | operator_name | BABA TRAVELS |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | B | operator_name | BABA TRAVELS |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | A | receipt_number | P98635 |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | B | receipt_number | P98635 |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | A | date | 01/03/2025 |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | B | date | 01/03/2025 |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | A | to_place | Ahmedabad |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | B | to_place | Ahmedabad |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | A | consignee_name | Orlicon Blazer |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | B | consignee_name | Orlicon Blazer |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | A | consignor_name | Self |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | B | consignor_name | Self |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | A | package_count | 5 |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | B | package_count | 5 |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | A | payment_mode | Paid |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | B | payment_mode | Paid |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | A | total_amount | 500.00 |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | B | total_amount | 500.00 |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | A | prepared_by | Nitin Kothari |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | B | prepared_by | Nitin Kothari |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | A | consignee_phone | 0000000000 |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | B | consignee_phone | 0000000000 |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | A | package_description | Parcel |  | missing (blank) |
| baba_p98635 |  22.01.40 (2).jpeg | B | package_description | Parcel |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | A | receipt_number | P97990 | 02/2025 | AI wrong / wrong source line (unclear) |
| baba_p97990 | 0 at 22.01.40.jpeg | B | receipt_number | P97990 | 02/2025 | AI wrong / wrong source line (unclear) |
| baba_p97990 | 0 at 22.01.40.jpeg | A | date | 07/02/2025 |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | B | date | 07/02/2025 |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | A | consignee_name | Ve Commerical |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | B | consignee_name | Ve Commerical |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | A | consignor_name | Self |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | B | consignor_name | Self |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | A | package_count | 8 |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | B | package_count | 8 |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | A | prepared_by | Sagar Sharma |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | B | prepared_by | Sagar Sharma |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | A | consignor_phone | 0000000000 |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | B | consignor_phone | 0000000000 |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | B | consignee_phone | 0000000000 |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | A | package_description | Parcel |  | missing (blank) |
| baba_p97990 | 0 at 22.01.40.jpeg | B | package_description | Parcel |  | missing (blank) |
| baba_p98347 |  22.01.41 (1).jpeg | A | date | 19/02/2025 |  | missing (blank) |
| baba_p98347 |  22.01.41 (1).jpeg | B | date | 19/02/2025 |  | missing (blank) |
| baba_p98347 |  22.01.41 (1).jpeg | A | prepared_by | Rahul Sharma |  | missing (blank) |
| baba_p98347 |  22.01.41 (1).jpeg | B | prepared_by | Rahul Sharma |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | B | operator_name | BABA TRAVELS |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | A | receipt_number | P98828 | 703/202 | AI wrong / wrong source line (unclear) |
| baba_p98828 |  22.01.41 (2).jpeg | B | receipt_number | P98828 |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | A | date | 10/03/2025 |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | B | date | 10/03/2025 |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | A | to_place | Ahmedabad |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | B | to_place | Ahmedabad |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | A | consignee_name | Ve Commercial |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | B | consignee_name | Ve Commercial |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | A | consignor_name | Self |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | B | consignor_name | Self |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | B | package_count | 10 |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | B | payment_mode | Paid |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | A | total_amount | 1000.00 | 0.00 | AI wrong / wrong source line (unclear) |
| baba_p98828 |  22.01.41 (2).jpeg | B | total_amount | 1000.00 |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | A | prepared_by | Rahul Sharma |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | B | prepared_by | Rahul Sharma |  | missing (blank) |
| baba_p98828 |  22.01.41 (2).jpeg | B | package_description | Parcel |  | missing (blank) |
| baba_p97829 | 0 at 22.01.41.jpeg | A | receipt_number | P97829 | B.0.27 | AI wrong / wrong source line (unclear) |
| baba_p97829 | 0 at 22.01.41.jpeg | B | receipt_number | P97829 | B.0.27 | AI wrong / wrong source line (unclear) |
| baba_p97829 | 0 at 22.01.41.jpeg | A | date | 01/02/2025 |  | missing (blank) |
| baba_p97829 | 0 at 22.01.41.jpeg | B | date | 01/02/2025 |  | missing (blank) |
| baba_p97829 | 0 at 22.01.41.jpeg | A | consignee_name | Ve Commercial |  | missing (blank) |
| baba_p97829 | 0 at 22.01.41.jpeg | B | consignee_name | Ve Commercial |  | missing (blank) |
| baba_p97829 | 0 at 22.01.41.jpeg | A | prepared_by | Alok Sen |  | missing (blank) |
| baba_p97829 | 0 at 22.01.41.jpeg | B | prepared_by | Alok Sen |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | A | receipt_number | P98595 |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | B | receipt_number | P98595 |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | A | date | 28/02/2025 |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | B | date | 28/02/2025 |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | A | to_place | Ahmedabad |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | B | to_place | Ahmedabad |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | A | consignee_name | Orlicon Blazer |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | B | consignee_name | Orlicon Blazer |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | A | consignor_name | Self |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | B | consignor_name | Self |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | A | package_count | 3 |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | B | package_count | 3 |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | A | payment_mode | Paid |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | B | payment_mode | Paid |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | A | total_amount | 300.00 |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | B | total_amount | 300.00 |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | A | prepared_by | Nitin Kothari |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | B | prepared_by | Nitin Kothari |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | A | consignee_phone | 0000000000 |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | B | consignee_phone | 0000000000 |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | A | package_description | Parcel |  | missing (blank) |
| baba_p98595 |  22.01.54 (2).jpeg | B | package_description | Parcel |  | missing (blank) |

Total mismatch cells: 228 (Run A 111, Run B 117).

## e. False values (truth empty, OCR non-empty in either run)

| receipt | photo | field | OCR Run A | OCR Run B |
|---|---|---|---|---|
| baba_p98506 | 0 at 22.01.37.jpeg | remark | Subject to INDORE Jurisdictlon |  |
| baba_p97829 | 0 at 22.01.41.jpeg | from_place |  | INDORE |

Total rows: 2 (all 20 files).

## f. Single vs bulk differences (Run A value != Run B value, same file)

| receipt | photo | field | actual | Run A | Run B |
|---|---|---|---|---|---|
| pawan_gr28625 |  22.01.33 (1).jpeg | from_place | INDORE | INDORE | Indore |
| pawan_gr28625 |  22.01.42 (3).jpeg | from_place | INDORE | INDORE | Indore |
| pawan_gr28625 |  22.01.42 (3).jpeg | amount_in_words | Rupees One Hundred Only | Rupees One Hundred Only | One Hundred Only |
| pawan_gr41468 |  22.01.33 (2).jpeg | freight | 200 |  | 200 |
| pawan_gr38420 | 0 at 22.01.33.jpeg | sgst | 0 | 0 |  |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | operator_gstin | 23AHQPS8492M1ZA |  | 23AHQP8492M1ZA |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | date | 21/04/2026 |  | 01/04/2026 |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | prepared_by | Shresth Sharma |  | Shresth Sharma |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | time | 17:17:59 |  | 17:17 |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | consignee_phone | 00 | 00 |  |
| baba_p98506 | 0 at 22.01.37.jpeg | operator_name | BABA TRAVELS | Baba Travels | ELSLASA TRAVELS |
| baba_p98506 | 0 at 22.01.37.jpeg | remark |  | Subject to INDORE Jurisdictlon |  |
| baba_p97394 |  22.01.38 (2).jpeg | operator_name | BABA TRAVELS |  | Baba Travels |
| baba_p98010 | 0 at 22.01.38.jpeg | operator_name | BABA TRAVELS | Baba Travels | BABA TRAVELS |
| baba_p98010 | 0 at 22.01.38.jpeg | consignee_name | Ve Commercila | Ve Commercila | ToVe Commercila |
| baba_p98010 | 0 at 22.01.38.jpeg | consignor_phone | 0000000000 |  | 0000000000 |
| baba_p97300 |  22.01.39 (1).jpeg | consignee_name | Ve Commercial | Commercial |  |
| baba_p97990 | 0 at 22.01.40.jpeg | consignee_phone | 0000000000 | 0000000000 |  |
| baba_p98828 |  22.01.41 (2).jpeg | operator_name | BABA TRAVELS | BABA TRAVELS |  |
| baba_p98828 |  22.01.41 (2).jpeg | receipt_number | P98828 | 703/202 |  |
| baba_p98828 |  22.01.41 (2).jpeg | package_count | 10 | 10 |  |
| baba_p98828 |  22.01.41 (2).jpeg | payment_mode | Paid | Paid |  |
| baba_p98828 |  22.01.41 (2).jpeg | total_amount | 1000.00 | 0.00 |  |
| baba_p98828 |  22.01.41 (2).jpeg | package_description | Parcel | Parcel |  |
| baba_p97829 | 0 at 22.01.41.jpeg | from_place |  |  | INDORE |

Total differing cells: 25 of 540 (checked cell by cell, not assumed). Both runs use the same code, same prompt and same model, with deterministic preprocessing/OCR/post-processing; the only run-to-run variation source is Groq LLM sampling, so identical or near-identical results are expected.

## g. Speed and failures

- Run A (single, upload to processed, polled every 1s): avg 25.1s/doc over 20 docs.
- Run B (bulk 4x5): avg 82.3s/doc measured from batch POST to each doc reaching processed (inflated by queueing inside a batch); batch wall times [144.4, 80.1, 102.7, 200.7]s => 26.4s/doc throughput.
- Failures/errors: none; all 40 documents reached processed, no client-visible errors or retries.
