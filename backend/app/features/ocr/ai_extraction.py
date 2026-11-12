from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.features.ocr.extraction import (
    EXTRACTION_VALUE_FIELDS,
    build_extraction_result,
    empty_extraction_result,
)
from app.features.ocr.json_parsing import parse_extraction_json
from app.features.ocr.providers.base import AIProvider
from app.features.ocr.providers.errors import BAD_REPLY, AIExtractionError
from app.features.ocr.providers.groq_provider import GroqProvider

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_env = Environment(loader=FileSystemLoader(str(_PROMPTS_DIR)), autoescape=False)
_TEMPLATE = "transport_receipt.j2"


async def extract_header(
    header_text: str | None,
    provider: AIProvider | None = None,
) -> dict:
    if not header_text or not header_text.strip():
        return empty_extraction_result()

    provider = provider or GroqProvider()
    system_prompt = _env.get_template(_TEMPLATE).render(field_count=len(EXTRACTION_VALUE_FIELDS))
    user_prompt = f"Extract from this bus luggage/parcel receipt OCR text:\n\n{header_text}"

    # The model occasionally returns an empty/truncated reply (or JSON that is not an object);
    # one retry fixes it. A second bad reply is a BAD_REPLY failure, never a crash.
    async def ask() -> dict:
        raw = await provider.extract(system_prompt, user_prompt)
        try:
            parsed = parse_extraction_json(raw)
        except (RecursionError, TypeError) as exc:  # absurdly nested / odd JSON from the model
            raise ValueError("AI reply could not be parsed") from exc
        if not isinstance(parsed, dict):
            raise ValueError("AI reply is not a JSON object")
        return parsed

    try:
        parsed = await ask()
    except ValueError:
        try:
            parsed = await ask()
        except ValueError:
            raise AIExtractionError(BAD_REPLY) from None
    return build_extraction_result(parsed)
