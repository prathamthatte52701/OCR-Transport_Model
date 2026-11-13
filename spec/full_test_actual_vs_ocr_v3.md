# Full OCR test v3: actual vs OCR (final code)

**Every number below is on the DEV SET (the same 20 images used to tune the prompt) - dev set, optimistic. None of it shows generalization.**

Code measured: master at `fbd9f70` (server started from it; no code or prompt change during the run). Real database `docintel_transport`, two dedicated test users (usernames are limited to 8 characters, so `zz_tr_lp` = Run A single uploads, `zz_tr_lb` = Run B bulk 4x5; separate users so Run B copies are not duplicates of Run A copies). Scoring via `spec/score.py`. Aggregates count each of the 18 unique receipts once (first photo by filename for the 2 duplicate-photo receipts); tables cover all 20 files. In tables `wrong` on a blank-truth cell = a false (invented) value.

## Worst 5 fields by strict accuracy, Run A (dev set, optimistic)

| field | n | strict % | lenient % |
|---|---|---|---|
| remark | 1 | 0.0 | 100.0 |
| delivery_address | 4 | 25.0 | 75.0 |
| receipt_number | 18 | 33.3 | 33.3 |
| date | 18 | 38.9 | 38.9 |
| prepared_by | 16 | 43.8 | 43.8 |

## Worst 5 fields by strict accuracy, Run B (dev set, optimistic)

| field | n | strict % | lenient % |
|---|---|---|---|
| remark | 1 | 0.0 | 100.0 |
| delivery_address | 4 | 25.0 | 75.0 |
| receipt_number | 18 | 33.3 | 33.3 |
| date | 18 | 33.3 | 33.3 |
| prepared_by | 16 | 43.8 | 43.8 |

## Headline (dev set, optimistic)

| scope | n | Run A strict % | Run A lenient % | Run B strict % | Run B lenient % |
|---|---|---|---|---|---|
| core | 193 | 63.2 | 63.2 | 62.7 | 62.7 |
| optional | 83 | 79.5 | 86.7 | 80.7 | 88.0 |
| overall | 276 | 68.1 | 70.3 | 68.1 | 70.3 |

Whole receipt correct (strict, every field of one document): Run A: all 11 core fields 3/18, all 27 fields 1/18; Run B: all 11 core fields 3/18, all 27 fields 1/18.

## 1. Per-receipt tables

18 unique receipts; **two receipts have duplicate photos (Pawan GR28625, Baba P98506)**: one ground truth, both photos shown.

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
| time | 11:25 AM | 11:25 AM | 11:25 AM | strict | strict |
| from_place | INDORE | INDORE | INDORE | strict | strict |
| delivery_address | MAYARAM JI 8087536777 | MAYARAM JI 8087536777 | MAYARAM JI 8087536777 | strict | strict |
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
| time | 11:25 AM | 11:25 AM | 11:25 AM | strict | strict |
| from_place | INDORE | Indore | INDORE | strict | strict |
| delivery_address | MAYARAM JI 8087536777 | MAYARAM JI 8087536777 | MAYARAM JI 8087536777 | strict | strict |
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
| time | 12:45 PM | 12:45 PM | 12:45 PM | strict | strict |
| from_place | INDORE |  | Indore | wrong | strict |
| delivery_address | MAYARAM JI 8087536777 | MAYARAMJI 8087536777 | MAYARAMJI 8087536777 | lenient | lenient |
| consignor_gstin | 27AAECK1993K1Z3 | 27AAECK1993K1Z3 | 27AAECK1993K1Z3 | strict | strict |
| consignor_phone | 8518888766 | 8518888766 | 8518888766 | strict | strict |
| consignee_gstin | 23AABCE9378F3ZI | 23AABCE9378F3ZI | 23AABCE9378F3ZI | strict | strict |
| consignee_phone | 8518888766 | 8518888766 | 8518888766 | strict | strict |
| package_description | PARCEL - PARCEL | PARCEL-PARCEL | PARCEL-PARCEL | lenient | lenient |
| freight | 200 | 200 | 200 | strict | strict |
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
| time | 10:04 AM | 10:04 AM | 10:04 AM | strict | strict |
| from_place | INDORE | INDORE | INDORE | strict | strict |
| delivery_address | MAYARAM JI 8087536777 | MAYARAMJI 8087536777 | MAYARAMJI 8087536777 | lenient | lenient |
| consignor_gstin | 27AAECK1993K1Z3 | 27AAECK1993K1Z3 | 27AAECK1993K1Z3 | strict | strict |
| consignor_phone | 8518888766 | 8518888766 | 8518888766 | strict | strict |
| consignee_gstin | 23AABCE9378F3ZI | 23AABCE9378F3ZI | 23AABCE9378F3ZI | strict | strict |
| consignee_phone | 8518888766 | 8518888766 | 8518888766 | strict | strict |
| package_description | PARCEL - PARCEL | PARCEL-PARCEL | PARCEL-PARCEL | lenient | lenient |
| freight | 200 | 200 | 200 | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst | 0 | 0 | 0 | strict | strict |
| cgst | 0 | 0 | 0 | strict | strict |
| igst | 0 | 0 | 0 | strict | strict |
| amount_in_words | Rupees Two Hundred Only | Rupees Two Hundred Only | Rupees Two Hundred Only | strict | strict |
| remark |  |  |  | strict | strict |

