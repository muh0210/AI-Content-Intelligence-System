"""
AI Content Intelligence System — Text Cleaning Module
Normalizes and prepares text for NLP analysis.
"""

import re
import unicodedata


def clean_text(text):
    """
    Comprehensive text cleaning pipeline.
    Normalizes whitespace, removes control chars, fixes encoding artifacts.
    """
    if not text or not text.strip():
        return ""

    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)

    # Remove control characters (keep newlines and tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    # Replace multiple spaces with single space
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize line breaks
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()


def split_sentences(text):
    """Split text into sentences using regex heuristics."""
    if not text:
        return []

    # Split on sentence-ending punctuation followed by space or end
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def split_paragraphs(text):
    """Split text into paragraphs."""
    if not text:
        return []

    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


def count_words(text):
    """Count words in text."""
    if not text:
        return 0
    return len(text.split())


def count_sentences(text):
    """Count sentences in text."""
    return len(split_sentences(text))


def count_paragraphs(text):
    """Count paragraphs in text."""
    return len(split_paragraphs(text))


def count_characters(text, include_spaces=True):
    """Count characters in text."""
    if not text:
        return 0
    if include_spaces:
        return len(text)
    return len(text.replace(" ", ""))


def average_word_length(text):
    """Calculate average word length."""
    words = text.split()
    if not words:
        return 0
    return sum(len(w) for w in words) / len(words)


def average_sentence_length(text):
    """Calculate average sentence length in words."""
    sentences = split_sentences(text)
    if not sentences:
        return 0
    word_counts = [len(s.split()) for s in sentences]
    return sum(word_counts) / len(word_counts)


def get_text_stats(text):
    """Return a comprehensive dictionary of text statistics."""
    cleaned = clean_text(text)
    words = count_words(cleaned)
    sentences = count_sentences(cleaned)
    paragraphs = count_paragraphs(cleaned)
    chars_with = count_characters(cleaned, True)
    chars_without = count_characters(cleaned, False)
    avg_word = round(average_word_length(cleaned), 1)
    avg_sent = round(average_sentence_length(cleaned), 1)

    return {
        "words": words,
        "sentences": sentences,
        "paragraphs": paragraphs,
        "characters": chars_with,
        "characters_no_spaces": chars_without,
        "avg_word_length": avg_word,
        "avg_sentence_length": avg_sent,
        "reading_time_min": round(words / 200, 1),  # avg 200 wpm
    }
