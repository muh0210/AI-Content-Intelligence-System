"""
AI Content Intelligence System — Content DNA Fingerprinting (V4)
Analyze writing style patterns and generate a unique "Content DNA" profile.
"""

import re
import numpy as np
from collections import Counter
from utils.cleaner import (
    split_sentences, count_words, average_sentence_length,
    average_word_length,
)


def sentence_length_variation(text):
    """Measure sentence length variation (std dev)."""
    sentences = split_sentences(text)
    if len(sentences) < 2:
        return {"std_dev": 0, "min": 0, "max": 0, "avg": 0, "variation_label": "N/A"}

    lengths = [len(s.split()) for s in sentences]
    std = float(np.std(lengths))
    avg = float(np.mean(lengths))

    if std > 8:
        label = "High Variety"
        color = "#00E676"
    elif std > 4:
        label = "Moderate Variety"
        color = "#FFA726"
    else:
        label = "Low Variety (Monotonous)"
        color = "#EF5350"

    return {
        "std_dev": round(std, 1),
        "min": min(lengths),
        "max": max(lengths),
        "avg": round(avg, 1),
        "variation_label": label,
        "color": color,
        "lengths": lengths,
    }


def vocabulary_richness(text):
    """Compute vocabulary richness metrics."""
    words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
    total = len(words)
    unique = len(set(words))

    if total == 0:
        return {"ttr": 0, "hapax": 0, "label": "N/A"}

    ttr = unique / total  # Type-Token Ratio
    freq = Counter(words)
    hapax = sum(1 for w, c in freq.items() if c == 1)  # Words used only once
    hapax_ratio = hapax / total

    if ttr > 0.7:
        label, color = "Very Rich", "#00E676"
    elif ttr > 0.5:
        label, color = "Rich", "#66BB6A"
    elif ttr > 0.35:
        label, color = "Moderate", "#FFA726"
    else:
        label, color = "Limited", "#EF5350"

    return {
        "ttr": round(ttr * 100, 1),
        "hapax_ratio": round(hapax_ratio * 100, 1),
        "unique_words": unique,
        "total_words": total,
        "label": label,
        "color": color,
    }


def passive_active_ratio(text):
    """Calculate passive vs active voice ratio."""
    sentences = split_sentences(text)
    passive_indicators = [
        r"\bwas\s+\w+ed\b", r"\bwere\s+\w+ed\b", r"\bbeen\s+\w+ed\b",
        r"\bis\s+being\b", r"\bare\s+being\b", r"\bwas\s+being\b",
        r"\bhas\s+been\b", r"\bhave\s+been\b", r"\bhad\s+been\b",
    ]

    passive_count = 0
    for sent in sentences:
        for pattern in passive_indicators:
            if re.search(pattern, sent.lower()):
                passive_count += 1
                break

    total = len(sentences) if sentences else 1
    passive_pct = (passive_count / total) * 100
    active_pct = 100 - passive_pct

    if passive_pct > 40:
        style = "Passive-Heavy"
        color = "#EF5350"
    elif passive_pct > 20:
        style = "Mixed"
        color = "#FFA726"
    else:
        style = "Active-Dominant"
        color = "#00E676"

    return {
        "passive_pct": round(passive_pct, 1),
        "active_pct": round(active_pct, 1),
        "passive_count": passive_count,
        "total_sentences": total,
        "style": style,
        "color": color,
    }


def paragraph_rhythm(text):
    """Analyze paragraph length patterns."""
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 10]
    if len(paragraphs) < 2:
        paragraphs = [p.strip() for p in text.split("\n") if len(p.strip()) > 10]

    if len(paragraphs) < 2:
        return {"rhythm": "Single Block", "lengths": [], "color": "#FFA726"}

    lengths = [len(p.split()) for p in paragraphs]
    std = float(np.std(lengths))
    avg = float(np.mean(lengths))

    if std > 20:
        rhythm = "Dynamic"
        color = "#00E676"
    elif std > 10:
        rhythm = "Moderate"
        color = "#66BB6A"
    else:
        rhythm = "Uniform"
        color = "#FFA726"

    return {
        "rhythm": rhythm,
        "lengths": lengths,
        "avg_length": round(avg, 1),
        "std": round(std, 1),
        "total_paragraphs": len(paragraphs),
        "color": color,
    }


def word_complexity_distribution(text):
    """Analyze distribution of word complexity by syllable count."""
    words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())

    def count_syllables(word):
        vowels = "aeiou"
        count = 0
        prev_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        return max(1, count)

    if not words:
        return {"distribution": {}, "avg_syllables": 0}

    syllable_counts = [count_syllables(w) for w in words]
    dist = Counter(syllable_counts)

    return {
        "distribution": {f"{k}-syl": v for k, v in sorted(dist.items())},
        "avg_syllables": round(sum(syllable_counts) / len(syllable_counts), 2),
        "complex_word_pct": round(sum(1 for s in syllable_counts if s >= 3) / len(syllable_counts) * 100, 1),
    }


def get_content_dna(text):
    """Generate complete Content DNA profile."""
    sent_var = sentence_length_variation(text)
    vocab = vocabulary_richness(text)
    voice = passive_active_ratio(text)
    rhythm = paragraph_rhythm(text)
    complexity = word_complexity_distribution(text)

    # DNA Radar scores (0-100 scale for visualization)
    radar = {
        "Sentence Variety": min(100, sent_var["std_dev"] * 10),
        "Vocabulary Richness": vocab["ttr"],
        "Active Voice": voice["active_pct"],
        "Paragraph Rhythm": min(100, rhythm.get("std", 0) * 5),
        "Word Simplicity": max(0, 100 - complexity.get("complex_word_pct", 0) * 2),
    }

    return {
        "sentence_variation": sent_var,
        "vocabulary": vocab,
        "voice": voice,
        "rhythm": rhythm,
        "complexity": complexity,
        "radar": radar,
    }


def compare_dna(dna_a, dna_b):
    """Compare two Content DNA profiles for brand voice consistency."""
    if not dna_a.get("radar") or not dna_b.get("radar"):
        return {"match_score": 0, "details": []}

    metrics = list(dna_a["radar"].keys())
    diffs = []
    for m in metrics:
        a = dna_a["radar"].get(m, 50)
        b = dna_b["radar"].get(m, 50)
        diff = abs(a - b)
        diffs.append({
            "metric": m,
            "a": round(a, 1),
            "b": round(b, 1),
            "diff": round(diff, 1),
            "match": "Strong" if diff < 10 else "Moderate" if diff < 25 else "Weak",
        })

    avg_diff = sum(d["diff"] for d in diffs) / len(diffs) if diffs else 50
    match_score = max(0, min(100, 100 - avg_diff))

    return {
        "match_score": round(match_score, 1),
        "details": diffs,
        "verdict": "Consistent" if match_score > 75 else "Somewhat Similar" if match_score > 50 else "Different Voices",
    }