### baba_p8851_twocopy - `WhatsApp Image 2026-11-10 at 22.01.34 (3).jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA |  | 23AHQP$8492M1ZA | wrong | wrong |
| receipt_number | P8851 |  |  | wrong | wrong |
| date | 21/04/2026 |  |  | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercial | Ve Commercial | Ve Commercial | strict | strict |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 4 | 4 | 4 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 400.00 | 400.00 | 400.00 | strict | strict |
| prepared_by | Shresth Sharma | Shresth Sharma | Shresth Sharma | strict | strict |
| time | 17:17:59 |  |  | wrong | wrong |
| from_place |  |  |  | strict | strict |
| delivery_address | Veer Travels Opp Vishva Hotel Ctm Cross Road |  |  | wrong | wrong |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone | 00 | 00 | 00 | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 00 | 00 | 00 | strict | strict |
| package_description | Parcel | Parcel | Parcel | strict | strict |
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
| receipt_number | 186,798 | eGey | eGey | wrong | wrong |
| date | 01/06/2026 |  |  | wrong | wrong |
| to_place | Indore | Indore | Indore | strict | strict |
| consignee_name | Ve Commercial | ToVe Commercial | ToVe Commercial | wrong | wrong |
| consignor_name | oerlikon, Ahmedabad | oerlikon |  | wrong | wrong |
| package_count | 14 | 14 | 14 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 140.00 | 140.00 | 140.00 | strict | strict |
| prepared_by | Devshree Vern | Devshree Vern | Devshree Vern | strict | strict |
| time | 10:33:06 |  |  | wrong | wrong |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone |  |  |  | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 8878424014 | 8878424014 | 8878424014 | strict | strict |
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
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA |  |  | wrong | wrong |
| receipt_number | P98250 | 39T No. - 23AH0PS0492:12A |  | wrong | wrong |
| date | 15/02/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercial |  |  | wrong | wrong |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 6 | 6 | 6 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 600.00 | 600.00 | 600.00 | strict | strict |
| prepared_by | Alok Sen |  |  | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone | 0000000000 | 0000000000 | 0000000000 | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone | 0000000000 | 0000000000 | 0000000000 | strict | strict |
| package_description | Parcel | Parce! | Parce! | wrong | wrong |
| freight |  |  |  | strict | strict |
| delivery_charge |  |  |  | strict | strict |
| demurrage |  |  |  | strict | strict |
| sgst |  |  |  | strict | strict |
| cgst |  |  |  | strict | strict |
| igst |  |  |  | strict | strict |
| amount_in_words |  |  |  | strict | strict |
| remark |  | Subject to INDORE JurisdictionAlok Sen |  | wrong | strict |

### baba_p98506 - `WhatsApp Image 2026-11-10 at 22.01.37.jpeg` (duplicate-pair photo)

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS |  |  | wrong | wrong |
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
| remark |  |  |  | strict | strict |

### baba_p98506 - `WhatsApp Image 2026-11-10 at 22.01.40 (1).jpeg` (duplicate-pair photo)

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA |  |  | wrong | wrong |
| receipt_number | P98506 | YOLSHABAIIAVEL565 | YOLSHABAIIAVEL565 | wrong | wrong |
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
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | strict | strict |
| receipt_number | P97394 | P97394 | P97394 | strict | strict |
| date | 16/01/2025 | 16/01/2023 | 16/01/2023 | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercial | Ve Commercial | Ve Commercial | strict | strict |
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
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA |  |  | wrong | wrong |
| receipt_number | P98010 |  |  | wrong | wrong |
| date | 08/02/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercila | Ve Commercila | Ve Commercila | strict | strict |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 2 | 2 | 2 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 200.00 | 200.00 | 200.00 | strict | strict |
| prepared_by | Bobby | Bobb | Bobb | wrong | wrong |
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

### baba_p97300 - `WhatsApp Image 2026-11-10 at 22.01.39 (1).jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA |  |  | wrong | wrong |
| receipt_number | P97300 |  |  | wrong | wrong |
| date | 13/01/2025 | 13/01/2025 | 13/01/2025 | strict | strict |
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
| receipt_number | P97433 | P97433 | P97433 | strict | strict |
| date | 17/01/2025 | 17/01/2025 | 17/01/2025 | strict | strict |
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
| operator_name | BABA TRAVELS | BABA TRAVELS | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | strict | strict |
| receipt_number | P97990 | 102/2025 | 102/2025 | wrong | wrong |
| date | 07/02/2025 | 07/02/2025 |  | strict | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commerical | Commerica! |  | wrong | wrong |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 8 | 8 | 8 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 800.00 | 800.00 | 800.00 | strict | strict |
| prepared_by | Sagar Sharma | Sagar Sharma | Sagar Sharma | strict | strict |
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

### baba_p98347 - `WhatsApp Image 2026-11-10 at 22.01.41 (1).jpeg`

| field | Actual | OCR (Run A) | OCR (Run B) | Match A | Match B |
|---|---|---|---|---|---|
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | strict | strict |
| receipt_number | P98347 | P98347 | P98347 | strict | strict |
| date | 19/02/2025 | 19/02/2025 | 19/02/2025 | strict | strict |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercial | Ve Commercial | Ve Commercial | strict | strict |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 4 | 4 | 4 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 400.00 | 400.00 | 400.00 | strict | strict |
| prepared_by | Rahul Sharma | Rahul Sharma | Rahul Sharma | strict | strict |
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
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA |  |  | wrong | wrong |
| receipt_number | P98828 | 703/202 | 703/202 | wrong | wrong |
| date | 10/03/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad |  |  | wrong | wrong |
| consignee_name | Ve Commercial |  |  | wrong | wrong |
| consignor_name | Self |  |  | wrong | wrong |
| package_count | 10 | 10 | 10 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 1000.00 | 000.00 | 000.00 | wrong | wrong |
| prepared_by | Rahul Sharma | anul-Sharma | anul-Sharma | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  |  |  | strict | strict |
| delivery_address |  |  |  | strict | strict |
| consignor_gstin |  |  |  | strict | strict |
| consignor_phone |  |  |  | strict | strict |
| consignee_gstin |  |  |  | strict | strict |
| consignee_phone |  |  |  | strict | strict |
| package_description | Parcel | Parcel | Parcel | strict | strict |
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
| operator_name | BABA TRAVELS | Baba Travels | Baba Travels | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA | strict | strict |
| receipt_number | P97829 | B.0.27 |  | wrong | wrong |
| date | 01/02/2025 |  |  | wrong | wrong |
| to_place | Ahmedabad | Ahmedabad | Ahmedabad | strict | strict |
| consignee_name | Ve Commercial |  |  | wrong | wrong |
| consignor_name | Self | Self | Self | strict | strict |
| package_count | 5 | 5 | 5 | strict | strict |
| payment_mode | Paid | Paid | Paid | strict | strict |
| total_amount | 500.00 | 500.00 | 500.00 | strict | strict |
| prepared_by | Alok Sen |  |  | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  |  | Indore | strict | wrong |
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
| operator_name | BABA TRAVELS | Baba Travels | BABA TRAVELS | strict | strict |
| operator_gstin | 23AHQPS8492M1ZA |  |  | wrong | wrong |
| receipt_number | P98595 |  | 60 | wrong | wrong |
| date | 28/02/2025 | 03/04/2005 | 03/04/2005 | wrong | wrong |
| to_place | Ahmedabad |  |  | wrong | wrong |
| consignee_name | Orlicon Blazer |  | RARA | wrong | wrong |
| consignor_name | Self |  |  | wrong | wrong |
| package_count | 3 |  |  | wrong | wrong |
| payment_mode | Paid |  |  | wrong | wrong |
| total_amount | 300.00 |  |  | wrong | wrong |
| prepared_by | Nitin Kothari | Nitin Kothan | Nitin Kothan | wrong | wrong |
| time |  |  |  | strict | strict |
| from_place |  | hmedabad | hmedabad | wrong | wrong |
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

