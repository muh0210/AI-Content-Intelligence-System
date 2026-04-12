"""
AI Content Intelligence System — SEO Analysis Module (V2 — Upgraded)
TF-IDF importance ranking, keyword density, topic clustering, and headline optimization.
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


def extract_trigrams(text, top_n=8):
    """Extract top N three-word phrases (trigrams)."""
    words = tokenize(text)
    filtered = [w for w in words if w not in SEO_STOP_WORDS]

    if len(filtered) < 3:
        return []

    trigrams = [
        f"{filtered[i]} {filtered[i+1]} {filtered[i+2]}"
        for i in range(len(filtered) - 2)
    ]
    freq = Counter(trigrams)

    return [
        {"phrase": phrase, "count": count}
        for phrase, count in freq.most_common(top_n)
        if count >= 2
    ]


# ═══════════════════════════════════════════════════════════════════
# TF-IDF Importance Ranking (NEW)
# ═══════════════════════════════════════════════════════════════════

def tfidf_keywords(text, top_n=15):
    """
    Extract keywords ranked by TF-IDF importance.
    Uses sklearn's TfidfVectorizer for proper weighting.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np

        # Split text into sentences as "documents" for TF-IDF
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        if len(sentences) < 2:
            sentences = [text[:len(text)//2], text[len(text)//2:]]

        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=100,
            ngram_range=(1, 2),
            min_df=1,
        )
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()

        # Average TF-IDF scores across all sentences
        avg_scores = tfidf_matrix.mean(axis=0).A1
        top_indices = avg_scores.argsort()[-top_n:][::-1]

        results = []
        for idx in top_indices:
            if avg_scores[idx] > 0.01:
                results.append({
                    "keyword": feature_names[idx],
                    "tfidf_score": round(float(avg_scores[idx]), 4),
                    "importance": "high" if avg_scores[idx] > 0.1 else "medium" if avg_scores[idx] > 0.05 else "low",
                })

        return results

    except ImportError:
        return []
    except Exception:
        return []


def topic_clusters(text, n_clusters=3):
    """
    Group keywords into topic clusters using simple frequency analysis.
    """
    words = tokenize(text)
    filtered = [w for w in words if w not in SEO_STOP_WORDS and len(w) > 3]
    freq = Counter(filtered)

    if len(freq) < n_clusters:
        return [{"topic": i + 1, "keywords": list(freq.keys())} for i in range(1)]

    # Simple clustering: group by frequency tiers
    sorted_words = freq.most_common()
    cluster_size = max(1, len(sorted_words) // n_clusters)

    clusters = []
    for i in range(n_clusters):
        start = i * cluster_size
        end = start + cluster_size
        cluster_words = [w for w, c in sorted_words[start:end]]
        if cluster_words:
            clusters.append({
                "topic": i + 1,
                "keywords": cluster_words[:8],
                "label": f"Topic {i + 1}: {', '.join(cluster_words[:3])}",
            })

    return clusters


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

    # Length check
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
        suggestions.append("Keep headline under 65 characters for search result display.")

    # Power words
    power_words = [
        "ultimate", "essential", "proven", "powerful", "complete",
        "comprehensive", "expert", "advanced", "best", "top",
        "guide", "secrets", "tips", "strategies", "how",
        "definitive", "critical", "revolutionary", "breakthrough",
    ]
    has_power = any(pw in headline.lower() for pw in power_words)
    if has_power:
        score += 10
    else:
        suggestions.append("Add a power word (e.g., 'Ultimate', 'Proven', 'Essential').")

    # Number presence
    if any(char.isdigit() for char in headline):
        score += 10
    else:
        suggestions.append("Headlines with numbers get more clicks (e.g., '7 Ways to...').")

    # Emotional words
    emotion_words = ["amazing", "incredible", "shocking", "surprising", "critical", "vital"]
    if any(ew in headline.lower() for ew in emotion_words):
        score += 5

    # Question format
    if headline.strip().endswith("?"):
        score += 5

    if not suggestions:
        suggestions.append("Great headline! It follows SEO best practices.")

    return {
        "score": min(100, score),
        "word_count": word_count,
        "char_count": char_count,
        "suggestions": suggestions,
    }


def content_seo_suggestions(text, keywords):
    """Generate actionable SEO improvement suggestions."""
    suggestions = []
    word_count = len(tokenize(text))

    # Content length
    if word_count < 300:
        suggestions.append({
            "icon": "📏",
            "text": f"Content is only {word_count} words. Aim for 1000+ for better SEO.",
            "priority": "high",
        })
    elif word_count < 1000:
        suggestions.append({
            "icon": "📏",
            "text": f"Content is {word_count} words. 1500–2500 is optimal for SEO ranking.",
            "priority": "medium",
        })
    else:
        suggestions.append({
            "icon": "✅",
            "text": f"Good content length ({word_count} words).",
            "priority": "low",
        })

    # Keyword density check
    if keywords:
        top = keywords[0]
        if top["density"] > 4:
            suggestions.append({
                "icon": "⚠️",
                "text": f"Keyword '{top['keyword']}' density is {top['density']}% — too high (keyword stuffing risk).",
                "priority": "high",
            })
        elif top["density"] < 0.5:
            suggestions.append({
                "icon": "🔑",
                "text": "No dominant keyword detected. Focus on a primary topic keyword.",
                "priority": "high",
            })

    # Heading structure
    if "#" not in text and word_count > 300:
        suggestions.append({
            "icon": "📑",
            "text": "No headings detected. Add H2/H3 headings to improve structure.",
            "priority": "medium",
        })

    # Paragraph variety
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    if len(paragraphs) < 3 and word_count > 200:
        suggestions.append({
            "icon": "📝",
            "text": "Break content into more paragraphs for better readability.",
            "priority": "medium",
        })

    return suggestions


def detect_search_intent(text):
    """
    Detect the search intent of the content.
    Categories: Informational, Transactional, Navigational, Commercial.
    """
    text_lower = text.lower()

    intent_signals = {
        "informational": {
            "keywords": [
                "what is", "how to", "why", "guide", "tutorial",
                "explain", "definition", "overview", "introduction",
                "learn", "understand", "meaning", "example", "tips",
                "history", "research", "study", "analysis", "review",
            ],
            "score": 0,
            "emoji": "📚",
            "description": "Content that educates or informs",
        },
        "transactional": {
            "keywords": [
                "buy", "price", "discount", "deal", "order",
                "purchase", "subscribe", "sign up", "download",
                "free trial", "coupon", "sale", "offer", "checkout",
                "shipping", "cart", "payment",
            ],
            "score": 0,
            "emoji": "🛒",
            "description": "Content aimed at driving purchases or actions",
        },
        "navigational": {
            "keywords": [
                "login", "sign in", "official", "website",
                "homepage", "contact", "about us", "support",
                "documentation", "dashboard", "account", "portal",
            ],
            "score": 0,
            "emoji": "🧭",
            "description": "Content directing users to specific pages",
        },
        "commercial": {
            "keywords": [
                "best", "top", "review", "comparison", "versus",
                "alternative", "recommended", "rating", "pros and cons",
                "benchmark", "features", "specifications", "vs",
            ],
            "score": 0,
            "emoji": "💼",
            "description": "Content comparing or evaluating products/services",
        },
    }

    for intent, data in intent_signals.items():
        for kw in data["keywords"]:
            if kw in text_lower:
                data["score"] += 1

    # Determine primary intent
    sorted_intents = sorted(intent_signals.items(), key=lambda x: x[1]["score"], reverse=True)
    primary = sorted_intents[0]
    secondary = sorted_intents[1] if sorted_intents[1][1]["score"] > 0 else None

    return {
        "primary": {
            "intent": primary[0].title(),
            "confidence": min(100, primary[1]["score"] * 15),
            "emoji": primary[1]["emoji"],
            "description": primary[1]["description"],
        },
        "secondary": {
            "intent": secondary[0].title(),
            "confidence": min(100, secondary[1]["score"] * 15),
            "emoji": secondary[1]["emoji"],
        } if secondary else None,
        "all_scores": {k: v["score"] for k, v in intent_signals.items()},
    }


def get_seo_report(text, title=""):
    """
    Generate comprehensive SEO analysis report with TF-IDF and search intent.
    """
    keywords = keyword_density(text)
    bigrams = extract_bigrams(text)
    trigrams = extract_trigrams(text)
    tfidf = tfidf_keywords(text)
    clusters = topic_clusters(text)
    seo_suggestions = content_seo_suggestions(text, keywords)
    search_intent = detect_search_intent(text)

    all_words = tokenize(text)
    unique = set(all_words)

    report = {
        "keywords": keywords,
        "bigrams": bigrams,
        "trigrams": trigrams,
        "tfidf_keywords": tfidf,
        "topic_clusters": clusters,
        "seo_suggestions": seo_suggestions,
        "search_intent": search_intent,
        "total_words": len(all_words),
        "unique_words": len(unique),
        "vocabulary_richness": round(len(unique) / max(1, len(all_words)) * 100, 1),
    }

    if title:
        report["headline_analysis"] = analyze_headline(title)

    return report
