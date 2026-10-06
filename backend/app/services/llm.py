import json
import random
import time
from typing import Type, Any
from pydantic import BaseModel
from ..config import settings


class GeminiUnavailableError(RuntimeError):
    """Raised when Gemini is temporarily unavailable after retries."""


def _gemini_schema(schema: Type[BaseModel]) -> dict[str, Any]:
    raw = schema.model_json_schema()

    def clean(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: clean(item) for key, item in value.items() if key != "additionalProperties"}
        if isinstance(value, list):
            return [clean(item) for item in value]
        return value

    return clean(raw)


def _is_transient(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(token in text for token in ("503", "unavailable", "high demand", "429", "resource exhausted", "500", "internal server error", "temporarily"))


class GeminiService:
    def __init__(self):
        self.client = None
        if settings.gemini_api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=settings.gemini_api_key)
            except Exception:
                self.client = None

    @property
    def available(self):
        return self.client is not None

    def generate_json(self, prompt: str, schema: Type[BaseModel]) -> dict:
        if not self.client:
            raise GeminiUnavailableError("Gemini API is not configured")

        last_exc = None
        # Gemini can return transient 429/500/503 errors. Retry before allowing
        # the agent layer to switch to its explicit Demo Mode fallback.
        for attempt in range(4):
            try:
                response = self.client.models.generate_content(
                    model=settings.gemini_model,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": _gemini_schema(schema),
                    },
                )
                text = getattr(response, "text", None) or "{}"
                return json.loads(text)
            except Exception as exc:
                last_exc = exc
                if not _is_transient(exc) or attempt == 3:
                    break
                delay = min(16, 2 ** attempt) + random.uniform(0.2, 0.8)
                time.sleep(delay)

        if last_exc is not None and _is_transient(last_exc):
            raise GeminiUnavailableError(
                "Gemini is temporarily unavailable after 4 retries; the analysis pipeline can use its explicit fallback."
            ) from last_exc
        raise last_exc