## 2. Per-field summary (dev set, optimistic)

| field | n | A strict % | A lenient % | B strict % | B lenient % |
|---|---|---|---|---|---|
| operator_name | 18 | 83.3 | 83.3 | 83.3 | 83.3 |
| operator_gstin | 15 | 46.7 | 46.7 | 46.7 | 46.7 |
| receipt_number | 18 | 33.3 | 33.3 | 33.3 | 33.3 |
| date | 18 | 38.9 | 38.9 | 33.3 | 33.3 |
| to_place | 18 | 77.8 | 77.8 | 77.8 | 77.8 |
| consignee_name | 18 | 55.6 | 55.6 | 55.6 | 55.6 |
| consignor_name | 18 | 72.2 | 72.2 | 72.2 | 72.2 |
| package_count | 18 | 77.8 | 77.8 | 77.8 | 77.8 |
| payment_mode | 18 | 83.3 | 83.3 | 83.3 | 83.3 |
| total_amount | 18 | 77.8 | 77.8 | 77.8 | 77.8 |
| prepared_by | 16 | 43.8 | 43.8 | 43.8 | 43.8 |
| time | 5 | 60.0 | 60.0 | 60.0 | 60.0 |
| from_place | 3 | 66.7 | 66.7 | 100.0 | 100.0 |
| delivery_address | 4 | 25.0 | 75.0 | 25.0 | 75.0 |
| consignor_gstin | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| consignor_phone | 11 | 100.0 | 100.0 | 100.0 | 100.0 |
| consignee_gstin | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| consignee_phone | 17 | 82.4 | 82.4 | 82.4 | 82.4 |
| package_description | 18 | 61.1 | 77.8 | 61.1 | 77.8 |
| freight | 4 | 100.0 | 100.0 | 100.0 | 100.0 |
| delivery_charge | 1 | 100.0 | 100.0 | 100.0 | 100.0 |
| demurrage | 1 | 100.0 | 100.0 | 100.0 | 100.0 |
| sgst | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| cgst | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| igst | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| amount_in_words | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| remark | 1 | 0.0 | 100.0 | 0.0 | 100.0 |

## 3. Core vs optional (dev set, optimistic)

| scope | Run | n | strict | lenient | strict % | lenient % |
|---|---|---|---|---|---|---|
| core | A | 193 | 122 | 122 | 63.2 | 63.2 |
| core | B | 193 | 121 | 121 | 62.7 | 62.7 |
| optional | A | 83 | 66 | 72 | 79.5 | 86.7 |
| optional | B | 83 | 67 | 73 | 80.7 | 88.0 |
| overall | A | 276 | 188 | 194 | 68.1 | 70.3 |
| overall | B | 276 | 188 | 194 | 68.1 | 70.3 |

## 4. Mismatches only, with probable cause (all 20 files, both runs)

Cause rule: look for the truth value (letters+digits only) in the stored OCR text of that document. Not in the text and value empty -> OCR empty; not in the text but a wrong value came out -> OCR garbled; in the text but wrong/empty -> model wrong or a rule changed it. The raw model reply is not stored, so "model wrong" and "rule changed it" cannot be told apart here (the post-processing rules only repair or flag).

