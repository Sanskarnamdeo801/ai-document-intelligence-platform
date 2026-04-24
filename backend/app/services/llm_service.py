import json
from typing import Any, Dict, List

import requests

from ..core.config import settings
from ..core.logging_config import logger


class LLMService:
    def __init__(self):
        self.model = settings.OLLAMA_MODEL
        self.host = settings.OLLAMA_HOST.rstrip("/")

    def generate_summary(self, chunks: List[str]) -> str:
        context = self._build_context(chunks, max_chunks=6)
        fallback_summary = self._fallback_summary(chunks)
        if not context:
            return fallback_summary

        prompt = (
            "Summarize this document in concise prose. "
            "Mention the main purpose, key obligations or findings, important entities, and notable dates.\n\n"
            f"Document context:\n{context}"
        )
        return self._generate(prompt, fallback=fallback_summary)

    def extract_metadata(self, chunks: List[str]) -> Dict[str, Any]:
        context = self._build_context(chunks, max_chunks=4)
        default_metadata = self._default_metadata(chunks)
        if not context:
            return default_metadata

        prompt = (
            "Extract metadata from the following document context as strict JSON only. "
            'Return keys: title, doc_type, parties, effective_date, expiration_date, tags, language. '
            "Use arrays for parties and tags. Use null for missing dates.\n\n"
            f"Document context:\n{context}"
        )
        raw_response = self._generate(
            prompt,
            fallback=json.dumps(default_metadata),
            response_format="json",
        )
        return self._parse_metadata(raw_response, default_metadata)

    def answer_question(self, question: str, context_chunks: List[str]) -> str:
        context = self._build_context(context_chunks, max_chunks=5)
        if not context:
            return "I do not have enough document context to answer that question."

        prompt = (
            "Answer the question using only the provided document context. "
            "If the answer is not supported, say that clearly.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        )
        return self._generate(
            prompt,
            fallback="The answer could not be generated from the retrieved document context.",
        )

    def _generate(self, prompt: str, fallback: str, response_format: str | None = None) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if response_format:
            payload["format"] = response_format

        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            body = response.json()
            generated = (body.get("response") or "").strip()
            return generated or fallback
        except Exception as exc:
            logger.warning("Ollama request failed, using fallback response: %s", exc)
            return fallback

    def _parse_metadata(self, raw_response: str, default_metadata: Dict[str, Any]) -> Dict[str, Any]:
        candidate = raw_response.strip()
        if not candidate:
            return default_metadata

        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            start = candidate.find("{")
            end = candidate.rfind("}")
            if start == -1 or end == -1 or end <= start:
                return default_metadata
            try:
                parsed = json.loads(candidate[start : end + 1])
            except json.JSONDecodeError:
                return default_metadata

        if not isinstance(parsed, dict):
            return default_metadata

        return {
            "title": str(parsed.get("title") or default_metadata["title"]),
            "doc_type": str(parsed.get("doc_type") or default_metadata["doc_type"]),
            "parties": self._ensure_list(parsed.get("parties")) or default_metadata["parties"],
            "effective_date": self._optional_string(parsed.get("effective_date")),
            "expiration_date": self._optional_string(parsed.get("expiration_date")),
            "tags": self._ensure_list(parsed.get("tags")) or default_metadata["tags"],
            "language": str(parsed.get("language") or default_metadata["language"]),
        }

    def _fallback_summary(self, chunks: List[str]) -> str:
        source_text = self._build_context(chunks, max_chunks=3)
        if not source_text:
            return "No extractable content was found in the document."
        fallback = source_text[:1000].strip()
        return fallback if fallback.endswith(".") else f"{fallback}..."

    def _default_metadata(self, chunks: List[str]) -> Dict[str, Any]:
        title = "Untitled document"
        if chunks:
            first_line = next((line.strip() for line in chunks[0].splitlines() if line.strip()), "")
            if first_line:
                title = first_line[:255]

        return {
            "title": title,
            "doc_type": "unknown",
            "parties": [],
            "effective_date": None,
            "expiration_date": None,
            "tags": [],
            "language": "en",
        }

    def _build_context(self, chunks: List[str], max_chunks: int) -> str:
        return "\n\n".join(chunk for chunk in chunks[:max_chunks] if chunk and chunk.strip()).strip()

    def _ensure_list(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return [str(value).strip()] if str(value).strip() else []

    def _optional_string(self, value: Any) -> str | None:
        if value in (None, "", "null"):
            return None
        return str(value).strip() or None
