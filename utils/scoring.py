"""
AI Content Intelligence System — Content Scoring Engine
Unified 0–100 quality score combining readability, engagement, clarity, and SEO.
"""

from utils.readability import flesch_reading_ease
from utils.cleaner import (
    count_words, count_sentences, count_paragraphs,
    average_sentence_length, split_sentences,
)
from utils.tone import analyze_sentiment
from config import SCORING_WEIGHTS


def score_readability(text):
    """Score readability component (0–100)."""
    fre = flesch_reading_ease(text)
    # Ideal range is 50–70 for general content
    if 50 <= fre <= 80:
        return min(100, fre + 20)
    elif fre > 80:
        return 90  # very easy, slightly penalize for oversimplicity
    elif fre >= 30:
        return fre + 10
    else:
        return max(20, fre)


def score_engagement(text):
    """
    Score engagement based on structure, variety, and rhetorical features.
    """
    score = 50  # base
    sentences = split_sentences(text)
    words = count_words(text)
    paragraphs = count_paragraphs(text)

    # Sentence variety (standard deviation of sentence lengths)
    if sentences:
        lengths = [len(s.split()) for s in sentences]
        avg = sum(lengths) / len(lengths)
        variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
        std_dev = variance ** 0.5

        # Good variety = std_dev between 3 and 10
        if 3 <= std_dev <= 10:
            score += 15
        elif std_dev > 1:
            score += 8

    # Paragraph structure
    if paragraphs >= 3:
        score += 10
    elif paragraphs >= 2:
        score += 5

    # Content length bonus
    if 300 <= words <= 2500:
        score += 15
    elif words > 100:
        score += 8

    # Question marks (engagement)
    if "?" in text:
        score += 5

    # Exclamation marks (energy — but not too many)
    excl_count = text.count("!")
    if 1 <= excl_count <= 3:
        score += 5
    elif excl_count > 5:
        score -= 5  # too many = unprofessional

    return max(0, min(100, score))


def score_clarity(text):
    """
    Score clarity based on sentence length, passive voice indicators,
    and word complexity.
    """
    score = 60  # base
    avg_sent_len = average_sentence_length(text)
    sentences = split_sentences(text)

    # Optimal sentence length: 15–20 words
    if 12 <= avg_sent_len <= 22:
        score += 20
    elif avg_sent_len <= 30:
        score += 10
    else:
        score -= 10  # sentences too long

    # Check for passive voice indicators
    passive_indicators = [" was ", " were ", " been ", " being ", " is being ", " are being "]
    text_lower = text.lower()
    passive_count = sum(text_lower.count(p) for p in passive_indicators)
    sentence_count = max(1, len(sentences))
    passive_ratio = passive_count / sentence_count

    if passive_ratio < 0.15:
        score += 10  # mostly active voice
    elif passive_ratio > 0.4:
        score -= 10  # too much passive

    # Transition words (improve clarity)
    transition_words = [
        "however", "therefore", "moreover", "furthermore",
        "in addition", "for example", "in contrast", "as a result",
        "consequently", "on the other hand", "similarly", "specifically",
    ]
    transition_count = sum(1 for tw in transition_words if tw in text_lower)
    if transition_count >= 3:
        score += 10
    elif transition_count >= 1:
        score += 5

    return max(0, min(100, score))


def score_seo_basic(text):
    """
    Basic SEO score based on content structure.
    """
    score = 40  # base
    words = count_words(text)
    sentences = count_sentences(text)
    paragraphs = count_paragraphs(text)

    # Word count (300–2000 ideal for articles)
    if 300 <= words <= 2000:
        score += 25
    elif words > 100:
        score += 15
    elif words > 50:
        score += 5

    # Paragraph structure
    if paragraphs >= 3:
        score += 15
    elif paragraphs >= 2:
        score += 8

    # Sentence count
    if sentences >= 5:
        score += 10
    elif sentences >= 3:
        score += 5

    # Heading indicators
    if any(line.startswith("#") for line in text.split("\n")):
        score += 10

    return max(0, min(100, score))


def compute_content_score(text):
    """
    Compute the unified content quality score (0–100).
    Weights defined in config.SCORING_WEIGHTS.
    """
    r_score = score_readability(text)
    e_score = score_engagement(text)
    c_score = score_clarity(text)
    s_score = score_seo_basic(text)

    weighted = (
        r_score * SCORING_WEIGHTS["readability"]
        + e_score * SCORING_WEIGHTS["engagement"]
        + c_score * SCORING_WEIGHTS["clarity"]
        + s_score * SCORING_WEIGHTS["seo"]
    )

    return {
        "overall": round(weighted, 1),
        "readability": round(r_score, 1),
        "engagement": round(e_score, 1),
        "clarity": round(c_score, 1),
        "seo": round(s_score, 1),
    }


def get_score_label(score):
    """Get human-readable label for a score."""
    if score >= 85:
        return {"label": "Excellent", "color": "#00E676", "emoji": "🏆"}
    elif score >= 70:
        return {"label": "Good", "color": "#66BB6A", "emoji": "✅"}
    elif score >= 55:
        return {"label": "Average", "color": "#FFA726", "emoji": "⚠️"}
    elif score >= 40:
        return {"label": "Below Average", "color": "#EF5350", "emoji": "📉"}
    else:
        return {"label": "Poor", "color": "#B71C1C", "emoji": "❌"}
