"""Deterministic post-AI rules (dates/time, receipt number, text, GST/phone). No AI call.
Flag only when unsure; rewrite only when the repair is mechanically certain."""
import pytest

from app.features.ocr.extraction import build_extraction_result as build

# ---------------- GROUP 1: date and time ----------------


@pytest.mark.parametrize("raw,want", [
    ("05 MAR 2026", "05/03/2026"), ("5-Mar-25", "05/03/2025"), ("5 March 2026", "05/03/2026"),
    ("12.Sept.2025", "12/09/2025"), ("03 0CT 2025", "03/10/2025"),
])
def test_month_name_dates(raw, want):
    out = build({"date": raw})
    assert out["date"] == want and out["dateNeedsReview"] is False


def test_month_name_ambiguous_noise_flagged_value_kept():
    out = build({"date": "05 MAX 2026"})  # MAR or MAY
    assert out["date"] == "05 MAX 2026" and out["dateNeedsReview"] is True


def test_month_name_garbage_flagged():
    assert build({"date": "05 XYZ 2026"})["dateNeedsReview"] is True


def test_month_name_invalid_day_not_normalized():
    out = build({"date": "31 FEB 2026"})
    assert out["date"] == "31 FEB 2026" and out["dateNeedsReview"] is True


def test_trailing_time_split_into_empty_time():
    out = build({"date": "21/04/2026 17:17:59"})
    assert out["date"] == "21/04/2026" and out["time"] == "17:17:59"
    out = build({"date": "05 MAR 2026 11:25 AM"})
    assert out["date"] == "05/03/2026" and out["time"] == "11:25 AM"


def test_trailing_time_never_overwrites_existing_time():
    out = build({"date": "21/04/2026 17:17:59", "time": "9:00 AM"})
    assert out["date"] == "21/04/2026" and out["time"] == "9:00 AM"


def test_slash_misread_repaired_only_when_real_date():
    out = build({"date": "17701/2025"})
    assert out["date"] == "17/01/2025" and out["dateAutoCorrected"] is True
    assert build({"date": "17101/2025"})["date"] == "17/01/2025"
    assert build({"date": "31/0112025"})["date"] == "31/01/2025"


def test_slash_misread_unreal_date_left_and_flagged():
    out = build({"date": "32701/2025"})
    assert out["date"] == "32701/2025" and out["dateNeedsReview"] is True
    out = build({"date": "17713/2025"})  # month 13
    assert out["date"] == "17713/2025" and out["dateNeedsReview"] is True


def test_clean_date_untouched():
    out = build({"date": "13/01/2025"})
    assert out["date"] == "13/01/2025" and out["dateAutoCorrected"] is False and out["dateNeedsReview"] is False


def test_baba_month_name_date_flagged_but_parsed():
    out = build({"date": "05 MAR 2025", "operatorName": "Baba Travels"})
    assert out["date"] == "05/03/2025" and out["dateNeedsReview"] is True
    assert build({"date": "05 MAR 2025", "operatorName": "PAWAN TRAVELS"})["dateNeedsReview"] is False
    assert build({"date": "05/03/2025", "operatorName": "Baba Travels"})["dateNeedsReview"] is False


@pytest.mark.parametrize("raw,want", [
    ("11:25AM", "11:25 AM"), ("12:45pm", "12:45 PM"), ("10:04 AM", "10:04 AM"), ("9:05 a.m.", "9:05 AM"),
    ("17:17:59", "17:17:59"), ("7:05:09", "07:05:09"), ("17:17", "17:17"),
])
def test_time_normalized(raw, want):
    out = build({"time": raw})
    assert out["time"] == want and out["timeNeedsReview"] is False


@pytest.mark.parametrize("raw", ["13:45 PM", "0:30 AM", "25:10:00", "12:60 PM", "10:10:75", "ab:cd"])
def test_time_out_of_range_kept_and_flagged(raw):
    out = build({"time": raw})
    assert out["time"] == raw and out["timeNeedsReview"] is True


def test_time_blank_no_flag():
    assert build({})["timeNeedsReview"] is False


def test_break_attempts_group1():
    # Baba numeric date with baked-in 24h time: clean, not flagged
    out = build({"date": "21/04/2026 17:17:59", "operatorName": "BABA TRAVELS"})
    assert (out["date"], out["time"], out["dateNeedsReview"], out["timeNeedsReview"]) == (
        "21/04/2026", "17:17:59", False, False)
    out = build({"date": "1 MAR 25 5:30 pm"})
    assert (out["date"], out["time"]) == ("01/03/2025", "5:30 PM")
    # invalid baked-in time: moved as-is and flagged, never silently normalised
    out = build({"date": "21/04/2026 25:99:00"})
    assert out["date"] == "21/04/2026" and out["time"] == "25:99:00" and out["timeNeedsReview"] is True
    # whole-number AI value and None don't crash
    assert build({"date": 17701, "time": None})["date"] == "17701"


# ---------------- GROUP 2: receipt number ----------------


