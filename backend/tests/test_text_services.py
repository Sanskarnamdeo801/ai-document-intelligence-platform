from app.services.chunker import TextChunker
from app.services.cleaner import TextCleaner


def test_chunker_creates_non_empty_chunks():
    chunker = TextChunker(chunk_word_size=8, overlap_words=2)
    text = "one two three four five six seven eight nine ten eleven twelve"

    chunks = chunker.chunk_text(text, page_num=3)

    assert len(chunks) >= 2
    assert all(chunk_text.strip() for chunk_text, _, _ in chunks)
    assert chunks[0][2] == 3


def test_cleaner_does_not_erase_valid_text():
    raw_text = "Heading\x00\n\nThis   is   a valid test.\n\nSecond paragraph."

    cleaned = TextCleaner.clean_text(raw_text)

    assert cleaned
    assert "Heading" in cleaned
    assert "This is a valid test." in cleaned
    assert "Second paragraph." in cleaned
