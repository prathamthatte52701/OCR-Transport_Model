"""Task 1: Baba (red-ink) pages OCR a red-channel gray copy AND a dark-ink-only copy and merge
the two texts; every other page (Pawan, blue ink) keeps the single original OCR pass."""
from unittest.mock import patch

import cv2
import numpy as np
import pytest

from app.features.ocr import pipeline
from app.features.ocr.preprocessing import (
    RED_INK_STEP,
    assess_and_preprocess,
    red_ink_variants,
)


def _png(img: np.ndarray) -> bytes:
    return cv2.imencode(".png", img)[1].tobytes()


def _decode(b: bytes) -> np.ndarray:
    return cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)


def _red_page() -> np.ndarray:
    """White paper, a pale-red watermark band, black typed ink on top of it."""
    img = np.full((400, 1200, 3), 255, np.uint8)
    img[60:140, 50:1150] = (190, 190, 255)  # BGR pale red watermark
    img[260:340, 50:1150] = (190, 190, 255)  # mirrored so no quadrant is brighter than the rest
    img[100:130, 100:500] = (0, 0, 0)  # black typed ink on the watermark
    img[270:300, 700:1100] = (0, 0, 0)
    img[170:230, 50:1150] = (40, 40, 230)  # strong red print
    return img


def _blue_page() -> np.ndarray:
    img = np.full((400, 1200, 3), 255, np.uint8)
    img[100:130, 100:500] = (200, 60, 20)  # blue ink (BGR)
    return img


def test_red_page_gets_marker_step_and_no_other_pixel_step(monkeypatch):
    from app.features.ocr import preprocessing

    # Isolate the red-page branch: no deskew / illumination work on the synthetic fixture.
    monkeypatch.setattr(preprocessing, "_deskew", lambda img, gray: (img, 0.0))
    monkeypatch.setattr(preprocessing, "_quadrant_brightness_delta", lambda gray: 0.0)
    png = _png(_red_page())
    out, steps = assess_and_preprocess(png)
    assert RED_INK_STEP in steps
    assert not {"adaptive_watermark_suppress", "clahe_contrast"} & set(steps)
    assert out == png  # marker only, no pixel work, no re-encode


def test_blue_page_never_gets_marker():
    _, steps = assess_and_preprocess(_png(_blue_page()))
    assert RED_INK_STEP not in steps


def test_variants_separate_black_ink_from_red_watermark():
    gray_png, ink_png = red_ink_variants(_png(_red_page()))
    ink = _decode(ink_png)[..., 0]
    assert set(np.unique(ink)) <= {0, 255}
    assert ink[115, 200] == 0  # black ink stays dark
    assert ink[80, 800] == 255  # pale-red watermark drops to white
    gray = _decode(gray_png)
    assert (gray[..., 0] == gray[..., 1]).all() and (gray[..., 1] == gray[..., 2]).all()
    assert gray[80, 800, 0] > 150  # watermark bright in the red channel
    assert gray[115, 200, 0] < 40  # black ink dark in the red channel


def test_variants_refuse_undecodable_bytes():
    with pytest.raises(ValueError):
        red_ink_variants(b"not an image")


async def _run(steps, image_bytes, ocr_results, variants=None):
    calls: list[str] = []
    results = iter(ocr_results)

    def fake_run_ocr(path, **_kw):
        calls.append(path)
        r = next(results)
        if isinstance(r, Exception):
            raise r
        return r

    async def fake_slot(fn, timeout):
        return fn()

    async def fake_norm(buf):
        return buf

    patches = [
        patch.object(pipeline, "_normalize_photo_page", fake_norm),
        patch.object(pipeline, "crop_header", lambda b: b),
        patch.object(pipeline, "crop_left_copy", lambda b: b),
        patch.object(pipeline, "assess_and_preprocess", lambda b: (image_bytes, steps)),
        patch.object(pipeline, "_run_in_slot", fake_slot),
        patch.object(pipeline, "run_ocr", fake_run_ocr),
        patch.object(pipeline.cv2, "imdecode", lambda *a, **k: object()),
    ]
    if variants is not None:
        patches.append(patch.object(pipeline, "red_ink_variants", variants))
    for p in patches:
        p.start()
    try:
        text = await pipeline._extract_header_text(b"orig", "image/jpeg")
    finally:
        for p in patches:
            p.stop()
    return text, calls


async def test_non_red_page_runs_one_pass_and_text_is_untouched():
    text, calls = await _run([], b"img", ["PAWAN TRAVELS\nGR 28625"])
    assert text == "PAWAN TRAVELS\nGR 28625"
    assert len(calls) == 1


async def test_red_page_runs_both_variants_and_merges_in_order():
    text, calls = await _run(
        [RED_INK_STEP], b"img", ["red gray text", "dark ink text"], variants=lambda b: (b"g", b"d")
    )
    assert len(calls) == 2
    lines = text.split("\n")
    assert lines[0] == "red gray text"
    assert lines[-1] == "dark ink text"
    assert sum(1 for ln in lines if ln.startswith("#")) == 1  # one source comment, nothing else added


async def test_red_page_second_pass_empty_keeps_first_text():
    text, _ = await _run([RED_INK_STEP], b"img", ["red gray text", None], variants=lambda b: (b"g", b"d"))
    assert text == "red gray text"


async def test_red_page_variant_build_failure_falls_back_to_single_original_pass():
    def boom(b):
        raise ValueError("bad")

    text, calls = await _run([RED_INK_STEP], b"img", ["orig text"], variants=boom)
    assert text == "orig text"
    assert len(calls) == 1


async def test_red_page_both_passes_empty_returns_none():
    text, _ = await _run([RED_INK_STEP], b"img", [None, None], variants=lambda b: (b"g", b"d"))
    assert text is None
