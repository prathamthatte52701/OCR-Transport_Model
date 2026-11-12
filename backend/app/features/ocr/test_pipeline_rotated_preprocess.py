"""I7: a rotated photo (normalize_photo returns different bytes) must still go through
quality-gated preprocessing. The old `cut_from_background` skip dated from the paper-crop
step, which is disabled; the flag had silently become "was rotated"."""
from unittest.mock import patch

from app.features.ocr import pipeline


async def test_rotated_photo_still_gets_preprocessing():
    calls = []

    async def fake_norm(buf):
        return b"rotated-" + buf

    def fake_assess(b):
        calls.append(b)
        return b, []

    async def fake_slot(fn, timeout):
        return "text"

    with patch.object(pipeline, "_normalize_photo_page", fake_norm), \
         patch.object(pipeline, "crop_header", lambda b: b), \
         patch.object(pipeline, "crop_left_copy", lambda b: b), \
         patch.object(pipeline, "assess_and_preprocess", fake_assess), \
         patch.object(pipeline, "_run_in_slot", fake_slot), \
         patch.object(pipeline.cv2, "imdecode", lambda *a, **k: object()):
        await pipeline._extract_header_text(b"orig", "image/jpeg")
    assert calls, "preprocessing skipped for a rotated photo"