| receipt | photo | run | field | actual | OCR | probable cause |
|---|---|---|---|---|---|---|
| pawan_gr41468 |  22.01.33 (2).jpeg | A | package_count | 2 |  | model/rules left it empty although the text has it |
| pawan_gr41468 |  22.01.33 (2).jpeg | B | package_count | 2 |  | model/rules left it empty although the text has it |
| pawan_gr41468 |  22.01.33 (2).jpeg | A | from_place | INDORE |  | model/rules left it empty although the text has it |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | operator_gstin | 23AHQPS8492M1ZA | 23AHQP$8492M1ZA | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | receipt_number | P8851 |  | OCR empty (value not in OCR text) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | receipt_number | P8851 |  | OCR empty (value not in OCR text) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | date | 21/04/2026 |  | OCR empty (value not in OCR text) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | date | 21/04/2026 |  | OCR empty (value not in OCR text) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | time | 17:17:59 |  | OCR empty (value not in OCR text) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | time | 17:17:59 |  | OCR empty (value not in OCR text) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | A | delivery_address | Veer Travels Opp Vishva Hotel Ctm Cross Road |  | OCR empty (value not in OCR text) |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | B | delivery_address | Veer Travels Opp Vishva Hotel Ctm Cross Road |  | OCR empty (value not in OCR text) |
| baba_186798 | 0 at 22.01.34.jpeg | A | receipt_number | 186,798 | eGey | model wrong or a rule changed it (truth IS in the OCR text; raw model reply not stored) - flagged for review |
| baba_186798 | 0 at 22.01.34.jpeg | B | receipt_number | 186,798 | eGey | model wrong or a rule changed it (truth IS in the OCR text; raw model reply not stored) - flagged for review |
| baba_186798 | 0 at 22.01.34.jpeg | A | date | 01/06/2026 |  | OCR empty (value not in OCR text) |
| baba_186798 | 0 at 22.01.34.jpeg | B | date | 01/06/2026 |  | OCR empty (value not in OCR text) |
| baba_186798 | 0 at 22.01.34.jpeg | A | consignee_name | Ve Commercial | ToVe Commercial | model wrong or a rule changed it (truth IS in the OCR text; raw model reply not stored) |
| baba_186798 | 0 at 22.01.34.jpeg | B | consignee_name | Ve Commercial | ToVe Commercial | model wrong or a rule changed it (truth IS in the OCR text; raw model reply not stored) |
| baba_186798 | 0 at 22.01.34.jpeg | A | consignor_name | oerlikon, Ahmedabad | oerlikon | model wrong or a rule changed it (truth IS in the OCR text; raw model reply not stored) |
| baba_186798 | 0 at 22.01.34.jpeg | B | consignor_name | oerlikon, Ahmedabad |  | model/rules left it empty although the text has it |
| baba_186798 | 0 at 22.01.34.jpeg | A | time | 10:33:06 |  | model/rules left it empty although the text has it |
| baba_186798 | 0 at 22.01.34.jpeg | B | time | 10:33:06 |  | model/rules left it empty although the text has it |
| baba_p98250 |  22.01.37 (2).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p98250 |  22.01.37 (2).jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p98250 |  22.01.37 (2).jpeg | A | receipt_number | P98250 | 39T No. - 23AH0PS0492:12A | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98250 |  22.01.37 (2).jpeg | B | receipt_number | P98250 |  | OCR empty (value not in OCR text) |
| baba_p98250 |  22.01.37 (2).jpeg | A | date | 15/02/2025 |  | OCR empty (value not in OCR text) |
| baba_p98250 |  22.01.37 (2).jpeg | B | date | 15/02/2025 |  | OCR empty (value not in OCR text) |
| baba_p98250 |  22.01.37 (2).jpeg | A | consignee_name | Ve Commercial |  | model/rules left it empty although the text has it |
| baba_p98250 |  22.01.37 (2).jpeg | B | consignee_name | Ve Commercial |  | model/rules left it empty although the text has it |
| baba_p98250 |  22.01.37 (2).jpeg | A | prepared_by | Alok Sen |  | model/rules left it empty although the text has it |
| baba_p98250 |  22.01.37 (2).jpeg | B | prepared_by | Alok Sen |  | model/rules left it empty although the text has it |
| baba_p98250 |  22.01.37 (2).jpeg | A | package_description | Parcel | Parce! | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98250 |  22.01.37 (2).jpeg | B | package_description | Parcel | Parce! | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98506 | 0 at 22.01.37.jpeg | A | operator_name | BABA TRAVELS |  | OCR empty (value not in OCR text) |
| baba_p98506 | 0 at 22.01.37.jpeg | B | operator_name | BABA TRAVELS |  | OCR empty (value not in OCR text) |
| baba_p98506 | 0 at 22.01.37.jpeg | A | receipt_number | P98506 |  | OCR empty (value not in OCR text) |
| baba_p98506 | 0 at 22.01.37.jpeg | B | receipt_number | P98506 |  | OCR empty (value not in OCR text) |
| baba_p98506 | 0 at 22.01.37.jpeg | A | date | 25/02/2025 |  | OCR empty (value not in OCR text) |
| baba_p98506 | 0 at 22.01.37.jpeg | B | date | 25/02/2025 |  | OCR empty (value not in OCR text) |
| baba_p98506 |  22.01.40 (1).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p98506 |  22.01.40 (1).jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p98506 |  22.01.40 (1).jpeg | A | receipt_number | P98506 | YOLSHABAIIAVEL565 | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98506 |  22.01.40 (1).jpeg | B | receipt_number | P98506 | YOLSHABAIIAVEL565 | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98506 |  22.01.40 (1).jpeg | A | date | 25/02/2025 |  | OCR empty (value not in OCR text) |
| baba_p98506 |  22.01.40 (1).jpeg | B | date | 25/02/2025 |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | A | operator_name | BABA TRAVELS |  | model/rules left it empty although the text has it |
| baba_p98755 |  22.01.38 (1).jpeg | B | operator_name | BABA TRAVELS |  | model/rules left it empty although the text has it |
| baba_p98755 |  22.01.38 (1).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | A | receipt_number | P98755 |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | B | receipt_number | P98755 |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | A | date | 06/03/2025 |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | B | date | 06/03/2025 |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | A | to_place | Ahmedabad |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | B | to_place | Ahmedabad |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | A | consignee_name | Orlicon Blazer |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | B | consignee_name | Orlicon Blazer |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | A | consignor_name | Self |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | B | consignor_name | Self |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | A | package_count | 7 |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | B | package_count | 7 |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | A | payment_mode | Paid |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | B | payment_mode | Paid |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | A | total_amount | 700.00 |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | B | total_amount | 700.00 |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | A | prepared_by | Nitin Kothari |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | B | prepared_by | Nitin Kothari |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | A | consignee_phone | 0000000000 |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | B | consignee_phone | 0000000000 |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | A | package_description | Parcel |  | OCR empty (value not in OCR text) |
| baba_p98755 |  22.01.38 (1).jpeg | B | package_description | Parcel |  | OCR empty (value not in OCR text) |
| baba_p97394 |  22.01.38 (2).jpeg | A | date | 16/01/2025 | 16/01/2023 | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p97394 |  22.01.38 (2).jpeg | B | date | 16/01/2025 | 16/01/2023 | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98010 | 0 at 22.01.38.jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p98010 | 0 at 22.01.38.jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p98010 | 0 at 22.01.38.jpeg | A | receipt_number | P98010 |  | OCR empty (value not in OCR text) |
| baba_p98010 | 0 at 22.01.38.jpeg | B | receipt_number | P98010 |  | OCR empty (value not in OCR text) |
| baba_p98010 | 0 at 22.01.38.jpeg | A | date | 08/02/2025 |  | OCR empty (value not in OCR text) |
| baba_p98010 | 0 at 22.01.38.jpeg | B | date | 08/02/2025 |  | OCR empty (value not in OCR text) |
| baba_p98010 | 0 at 22.01.38.jpeg | A | prepared_by | Bobby | Bobb | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98010 | 0 at 22.01.38.jpeg | B | prepared_by | Bobby | Bobb | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p97300 |  22.01.39 (1).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p97300 |  22.01.39 (1).jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p97300 |  22.01.39 (1).jpeg | A | receipt_number | P97300 |  | model/rules left it empty although the text has it |
| baba_p97300 |  22.01.39 (1).jpeg | B | receipt_number | P97300 |  | model/rules left it empty although the text has it |
| baba_p97300 |  22.01.39 (1).jpeg | A | prepared_by | Rahul Sharma |  | OCR empty (value not in OCR text) |
| baba_p97300 |  22.01.39 (1).jpeg | B | prepared_by | Rahul Sharma |  | OCR empty (value not in OCR text) |
| baba_p97433 | 0 at 22.01.39.jpeg | A | prepared_by | Alok Sen |  | model/rules left it empty although the text has it |
| baba_p97433 | 0 at 22.01.39.jpeg | B | prepared_by | Alok Sen |  | model/rules left it empty although the text has it |
| baba_p98635 |  22.01.40 (2).jpeg | A | operator_name | BABA TRAVELS |  | model/rules left it empty although the text has it |
| baba_p98635 |  22.01.40 (2).jpeg | B | operator_name | BABA TRAVELS |  | model/rules left it empty although the text has it |
| baba_p98635 |  22.01.40 (2).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | A | receipt_number | P98635 |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | B | receipt_number | P98635 |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | A | date | 01/03/2025 |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | B | date | 01/03/2025 |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | A | to_place | Ahmedabad |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | B | to_place | Ahmedabad |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | A | consignee_name | Orlicon Blazer |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | B | consignee_name | Orlicon Blazer |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | A | consignor_name | Self |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | B | consignor_name | Self |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | A | package_count | 5 |  | model/rules left it empty although the text has it |
| baba_p98635 |  22.01.40 (2).jpeg | B | package_count | 5 |  | model/rules left it empty although the text has it |
| baba_p98635 |  22.01.40 (2).jpeg | A | payment_mode | Paid |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | B | payment_mode | Paid |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | A | total_amount | 500.00 |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | B | total_amount | 500.00 |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | A | prepared_by | Nitin Kothari |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | B | prepared_by | Nitin Kothari |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | A | consignee_phone | 0000000000 |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | B | consignee_phone | 0000000000 |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | A | package_description | Parcel |  | OCR empty (value not in OCR text) |
| baba_p98635 |  22.01.40 (2).jpeg | B | package_description | Parcel |  | OCR empty (value not in OCR text) |
| baba_p97990 | 0 at 22.01.40.jpeg | A | receipt_number | P97990 | 102/2025 | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p97990 | 0 at 22.01.40.jpeg | B | receipt_number | P97990 | 102/2025 | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p97990 | 0 at 22.01.40.jpeg | B | date | 07/02/2025 |  | model/rules left it empty although the text has it |
| baba_p97990 | 0 at 22.01.40.jpeg | A | consignee_name | Ve Commerical | Commerica! | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p97990 | 0 at 22.01.40.jpeg | B | consignee_name | Ve Commerical |  | OCR empty (value not in OCR text) |
| baba_p98828 |  22.01.41 (2).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p98828 |  22.01.41 (2).jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p98828 |  22.01.41 (2).jpeg | A | receipt_number | P98828 | 703/202 | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98828 |  22.01.41 (2).jpeg | B | receipt_number | P98828 | 703/202 | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98828 |  22.01.41 (2).jpeg | A | date | 10/03/2025 |  | OCR empty (value not in OCR text) |
| baba_p98828 |  22.01.41 (2).jpeg | B | date | 10/03/2025 |  | OCR empty (value not in OCR text) |
| baba_p98828 |  22.01.41 (2).jpeg | A | to_place | Ahmedabad |  | OCR empty (value not in OCR text) |
| baba_p98828 |  22.01.41 (2).jpeg | B | to_place | Ahmedabad |  | OCR empty (value not in OCR text) |
| baba_p98828 |  22.01.41 (2).jpeg | A | consignee_name | Ve Commercial |  | OCR empty (value not in OCR text) |
| baba_p98828 |  22.01.41 (2).jpeg | B | consignee_name | Ve Commercial |  | OCR empty (value not in OCR text) |
| baba_p98828 |  22.01.41 (2).jpeg | A | consignor_name | Self |  | OCR empty (value not in OCR text) |
| baba_p98828 |  22.01.41 (2).jpeg | B | consignor_name | Self |  | OCR empty (value not in OCR text) |
| baba_p98828 |  22.01.41 (2).jpeg | A | total_amount | 1000.00 | 000.00 | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98828 |  22.01.41 (2).jpeg | B | total_amount | 1000.00 | 000.00 | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98828 |  22.01.41 (2).jpeg | A | prepared_by | Rahul Sharma | anul-Sharma | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98828 |  22.01.41 (2).jpeg | B | prepared_by | Rahul Sharma | anul-Sharma | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p97829 | 0 at 22.01.41.jpeg | A | receipt_number | P97829 | B.0.27 | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p97829 | 0 at 22.01.41.jpeg | B | receipt_number | P97829 |  | OCR empty (value not in OCR text) |
| baba_p97829 | 0 at 22.01.41.jpeg | A | date | 01/02/2025 |  | OCR empty (value not in OCR text) |
| baba_p97829 | 0 at 22.01.41.jpeg | B | date | 01/02/2025 |  | OCR empty (value not in OCR text) |
| baba_p97829 | 0 at 22.01.41.jpeg | A | consignee_name | Ve Commercial |  | model/rules left it empty although the text has it |
| baba_p97829 | 0 at 22.01.41.jpeg | B | consignee_name | Ve Commercial |  | model/rules left it empty although the text has it |
| baba_p97829 | 0 at 22.01.41.jpeg | A | prepared_by | Alok Sen |  | OCR empty (value not in OCR text) |
| baba_p97829 | 0 at 22.01.41.jpeg | B | prepared_by | Alok Sen |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | A | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | B | operator_gstin | 23AHQPS8492M1ZA |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | A | receipt_number | P98595 |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | B | receipt_number | P98595 | 60 | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98595 |  22.01.54 (2).jpeg | A | date | 28/02/2025 | 03/04/2005 | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98595 |  22.01.54 (2).jpeg | B | date | 28/02/2025 | 03/04/2005 | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98595 |  22.01.54 (2).jpeg | A | to_place | Ahmedabad |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | B | to_place | Ahmedabad |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | A | consignee_name | Orlicon Blazer |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | B | consignee_name | Orlicon Blazer | RARA | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98595 |  22.01.54 (2).jpeg | A | consignor_name | Self |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | B | consignor_name | Self |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | A | package_count | 3 |  | model/rules left it empty although the text has it |
| baba_p98595 |  22.01.54 (2).jpeg | B | package_count | 3 |  | model/rules left it empty although the text has it |
| baba_p98595 |  22.01.54 (2).jpeg | A | payment_mode | Paid |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | B | payment_mode | Paid |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | A | total_amount | 300.00 |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | B | total_amount | 300.00 |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | A | prepared_by | Nitin Kothari | Nitin Kothan | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98595 |  22.01.54 (2).jpeg | B | prepared_by | Nitin Kothari | Nitin Kothan | OCR garbled (truth not in OCR text; value is the nearest misread) |
| baba_p98595 |  22.01.54 (2).jpeg | A | consignee_phone | 0000000000 |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | B | consignee_phone | 0000000000 |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | A | package_description | Parcel |  | OCR empty (value not in OCR text) |
| baba_p98595 |  22.01.54 (2).jpeg | B | package_description | Parcel |  | OCR empty (value not in OCR text) |

