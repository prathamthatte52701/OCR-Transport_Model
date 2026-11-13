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
