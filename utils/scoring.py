"""
AI Content Intelligence System — Content Scoring Engine (V2 — Upgraded)
Unified 0–100 quality score with domain-aware presets and dynamic weights.
"""

from utils.readability import flesch_reading_ease
from utils.cleaner import (
    count_words, count_sentences, count_paragraphs,
    average_sentence_length, split_sentences,
)
from utils.tone import analyze_sentiment
from config import SCORING_WEIGHTS


# ═══════════════════════════════════════════════════════════════════
# Domain-Aware Scoring Presets
# ═══════════════════════════════════════════════════════════════════

DOMAIN_PRESETS = {
    "general": {
        "label": "📝 General Content",
        "weights": {"readability": 0.30, "engagement": 0.25, "clarity": 0.25, "seo": 0.20},
        "ideal_readability": (50, 80),
        "ideal_sentence_length": (12, 22),
    },
    "academic": {
        "label": "🎓 Academic / Thesis",
        "weights": {"readability": 0.15, "engagement": 0.15, "clarity": 0.40, "seo": 0.30},
        "ideal_readability": (30, 60),
        "ideal_sentence_length": (15, 30),
    },
    "blog": {
        "label": "📰 Blog / Article",
        "weights": {"readability": 0.30, "engagement": 0.30, "clarity": 0.20, "seo": 0.20},
        "ideal_readability": (60, 90),
        "ideal_sentence_length": (10, 20),
    },
    "business": {
        "label": "💼 Business / Professional",
        "weights": {"readability": 0.25, "engagement": 0.20, "clarity": 0.35, "seo": 0.20},
        "ideal_readability": (45, 70),
        "ideal_sentence_length": (12, 25),
    },
    "seo": {
        "label": "🔍 SEO-Optimized",
        "weights": {"readability": 0.20, "engagement": 0.25, "clarity": 0.15, "seo": 0.40},
        "ideal_readability": (55, 75),
        "ideal_sentence_length": (12, 20),
    },
    "viral": {
        "label": "🚀 Viral / Social Media",
        "weights": {"readability": 0.30, "engagement": 0.40, "clarity": 0.15, "seo": 0.15},
        "ideal_readability": (70, 95),
        "ideal_sentence_length": (8, 15),
    },
    # V4: Industry-Specific Profiles
    "financial": {
        "label": "💰 Financial Reports",
        "weights": {"readability": 0.10, "engagement": 0.10, "clarity": 0.45, "seo": 0.35},
        "ideal_readability": (25, 50),
        "ideal_sentence_length": (15, 30),
    },
    "marketing": {
        "label": "📣 Marketing Copy",
        "weights": {"readability": 0.25, "engagement": 0.40, "clarity": 0.15, "seo": 0.20},
        "ideal_readability": (65, 90),
        "ideal_sentence_length": (8, 16),
    },
    "legal": {
        "label": "⚖️ Legal Documents",
        "weights": {"readability": 0.05, "engagement": 0.05, "clarity": 0.50, "seo": 0.40},
        "ideal_readability": (20, 45),
        "ideal_sentence_length": (18, 35),
    },
    "academic_paper": {
        "label": "📄 Academic Papers",
        "weights": {"readability": 0.10, "engagement": 0.10, "clarity": 0.45, "seo": 0.35},
        "ideal_readability": (25, 55),
        "ideal_sentence_length": (16, 30),
    },
    "upwork": {
        "label": "💼 Upwork Proposals",
        "weights": {"readability": 0.30, "engagement": 0.35, "clarity": 0.25, "seo": 0.10},
        "ideal_readability": (65, 85),
        "ideal_sentence_length": (10, 18),
    },
}


def score_readability(text, ideal_range=(50, 80)):
    """Score readability component (0–100)."""
    fre = flesch_reading_ease(text)
    low, high = ideal_range

    if low <= fre <= high:
        return min(100, 70 + (fre - low) / (high - low) * 30)
    elif fre > high:
        return max(70, 100 - (fre - high) * 0.5)
    elif fre >= low - 20:
        return max(40, 50 + (fre - (low - 20)) / 20 * 20)
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

    # Sentence variety
    if sentences:
        lengths = [len(s.split()) for s in sentences]
        avg = sum(lengths) / len(lengths)
        variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
        std_dev = variance ** 0.5

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

    # Questions (engagement)
    question_count = text.count("?")
    if 1 <= question_count <= 5:
        score += 5 + min(question_count, 3)

    # Exclamation marks (energy)
    excl_count = text.count("!")
    if 1 <= excl_count <= 3:
        score += 5
    elif excl_count > 5:
        score -= 5

    # Lists / bullet points
    if any(line.strip().startswith(("-", "•", "*", "1.")) for line in text.split("\n")):
        score += 5

    return max(0, min(100, score))


def score_clarity(text, ideal_sentence_length=(12, 22)):
    """
    Score clarity based on sentence length, passive voice indicators,
    transition words, and word complexity.
    """
    score = 60  # base
    avg_sent_len = average_sentence_length(text)
    sentences = split_sentences(text)
    low, high = ideal_sentence_length

    # Optimal sentence length
    if low <= avg_sent_len <= high:
        score += 20
    elif avg_sent_len <= high + 8:
        score += 10
    else:
        score -= 10

    # Passive voice indicators
    passive_indicators = [" was ", " were ", " been ", " being ", " is being ", " are being "]
    text_lower = text.lower()
    passive_count = sum(text_lower.count(p) for p in passive_indicators)
    sentence_count = max(1, len(sentences))
    passive_ratio = passive_count / sentence_count

    if passive_ratio < 0.15:
        score += 10
    elif passive_ratio > 0.4:
        score -= 10

    # Transition words
    transition_words = [
        "however", "therefore", "moreover", "furthermore",
        "in addition", "for example", "in contrast", "as a result",
        "consequently", "on the other hand", "similarly", "specifically",
        "nevertheless", "meanwhile", "subsequently",
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
    score = 40
    words = count_words(text)
    sentences = count_sentences(text)
    paragraphs = count_paragraphs(text)

    if 300 <= words <= 2000:
        score += 25
    elif words > 100:
        score += 15
    elif words > 50:
        score += 5

    if paragraphs >= 3:
        score += 15
    elif paragraphs >= 2:
        score += 8

    if sentences >= 5:
        score += 10
    elif sentences >= 3:
        score += 5

    if any(line.startswith("#") for line in text.split("\n")):
        score += 10

    return max(0, min(100, score))


def compute_content_score(text, domain="general", custom_weights=None):
    """
    Compute the unified content quality score (0–100).
    Supports domain presets and custom weight overrides.
    """
    preset = DOMAIN_PRESETS.get(domain, DOMAIN_PRESETS["general"])
    weights = custom_weights if custom_weights else preset["weights"]
    ideal_read = preset.get("ideal_readability", (50, 80))
    ideal_sent = preset.get("ideal_sentence_length", (12, 22))

    r_score = score_readability(text, ideal_read)
    e_score = score_engagement(text)
    c_score = score_clarity(text, ideal_sent)
    s_score = score_seo_basic(text)

    weighted = (
        r_score * weights["readability"]
        + e_score * weights["engagement"]
        + c_score * weights["clarity"]
        + s_score * weights["seo"]
    )

    return {
        "overall": round(weighted, 1),
        "readability": round(r_score, 1),
        "engagement": round(e_score, 1),
        "clarity": round(c_score, 1),
        "seo": round(s_score, 1),
        "domain": domain,
        "domain_label": preset["label"],
        "weights_used": weights,
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


def get_domain_presets():
    """Return all domain presets for UI."""
    return DOMAIN_PRESETS