Total mismatch cells: 170 (Run A 85, Run B 85). By cause: {'model/rules left it empty although the text has it': 25, 'OCR empty': 114, 'OCR garbled': 26, 'model wrong or a rule changed it': 5}.

## 5. False values (truth empty, OCR non-empty, either run)

| receipt | photo | field | OCR Run A | OCR Run B |
|---|---|---|---|---|
| baba_p98250 |  22.01.37 (2).jpeg | remark | Subject to INDORE JurisdictionAlok Sen |  |
| baba_p97829 | 0 at 22.01.41.jpeg | from_place |  | Indore |
| baba_p98595 |  22.01.54 (2).jpeg | from_place | hmedabad | hmedabad |

Run A: 2/210 blank-truth cells filled anyway (1.0%) on the 18 scored receipts; rows listed (20 files): 3.

Run B: 2/210 blank-truth cells filled anyway (1.0%) on the 18 scored receipts; rows listed (20 files): 3.

## 6. Single vs bulk differences (Run A != Run B, same file)

| receipt | photo | field | actual | Run A | Run B |
|---|---|---|---|---|---|
| pawan_gr28625 |  22.01.42 (3).jpeg | from_place | INDORE | Indore | INDORE |
| pawan_gr41468 |  22.01.33 (2).jpeg | from_place | INDORE |  | Indore |
| baba_p8851_twocopy |  22.01.34 (3).jpeg | operator_gstin | 23AHQPS8492M1ZA |  | 23AHQP$8492M1ZA |
| baba_186798 | 0 at 22.01.34.jpeg | consignor_name | oerlikon, Ahmedabad | oerlikon |  |
| baba_p98250 |  22.01.37 (2).jpeg | receipt_number | P98250 | 39T No. - 23AH0PS0492:12A |  |
| baba_p98250 |  22.01.37 (2).jpeg | remark |  | Subject to INDORE JurisdictionAlok Sen |  |
| baba_p97990 | 0 at 22.01.40.jpeg | operator_name | BABA TRAVELS | BABA TRAVELS | Baba Travels |
| baba_p97990 | 0 at 22.01.40.jpeg | date | 07/02/2025 | 07/02/2025 |  |
| baba_p97990 | 0 at 22.01.40.jpeg | consignee_name | Ve Commerical | Commerica! |  |
| baba_p97829 | 0 at 22.01.41.jpeg | receipt_number | P97829 | B.0.27 |  |
| baba_p97829 | 0 at 22.01.41.jpeg | from_place |  |  | Indore |
| baba_p98595 |  22.01.54 (2).jpeg | operator_name | BABA TRAVELS | Baba Travels | BABA TRAVELS |
| baba_p98595 |  22.01.54 (2).jpeg | receipt_number | P98595 |  | 60 |
| baba_p98595 |  22.01.54 (2).jpeg | consignee_name | Orlicon Blazer |  | RARA |

