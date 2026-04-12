"""
AI Content Intelligence System — SEO Analysis Module
Keyword density, top keywords, and headline optimization.
"""

import re
from collections import Counter
from config import SEO_STOP_WORDS


def tokenize(text):
    """Tokenize text into lowercase words, removing punctuation."""
    words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
    return words


def keyword_density(text, top_n=15):
    """
    Compute keyword density for all meaningful words.
    Returns top N keywords with count and density %.
    """
    words = tokenize(text)
    filtered = [w for w in words if w not in SEO_STOP_WORDS]
    total = len(filtered)

    if total == 0:
        return []

    freq = Counter(filtered)
    top_keywords = freq.most_common(top_n)

    return [
        {
            "keyword": kw,
            "count": count,
            "density": round((count / total) * 100, 2),
        }
        for kw, count in top_keywords
    ]


def extract_bigrams(text, top_n=10):
    """Extract top N two-word phrases (bigrams)."""
    words = tokenize(text)
    filtered = [w for w in words if w not in SEO_STOP_WORDS]

    if len(filtered) < 2:
        return []

    bigrams = [f"{filtered[i]} {filtered[i+1]}" for i in range(len(filtered) - 1)]
    freq = Counter(bigrams)

    return [
        {"phrase": phrase, "count": count}
        for phrase, count in freq.most_common(top_n)
        if count >= 2
    ]


def analyze_headline(headline):
    """
    Analyze a headline for SEO effectiveness.
    Returns score and suggestions.
    """
    suggestions = []
    score = 50  # base

    words = headline.split()
    word_count = len(words)
    char_count = len(headline)

    # Length check (ideal: 6–12 words, 50–60 chars)
    if 6 <= word_count <= 12:
        score += 15
    elif word_count < 4:
        suggestions.append("Headline is too short. Aim for 6–12 words.")
    elif word_count > 15:
        suggestions.append("Headline is too long. Keep it under 12 words.")
    else:
        score += 8

    if 40 <= char_count <= 65:
        score += 10
    elif char_count > 70:
        suggestions.append("Keep headline under 65 characters for best display in search results.")

    # Power words
    power_words = [
        "ultimate", "essential", "proven", "powerful", "complete",
        "comprehensive", "expert", "advanced", "best", "top",
        "guide", "secrets", "tips", "strategies", "how",
    ]
    has_power = any(pw in headline.lower() for pw in power_words)
    if has_power:
        score += 10
    else:
        suggestions.append("Consider adding a power word (e.g., 'Ultimate', 'Proven', 'Essential').")

    # Number presence
    if any(char.isdigit() for char in headline):
        score += 10
    else:
        suggestions.append("Headlines with numbers tend to get more clicks (e.g., '7 Ways to...').")

    # Emotional triggers
    emotion_words = ["amazing", "incredible", "shocking", "surprising", "critical", "vital"]
    if any(ew in headline.lower() for ew in emotion_words):
        score += 5

    if not suggestions:
        suggestions.append("Great headline! It follows SEO best practices.")

    return {
        "score": min(100, score),
        "word_count": word_count,
        "char_count": char_count,
        "suggestions": suggestions,
    }


def get_seo_report(text, title=""):
    """
    Generate a comprehensive SEO analysis report.
    """
    keywords = keyword_density(text)
    bigrams = extract_bigrams(text)

    report = {
        "keywords": keywords,
        "bigrams": bigrams,
        "total_words": len(tokenize(text)),
        "unique_words": len(set(tokenize(text))),
        "vocabulary_richness": 0,
    }

    if report["total_words"] > 0:
        report["vocabulary_richness"] = round(
            report["unique_words"] / report["total_words"] * 100, 1
        )

    if title:
        report["headline_analysis"] = analyze_headline(title)

    return report