@pytest.mark.parametrize("raw,want", [
    ("GrNo28625", "28625"), ("Gr No 28625", "28625"), ("gr no: 28625", "28625"),
    ("R No 41468", "41468"), ("RNo41468", "41468"), ("Receipt No P98250", "P98250"),
    ("RECEIPT NO. 38420", "38420"),
])
def test_receipt_label_prefix_stripped(raw, want):
    out = build({"receiptNumber": raw})
    assert out["receiptNumber"] == want and out["receiptNumberNeedsReview"] is False


@pytest.mark.parametrize("val", ["28625", "P8851", "P98250", "123456", "186,798", "1,86,798"])
def test_valid_receipt_shapes_kept_as_printed_not_flagged(val):
    out = build({"receiptNumber": val})
    assert out["receiptNumber"] == val and out["receiptNumberNeedsReview"] is False


@pytest.mark.parametrize("raw,want", [("PO1234", "P01234"), ("PS8851", "P58851"), ("Pl2345", "P12345"), ("P9O25O", "P90250"),
    ("P9X250", None), ("PD1234", None), ("2862S", None)])
def test_confusion_fix_only_in_digit_part_after_leading_p(raw, want):
    out = build({"receiptNumber": raw})
    if want:
        assert out["receiptNumber"] == want and out["receiptNumberNeedsReview"] is False
    else:  # any other letter/digit mixing is not guess-fixed
        assert out["receiptNumber"] == raw and out["receiptNumberNeedsReview"] is True


@pytest.mark.parametrize("val", ["B.0.27", "OLSHASIAVEL", "02/2025", "703/202", "2862S", "O8625", "PP1234", "P123", "1234"])
def test_other_shapes_flagged_value_kept(val):
    out = build({"receiptNumber": val})
    assert out["receiptNumber"] == val and out["receiptNumberNeedsReview"] is True


def test_label_only_becomes_blank_unflagged():
    assert build({"receiptNumber": "GrNo"})["receiptNumber"] == ""


# ---------------- GROUP 3: text fields ----------------


@pytest.mark.parametrize("raw,want", [
    ("MAYARAM JI8087536777", "MAYARAM JI 8087536777"),
    ("MAYARAMJI8087536777", "MAYARAMJI 8087536777"),
    ("MAYARAM JI 8087536777", "MAYARAM JI 8087536777"),   # already spaced: untouched
    ("Veer Travels Opp Vishva Hotel Ctm Cross Road", "Veer Travels Opp Vishva Hotel Ctm Cross Road"),
    ("Shop 12 Main Rd", "Shop 12 Main Rd"),
    ("JI80875367771", "JI80875367771"),                    # 11 digits is not a phone: untouched
    ("JI808753677", "JI808753677"),                         # 9 digits: untouched
])
def test_delivery_address_phone_space(raw, want):
    assert build({"deliveryAddress": raw})["deliveryAddress"] == want


@pytest.mark.parametrize("raw,want,flag", [
    ("(PAWAN)", "PAWAN", False), ("PAWAN", "PAWAN", False), ("(Shresth Sharma)", "Shresth Sharma", False),
    ("A. K. Sen", "A. K. Sen", False), ("(PAWAN", "(PAWAN", True), ("PAWAN)", "PAWAN)", True),
    ("PAWAN2", "PAWAN2", True), ("(Rahul 5)", "Rahul 5", True), ("Al0k Sen", "Al0k Sen", True),
])
def test_prepared_by(raw, want, flag):
    out = build({"preparedBy": raw})
    assert out["preparedBy"] == want and out["preparedByNeedsReview"] is flag


@pytest.mark.parametrize("field", ["consignorName", "consigneeName", "toPlace", "fromPlace"])
def test_digit_contamination_flagged_never_fixed(field):
    out = build({field: "K1INGELBERG 1ND1A"})
    assert out[field] == "K1INGELBERG 1ND1A" and out[f"{field}NeedsReview"] is True
    out = build({field: "KLINGELBERG INDIA"})
    assert out[field] == "KLINGELBERG INDIA" and out[f"{field}NeedsReview"] is False
    assert build({})[f"{field}NeedsReview"] is False


def test_baba_from_place_must_be_empty():
    assert build({"operatorName": "BABA TRAVELS", "fromPlace": "INDORE"})["fromPlaceNeedsReview"] is True
    assert build({"operatorName": "BABA TRAVELS", "fromPlace": ""})["fromPlaceNeedsReview"] is False
    assert build({"operatorName": "PAWAN TRAVELS", "fromPlace": "INDORE"})["fromPlaceNeedsReview"] is False
    assert build({"operatorName": "", "fromPlace": "INDORE"})["fromPlaceNeedsReview"] is False


@pytest.mark.parametrize("raw,want", [
    ("Baba Travels", "Baba Travels"),                 # clean case-variant: left as read
    ("BABA TRAVELS, INDORE PT", "BABA TRAVELS"),
    ("pawan travels , Indore PT.", "pawan travels"), ("Pawan", "PAWAN TRAVELS"),
    ("Baba Travel", "BABA TRAVELS"), ("PAWAN TRAVELS", "PAWAN TRAVELS"),
    ("ELSLASA TRAVELS", "ELSLASA TRAVELS"),           # unknown: never guessed
    ("Veer Travels", "Veer Travels"),
])
def test_operator_name_snap(raw, want):
    assert build({"operatorName": raw})["operatorName"] == want