Differing cells: 14 of 540 (checked cell by cell). Same code, prompt, model and temperature 0; Run B ran under a different user, so any difference is OCR/Groq run-to-run variation or the bulk path.

## 7. Speed and retries

- Run A (single, upload to processed, polled every 1 s): avg 24.1 s/doc (min 10.2, max 37.6) over 20 docs.
- Run B (bulk 4x5): batch wall times [127.6, 90.3, 98.8, 100.9] s => 20.9 s/doc throughput (per-doc time inside a batch includes queueing: avg 65.3 s, max 127.6 s).
- Retries / failures in the server log during the run: 0 line(s).
- Documents not `processed`: [('A', ' 22.01.38 (1).jpeg', 'failed'), ('A', ' 22.01.40 (2).jpeg', 'failed'), ('B', ' 22.01.38 (1).jpeg', 'failed'), ('B', ' 22.01.40 (2).jpeg', 'failed')].

## 8. Comparison: v1 recorded run, v2 (541acc1 rules replayed on the v1 raw rows), v3 (this run) - dev set, optimistic

v1 = the earlier real run (`spec/full_test_results.csv`, code before the post-processing rules). v2 = the same v1 rows passed through the `541acc1` rules (no new OCR/LLM, so it isolates the rules). v3 = new real run on the final code. Strict % and lenient %.

| scope | Run | v1 strict | v2 strict | v3 strict | v1 lenient | v2 lenient | v3 lenient |
|---|---|---|---|---|---|---|---|
| core | A | 54.9 | 54.9 | 63.2 | 54.9 | 54.9 | 63.2 |
| core | B | 53.4 | 53.4 | 62.7 | 53.4 | 53.4 | 62.7 |
| optional | A | 65.1 | 69.9 | 79.5 | 77.1 | 77.1 | 86.7 |
| optional | B | 62.7 | 67.5 | 80.7 | 74.7 | 74.7 | 88.0 |
| overall | A | 58.0 | 59.4 | 68.1 | 61.6 | 61.6 | 70.3 |
| overall | B | 56.2 | 57.6 | 68.1 | 59.8 | 59.8 | 70.3 |

Per field, Run A (strict %):

| field | n | v1 | v2 | v3 | change v2 -> v3 |
|---|---|---|---|---|---|
| operator_name | 18 | 83.3 | 83.3 | 83.3 | +0.0 |
| operator_gstin | 15 | 53.3 | 53.3 | 46.7 | -6.6 |
| receipt_number | 18 | 27.8 | 27.8 | 33.3 | +5.5 |
| date | 18 | 22.2 | 22.2 | 38.9 | +16.7 |
| to_place | 18 | 72.2 | 72.2 | 77.8 | +5.6 |
| consignee_name | 18 | 44.4 | 44.4 | 55.6 | +11.2 |
| consignor_name | 18 | 61.1 | 61.1 | 72.2 | +11.1 |
| package_count | 18 | 61.1 | 61.1 | 77.8 | +16.7 |
| payment_mode | 18 | 83.3 | 83.3 | 83.3 | +0.0 |
| total_amount | 18 | 72.2 | 72.2 | 77.8 | +5.6 |
| prepared_by | 16 | 18.8 | 18.8 | 43.8 | +25.0 |
| time | 5 | 0.0 | 60.0 | 60.0 | +0.0 |
| from_place | 3 | 66.7 | 66.7 | 66.7 | +0.0 |
| delivery_address | 4 | 0.0 | 25.0 | 25.0 | +0.0 |
| consignor_gstin | 3 | 100.0 | 100.0 | 100.0 | +0.0 |
| consignor_phone | 11 | 63.6 | 63.6 | 100.0 | +36.4 |
| consignee_gstin | 3 | 100.0 | 100.0 | 100.0 | +0.0 |
| consignee_phone | 17 | 76.5 | 76.5 | 82.4 | +5.9 |
| package_description | 18 | 50.0 | 50.0 | 61.1 | +11.1 |
| freight | 4 | 75.0 | 75.0 | 100.0 | +25.0 |
| delivery_charge | 1 | 100.0 | 100.0 | 100.0 | +0.0 |
| demurrage | 1 | 100.0 | 100.0 | 100.0 | +0.0 |
| sgst | 3 | 100.0 | 100.0 | 100.0 | +0.0 |
| cgst | 3 | 100.0 | 100.0 | 100.0 | +0.0 |
| igst | 3 | 100.0 | 100.0 | 100.0 | +0.0 |
| amount_in_words | 3 | 100.0 | 100.0 | 100.0 | +0.0 |
| remark | 1 | 0.0 | 0.0 | 0.0 | +0 |

