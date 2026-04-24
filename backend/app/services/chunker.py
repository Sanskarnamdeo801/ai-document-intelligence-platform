from typing import List, Tuple


class TextChunker:
    def __init__(self, chunk_word_size: int = 350, overlap_words: int = 60):
        if overlap_words >= chunk_word_size:
            raise ValueError("overlap_words must be smaller than chunk_word_size")
        self.chunk_word_size = chunk_word_size
        self.overlap_words = overlap_words

    def chunk_text(self, text: str, page_num: int | None = None) -> List[Tuple[str, int, int | None]]:
        words = text.split()
        if not words:
            return []

        chunks: List[Tuple[str, int, int | None]] = []
        step = self.chunk_word_size - self.overlap_words

        for start in range(0, len(words), step):
            chunk_words = words[start : start + self.chunk_word_size]
            chunk_text = " ".join(chunk_words).strip()
            if not chunk_text:
                continue
            token_count = max(1, round(len(chunk_text) / 4))
            chunks.append((chunk_text, token_count, page_num))
            if start + self.chunk_word_size >= len(words):
                break

        return chunks

    def chunk_pages(self, pages: List[Tuple[str, int | None]]) -> List[Tuple[str, int, int, int | None]]:
        all_chunks: List[Tuple[str, int, int, int | None]] = []
        chunk_index = 0

        for page_text, page_number in pages:
            for chunk_text, token_count, chunk_page in self.chunk_text(page_text, page_number):
                if not chunk_text.strip():
                    continue
                all_chunks.append((chunk_text, chunk_index, token_count, chunk_page))
                chunk_index += 1

        return all_chunks