def test_operator_both_names_not_snapped():
    assert build({"operatorName": "Pawan Baba Travels"})["operatorName"] == "Pawan Baba Travels"


def test_baba_rules_see_snapped_operator():
    out = build({"operatorName": "Baba Travels, INDORE PT", "date": "05 MAR 2025"})
    assert out["dateNeedsReview"] is True


# ---------------- GROUP 4: GST and phone ----------------

REAL = ("27AAECK1993K1Z3", "23AABCE9378F3ZI", "23AHQPS8492M1ZA", "27AAPFU0939F1ZV")


@pytest.mark.parametrize("g", REAL)
def test_valid_checksum_not_flagged(g):
    out = build({"consignorGstin": g})
    assert out["consignorGstin"] == g and out["consignorGstinNeedsReview"] is False
    assert out["consignorGstinAutoCorrected"] is False


def test_checksum_fail_no_single_fix_flagged_value_kept():
    bad = "27AAECK1993K1Z4"  # wrong check char; the only "fix" would be a non-confusion char
    out = build({"consigneeGstin": bad})
    assert out["consigneeGstin"] == bad and out["consigneeGstinNeedsReview"] is True
    assert out["consigneeGstinAutoCorrected"] is False


@pytest.mark.parametrize("good,bad", [
    ("23AABCE9378F3ZI", "23AABCE9378F3Z1"),   # checksum char I misread as 1
    ("23AHQPS8492M1ZA", "23AHQP58492M1ZA"),   # S read as 5 (wrong shape too)
    ("27AAPFU0939F1ZV", "27AAPFUO939F1ZV"),   # 0 read as O
])
def test_single_confusion_fix_repairs_and_marks_autocorrected(good, bad):
    out = build({"consignorGstin": bad})
    assert out["consignorGstin"] == good
    assert out["consignorGstinAutoCorrected"] is True and out["consignorGstinNeedsReview"] is False


def test_ambiguous_or_multi_fix_only_flags():
    # two confusable characters both wrong (O for 0 and S for 5): one fix cannot pass -> flag
    out = build({"consignorGstin": "23AHQP58492M1ZA".replace("8492", "84O2")})
    assert out["consignorGstinNeedsReview"] is True and out["consignorGstinAutoCorrected"] is False


def test_operator_gstin_checked_too_and_blank_untouched():
    assert build({"operatorGstin": "23AHQPS8492M1ZA"})["operatorGstinNeedsReview"] is False
    assert build({"operatorGstin": "23AHQP8492M1ZA"})["operatorGstinNeedsReview"] is True  # 14 chars
    assert build({})["operatorGstinNeedsReview"] is False


@pytest.mark.parametrize("raw,want", [
    ("+918518888766", "8518888766"), ("918518888766", "8518888766"), ("08518888766", "8518888766"),
    ("+91 85188 88766", "8518888766"), ("8518888766", "8518888766"), ("9198765432", "9198765432"),
])
def test_phone_prefix_stripped_valid(raw, want):
    out = build({"consignorPhone": raw})
    assert out["consignorPhone"] == want and out["consignorPhoneNeedsReview"] is False


@pytest.mark.parametrize("raw", ["0000000000", "00", "000000000"])
def test_placeholder_zero_phone_valid(raw):
    out = build({"consigneePhone": raw})
    assert out["consigneePhone"] == raw and out["consigneePhoneNeedsReview"] is False


@pytest.mark.parametrize("raw", ["5518888766", "851888876", "85188887661", "1234567890", "+91518888766", "123"])
def test_phone_bad_flagged(raw):
    assert build({"consignorPhone": raw})["consignorPhoneNeedsReview"] is True


def test_sgst_cgst_must_match():
    out = build({"sgst": "9", "cgst": "9"})
    assert out["sgstNeedsReview"] is False and out["cgstNeedsReview"] is False
    out = build({"sgst": "9", "cgst": "4.5"})
    assert out["sgstNeedsReview"] is True and out["cgstNeedsReview"] is True
    out = build({"sgst": "9.0", "cgst": "9"})  # numerically equal
    assert out["sgstNeedsReview"] is False
    out = build({"sgst": "9", "cgst": ""})  # one blank: no comparison
    assert out["sgstNeedsReview"] is False


def test_igst_and_cgst_sgst_both_nonzero_is_a_break():
    out = build({"igst": "18", "sgst": "9", "cgst": "9"})
    assert all(out[f"{f}NeedsReview"] for f in ("igst", "sgst", "cgst"))
    out = build({"igst": "18", "sgst": "0", "cgst": "0"})
    assert not any(out[f"{f}NeedsReview"] for f in ("igst", "sgst", "cgst"))
    out = build({"igst": "0", "sgst": "9", "cgst": "9"})
    assert not any(out[f"{f}NeedsReview"] for f in ("igst", "sgst", "cgst"))
    out = build({"igst": "18"})
    assert out["igstNeedsReview"] is False