Per field, Run B (strict %):

| field | n | v1 | v2 | v3 | change v2 -> v3 |
|---|---|---|---|---|---|
| operator_name | 18 | 77.8 | 77.8 | 83.3 | +5.5 |
| operator_gstin | 15 | 53.3 | 53.3 | 46.7 | -6.6 |
| receipt_number | 18 | 27.8 | 27.8 | 33.3 | +5.5 |
| date | 18 | 22.2 | 22.2 | 33.3 | +11.1 |
| to_place | 18 | 72.2 | 72.2 | 77.8 | +5.6 |
| consignee_name | 18 | 38.9 | 38.9 | 55.6 | +16.7 |
| consignor_name | 18 | 61.1 | 61.1 | 72.2 | +11.1 |
| package_count | 18 | 55.6 | 55.6 | 77.8 | +22.2 |
| payment_mode | 18 | 77.8 | 77.8 | 83.3 | +5.5 |
| total_amount | 18 | 72.2 | 72.2 | 77.8 | +5.6 |
| prepared_by | 16 | 25.0 | 25.0 | 43.8 | +18.8 |
| time | 5 | 0.0 | 60.0 | 60.0 | +0.0 |
| from_place | 3 | 66.7 | 66.7 | 100.0 | +33.3 |
| delivery_address | 4 | 0.0 | 25.0 | 25.0 | +0.0 |
| consignor_gstin | 3 | 100.0 | 100.0 | 100.0 | +0.0 |
| consignor_phone | 11 | 72.7 | 72.7 | 100.0 | +27.3 |
| consignee_gstin | 3 | 100.0 | 100.0 | 100.0 | +0.0 |
| consignee_phone | 17 | 64.7 | 64.7 | 82.4 | +17.7 |
| package_description | 18 | 44.4 | 44.4 | 61.1 | +16.7 |
| freight | 4 | 100.0 | 100.0 | 100.0 | +0.0 |
| delivery_charge | 1 | 100.0 | 100.0 | 100.0 | +0.0 |
| demurrage | 1 | 100.0 | 100.0 | 100.0 | +0.0 |
| sgst | 3 | 66.7 | 66.7 | 100.0 | +33.3 |
| cgst | 3 | 100.0 | 100.0 | 100.0 | +0.0 |
| igst | 3 | 100.0 | 100.0 | 100.0 | +0.0 |
| amount_in_words | 3 | 100.0 | 100.0 | 100.0 | +0.0 |
| remark | 1 | 0.0 | 0.0 | 0.0 | +0 |

The 4 photos that had no receipt number / date before:

| receipt | run | version | receipt_number | date | core fields filled (of 11) | core strict-correct (of 11) |
|---|---|---|---|---|---|---|
| baba_p98755 | A | v1 |  |  | 0 | 0 |
| baba_p98755 | A | v2 |  |  | 0 | 0 |
| baba_p98755 | A | v3 |  |  | 0 | 0 |
| baba_p98755 | B | v1 |  |  | 0 | 0 |
| baba_p98755 | B | v2 |  |  | 0 | 0 |
| baba_p98755 | B | v3 |  |  | 0 | 0 |
| baba_p98635 | A | v1 |  |  | 0 | 0 |
| baba_p98635 | A | v2 |  |  | 0 | 0 |
| baba_p98635 | A | v3 |  |  | 0 | 0 |
| baba_p98635 | B | v1 |  |  | 0 | 0 |
| baba_p98635 | B | v2 |  |  | 0 | 0 |
| baba_p98635 | B | v3 |  |  | 0 | 0 |
| baba_p98828 | A | v1 | 703/202 |  | 5 | 3 |
| baba_p98828 | A | v2 | 703/202 |  | 5 | 3 |
| baba_p98828 | A | v3 | 703/202 |  | 6 | 3 |
| baba_p98828 | B | v1 |  |  | 0 | 0 |
| baba_p98828 | B | v2 |  |  | 0 | 0 |
| baba_p98828 | B | v3 | 703/202 |  | 6 | 3 |
| baba_p98595 | A | v1 |  |  | 1 | 1 |
| baba_p98595 | A | v2 |  |  | 1 | 1 |
| baba_p98595 | A | v3 |  | 03/04/2005 | 3 | 1 |
| baba_p98595 | B | v1 |  |  | 1 | 1 |
| baba_p98595 | B | v2 |  |  | 1 | 1 |
| baba_p98595 | B | v3 | 60 | 03/04/2005 | 5 | 1 |

**Fields that got worse v2 -> v3 (strict):** {'A': ['operator_gstin'], 'B': ['operator_gstin']}.

Cells right in v2 and wrong in v3 (strict), both runs:

| run | receipt | field | actual | v2 | v3 |
|---|---|---|---|---|---|
| A | baba_p98250 | operator_gstin | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA |  |
| A | baba_p98506 | operator_name | BABA TRAVELS | Baba Travels |  |
| B | baba_p98250 | operator_gstin | 23AHQPS8492M1ZA | 23AHQPS8492M1ZA |  |

## 9. Stored-document checks (read back from the real database)

### Run A user

- documents stored: 20; statuses: {'failed': 2, 'processed': 18}; summary endpoint counts: total 20, processed 18, failed 2
- isDuplicate = true on 2 docs: [(' 22.01.42 (3).jpeg', '28625'), (' 22.01.33 (1).jpeg', '28625')]
  - Pawan GR28625 pair (2 photos): 2 docs read with that receipt number, isDuplicate = [True, True] -> BOTH flagged
  - Baba P98506 pair (2 photos): 0 docs read with that receipt number, isDuplicate = [] -> NOT both flagged (see note)
