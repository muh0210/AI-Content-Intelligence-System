"""
AI Content Intelligence System — Configuration
Centralized settings for scoring weights, thresholds, and presets.
"""

import os

# ─── API Configuration ──────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4"

# ─── Scoring Weights (must sum to 1.0) ──────────────────────────
SCORING_WEIGHTS = {
    "readability": 0.30,
    "engagement": 0.25,
    "clarity": 0.25,
    "seo": 0.20,
}

# ─── Readability Thresholds ─────────────────────────────────────
READABILITY_LABELS = {
    (90, 100): {"label": "Very Easy", "color": "#00E676", "icon": "🟢"},
    (70, 89):  {"label": "Easy", "color": "#66BB6A", "icon": "🟢"},
    (50, 69):  {"label": "Moderate", "color": "#FFA726", "icon": "🟡"},
    (30, 49):  {"label": "Difficult", "color": "#EF5350", "icon": "🔴"},
    (0, 29):   {"label": "Very Difficult", "color": "#B71C1C", "icon": "🔴"},
}

# ─── Tone Labels ────────────────────────────────────────────────
TONE_CONFIG = {
    "positive_threshold": 0.1,
    "negative_threshold": -0.1,
    "formal_word_length": 5.5,
}

# ─── Audience Presets ───────────────────────────────────────────
AUDIENCE_PRESETS = {
    "academic": {
        "label": "🎓 Academic",
        "description": "Formal, structured, citation-ready prose",
        "prompt_modifier": (
            "Rewrite in a formal academic tone. Use precise vocabulary, "
            "passive voice where appropriate, and structured argumentation. "
            "Ensure clarity and logical flow."
        ),
    },
    "business": {
        "label": "💼 Business",
        "description": "Professional, concise, action-oriented",
        "prompt_modifier": (
            "Rewrite in a professional business tone. Be concise, "
            "use active voice, focus on key takeaways, and maintain "
            "an action-oriented structure."
        ),
    },
    "casual": {
        "label": "💬 Casual",
        "description": "Friendly, conversational, engaging",
        "prompt_modifier": (
            "Rewrite in a friendly, conversational tone. Use simple words, "
            "short sentences, and an engaging style that feels natural "
            "and approachable."
        ),
    },
}

# ─── SEO Configuration ─────────────────────────────────────────
SEO_STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above",
    "below", "between", "out", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "when", "where", "why",
    "how", "all", "each", "every", "both", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "just", "because", "but", "and", "or",
    "if", "while", "about", "up", "it", "its", "i", "you", "he", "she",
    "we", "they", "me", "him", "her", "us", "them", "my", "your", "his",
    "our", "their", "this", "that", "these", "those", "what", "which",
    "who", "whom", "am",
}

# ─── Plagiarism Thresholds ──────────────────────────────────────
PLAGIARISM_THRESHOLDS = {
    "low": 0.3,
    "medium": 0.6,
    "high": 0.85,
}

# ─── Content Length Thresholds ──────────────────────────────────
MIN_CONTENT_LENGTH = 50       # minimum chars for analysis
IDEAL_WORD_COUNT_MIN = 300    # ideal word count lower bound
IDEAL_WORD_COUNT_MAX = 2500   # ideal word count upper bound

# ─── App Metadata ───────────────────────────────────────────────
APP_TITLE = "AI Content Intelligence System"
APP_ICON = "🧠"
APP_VERSION = "4.1.0"
