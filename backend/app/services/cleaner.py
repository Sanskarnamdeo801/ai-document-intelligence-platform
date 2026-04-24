import re
from typing import List, Tuple


class TextCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""

        cleaned = text.replace("\ufeff", " ").replace("\x00", " ")
        cleaned = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", cleaned)
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n[ \t]+", "\n", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    @classmethod
    def clean_pages(cls, pages: List[Tuple[str, int | None]]) -> List[Tuple[str, int | None]]:
        cleaned_pages: List[Tuple[str, int | None]] = []
        for text, page_number in pages:
            cleaned_text = cls.clean_text(text)
            if cleaned_text.strip():
                cleaned_pages.append((cleaned_text, page_number))
        return cleaned_pages