- documents with warnings or review flags:
  -  22.01.33 (1).jpeg (28625): flags=[]; warnings=['receiptNumber|Possible duplicate: same operator, receipt numbe']
  -  22.01.34 (3).jpeg (-): flags=[]; warnings=['receiptNumber|Receipt number missing', 'date|Date missing']
  - 0 at 22.01.34.jpeg (eGey): flags=['receiptNumberNeedsReview']; warnings=['receiptNumber|Receipt number looks incomplete', 'date|Date missing']
  -  22.01.37 (2).jpeg (39T No. - 23AH0PS0492:12A): flags=['receiptNumberNeedsReview']; warnings=['receiptNumber|Receipt number looks incomplete', 'date|Date missing']
  - 0 at 22.01.37.jpeg (-): flags=[]; warnings=['receiptNumber|Receipt number missing', 'date|Date missing']
  -  22.01.38 (1).jpeg (-): flags=[]; warnings=['receiptNumber|Receipt number missing', 'date|Date missing', 'totalAmount|Total amount missing']
  - 0 at 22.01.38.jpeg (-): flags=[]; warnings=['receiptNumber|Receipt number missing', 'date|Date missing']
  -  22.01.39 (1).jpeg (-): flags=[]; warnings=['receiptNumber|Receipt number missing']
  -  22.01.40 (1).jpeg (YOLSHABAIIAVEL565): flags=['receiptNumberNeedsReview']; warnings=['receiptNumber|Receipt number looks incomplete', 'date|Date missing']
  -  22.01.40 (2).jpeg (-): flags=[]; warnings=['receiptNumber|Receipt number missing', 'date|Date missing', 'totalAmount|Total amount missing']
  - 0 at 22.01.40.jpeg (102/2025): flags=['receiptNumberNeedsReview']; warnings=['receiptNumber|Receipt number looks incomplete']
  -  22.01.41 (2).jpeg (703/202): flags=['receiptNumberNeedsReview', 'preparedByNeedsReview']; warnings=['receiptNumber|Receipt number looks incomplete', 'date|Date missing']
  - 0 at 22.01.41.jpeg (B.0.27): flags=['receiptNumberNeedsReview']; warnings=['receiptNumber|Receipt number looks incomplete', 'date|Date missing']
  -  22.01.42 (3).jpeg (28625): flags=[]; warnings=['receiptNumber|Possible duplicate: same operator, receipt numbe']
  -  22.01.54 (2).jpeg (-): flags=['dateNeedsReview', 'fromPlaceNeedsReview']; warnings=['receiptNumber|Receipt number missing', 'date|Date looks implausible', 'totalAmount|Total amount missing']
- needs-review filter (?needsReview=true) returned 13 of 20 documents. Expected by its documented rule (any NeedsReview flag, a flagged duplicate, or a processed document with receipt number/date/total empty): 13. Expected but missing from the filter: none; in the filter but not expected: none. Failed documents are not in this filter by design (they show as Failed): 2.
- failed / unreadable documents: [(' 22.01.40 (2).jpeg', 'OCR_UNREADABLE', 'We could not read this photo. Try a clearer photo or retry.'), (' 22.01.38 (1).jpeg', 'OCR_UNREADABLE', 'We could not read this photo. Try a clearer photo or retry.')]

### Run B user

- documents stored: 20; statuses: {'failed': 2, 'processed': 18}; summary endpoint counts: total 20, processed 18, failed 2
- isDuplicate = true on 2 docs: [(' 22.01.42 (3).jpeg', '28625'), (' 22.01.33 (1).jpeg', '28625')]
  - Pawan GR28625 pair (2 photos): 2 docs read with that receipt number, isDuplicate = [True, True] -> BOTH flagged
  - Baba P98506 pair (2 photos): 0 docs read with that receipt number, isDuplicate = [] -> NOT both flagged (see note)
- documents with warnings or review flags:
  -  22.01.33 (1).jpeg (28625): flags=[]; warnings=['receiptNumber|Possible duplicate: same operator, receipt numbe']
  -  22.01.34 (3).jpeg (-): flags=['operatorGstinNeedsReview']; warnings=['receiptNumber|Receipt number missing', 'date|Date missing', 'operatorGstin|Operator GSTIN format looks wrong']
  - 0 at 22.01.34.jpeg (eGey): flags=['receiptNumberNeedsReview']; warnings=['receiptNumber|Receipt number looks incomplete', 'date|Date missing']
  -  22.01.37 (2).jpeg (-): flags=[]; warnings=['receiptNumber|Receipt number missing', 'date|Date missing']
  - 0 at 22.01.37.jpeg (-): flags=[]; warnings=['receiptNumber|Receipt number missing', 'date|Date missing']
  -  22.01.38 (1).jpeg (-): flags=[]; warnings=['receiptNumber|Receipt number missing', 'date|Date missing', 'totalAmount|Total amount missing']
  - 0 at 22.01.38.jpeg (-): flags=[]; warnings=['receiptNumber|Receipt number missing', 'date|Date missing']
  -  22.01.39 (1).jpeg (-): flags=[]; warnings=['receiptNumber|Receipt number missing']
  -  22.01.40 (1).jpeg (YOLSHABAIIAVEL565): flags=['receiptNumberNeedsReview']; warnings=['receiptNumber|Receipt number looks incomplete', 'date|Date missing']
  -  22.01.40 (2).jpeg (-): flags=[]; warnings=['receiptNumber|Receipt number missing', 'date|Date missing', 'totalAmount|Total amount missing']
  - 0 at 22.01.40.jpeg (102/2025): flags=['receiptNumberNeedsReview']; warnings=['receiptNumber|Receipt number looks incomplete', 'date|Date missing']
  -  22.01.41 (2).jpeg (703/202): flags=['receiptNumberNeedsReview', 'preparedByNeedsReview']; warnings=['receiptNumber|Receipt number looks incomplete', 'date|Date missing']
  - 0 at 22.01.41.jpeg (-): flags=['fromPlaceNeedsReview']; warnings=['receiptNumber|Receipt number missing', 'date|Date missing']
  -  22.01.42 (3).jpeg (28625): flags=[]; warnings=['receiptNumber|Possible duplicate: same operator, receipt numbe']
  -  22.01.54 (2).jpeg (60): flags=['dateNeedsReview', 'receiptNumberNeedsReview', 'fromPlaceNeedsReview']; warnings=['receiptNumber|Receipt number looks incomplete', 'date|Date looks implausible', 'totalAmount|Total amount missing']
- needs-review filter (?needsReview=true) returned 13 of 20 documents. Expected by its documented rule (any NeedsReview flag, a flagged duplicate, or a processed document with receipt number/date/total empty): 13. Expected but missing from the filter: none; in the filter but not expected: none. Failed documents are not in this filter by design (they show as Failed): 2.
- failed / unreadable documents: [(' 22.01.40 (2).jpeg', 'OCR_UNREADABLE', 'We could not read this photo. Try a clearer photo or retry.'), (' 22.01.38 (1).jpeg', 'OCR_UNREADABLE', 'We could not read this photo. Try a clearer photo or retry.')]

