"""
AI Content Intelligence System — Plagiarism Risk Indicator (V2 — Upgraded)
Internal similarity, n-gram fingerprinting, cross-document TF-IDF, common phrase filtering.
"""

import re
from difflib import SequenceMatcher
from collections import Counter
from config import PLAGIARISM_THRESHOLDS


def split_into_sentences(text):
    """Split text into sentences for comparison."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def sentence_similarity(a, b):
    """Compute similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# ═══════════════════════════════════════════════════════════════════
# N-Gram Fingerprinting (NEW)
# ═══════════════════════════════════════════════════════════════════

COMMON_PHRASES = {
    "on the other hand", "in addition to", "as a result of",
    "in order to", "due to the fact", "it is important",
    "the fact that", "in terms of", "as well as",
    "at the same time", "on the basis of", "in the case of",
    "with respect to", "in the context of", "for the purpose of",
    "it should be noted", "it is worth noting", "it can be seen",
    "this is because", "for example", "such as",
}


def extract_ngrams(text, n=4):
    """Extract character-level n-grams for fingerprinting."""
    words = text.lower().split()
    if len(words) < n:
        return []
    return [" ".join(words[i:i + n]) for i in range(len(words) - n + 1)]


def is_common_phrase(ngram):
    """Check if an n-gram is a common English phrase (not plagiarism)."""
    for cp in COMMON_PHRASES:
        if cp in ngram or ngram in cp:
            return True
    return False


def ngram_fingerprint(text, n=4):
    """
    Generate n-gram fingerprint of the text.
    Returns set of unique n-grams (excluding common phrases).
    """
    ngrams = extract_ngrams(text, n)
    return {ng for ng in ngrams if not is_common_phrase(ng)}


def fingerprint_similarity(text_a, text_b, n=4):
    """
    Compare two texts using n-gram fingerprinting.
    Returns Jaccard similarity coefficient.
    """
    fp_a = ngram_fingerprint(text_a, n)
    fp_b = ngram_fingerprint(text_b, n)

    if not fp_a or not fp_b:
        return 0.0

    intersection = fp_a & fp_b
    union = fp_a | fp_b

    jaccard = len(intersection) / len(union)
    return jaccard


# ═══════════════════════════════════════════════════════════════════
# Internal Similarity Check (Enhanced)
# ═══════════════════════════════════════════════════════════════════

def internal_similarity_check(text):
    """
    Enhanced internal plagiarism / repetitive content detection.
    Uses both sentence comparison and n-gram fingerprinting.
    """
    sentences = split_into_sentences(text)

    if len(sentences) < 2:
        return {
            "risk_level": "Low",
            "risk_score": 0,
            "color": "#00E676",
            "similar_pairs": [],
            "repeated_ngrams": [],
            "message": "Not enough sentences to compare.",
        }

    similar_pairs = []
    total_comparisons = 0
    high_similarity_count = 0

    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            total_comparisons += 1
            sim = sentence_similarity(sentences[i], sentences[j])

            if sim > PLAGIARISM_THRESHOLDS["low"]:
                similar_pairs.append({
                    "sentence_a": sentences[i][:120],
                    "sentence_b": sentences[j][:120],
                    "similarity": round(sim * 100, 1),
                    "index_a": i + 1,
                    "index_b": j + 1,
                })

            if sim > PLAGIARISM_THRESHOLDS["medium"]:
                high_similarity_count += 1

    # N-gram repetition detection
    ngrams = extract_ngrams(text, 5)
    ngram_freq = Counter(ngrams)
    repeated = [
        {"ngram": ng, "count": c}
        for ng, c in ngram_freq.most_common(10)
        if c >= 2 and not is_common_phrase(ng)
    ]

    # Calculate risk score
    if total_comparisons == 0:
        risk_score = 0
    else:
        sentence_risk = (high_similarity_count / total_comparisons) * 100 * 5
        ngram_risk = min(30, len(repeated) * 5)
        risk_score = min(100, sentence_risk + ngram_risk)

    if risk_score > 60:
        risk_level, color = "High", "#B71C1C"
        message = "⚠️ High internal repetition detected. Diversify your content."
    elif risk_score > 30:
        risk_level, color = "Medium", "#FFA726"
        message = "⚡ Some repetitive patterns found. Review flagged items."
    else:
        risk_level, color = "Low", "#00E676"
        message = "✅ Content shows good variety with minimal repetition."

    return {
        "risk_level": risk_level,
        "risk_score": round(risk_score, 1),
        "color": color,
        "similar_pairs": sorted(similar_pairs, key=lambda x: x["similarity"], reverse=True)[:10],
        "repeated_ngrams": repeated[:8],
        "total_sentences": len(sentences),
        "total_comparisons": total_comparisons,
        "message": message,
    }


# ═══════════════════════════════════════════════════════════════════
# Cross-Document Comparison (Enhanced)
# ═══════════════════════════════════════════════════════════════════

def cross_document_similarity(text_a, text_b):
    """
    Compare two documents using multiple methods:
    1. TF-IDF cosine similarity
    2. N-gram fingerprint similarity
    Returns combined assessment.
    """
    results = {}

    # Method 1: TF-IDF Cosine Similarity
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
        cos_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        results["tfidf_similarity"] = round(cos_sim * 100, 1)
    except Exception:
        cos_sim = SequenceMatcher(None, text_a.lower(), text_b.lower()).ratio()
        results["tfidf_similarity"] = round(cos_sim * 100, 1)

    # Method 2: N-gram Fingerprint
    jaccard = fingerprint_similarity(text_a, text_b)
    results["fingerprint_similarity"] = round(jaccard * 100, 1)

    # Combined score (weighted average)
    combined = (results["tfidf_similarity"] * 0.6) + (results["fingerprint_similarity"] * 0.4)
    results["combined_similarity"] = round(combined, 1)

    # Risk level
    if combined > 80:
        results["level"] = "Very High"
        results["color"] = "#B71C1C"
    elif combined > 60:
        results["level"] = "High"
        results["color"] = "#EF5350"
    elif combined > 35:
        results["level"] = "Moderate"
        results["color"] = "#FFA726"
    else:
        results["level"] = "Low"
        results["color"] = "#00E676"

    return results


def get_plagiarism_report(text, reference_text=None):
    """
    Generate comprehensive plagiarism risk report with AI detection.
    """
    report = {
        "internal": internal_similarity_check(text),
        "ai_detection": detect_ai_content(text),
    }

    if reference_text and reference_text.strip():
        report["cross_document"] = cross_document_similarity(text, reference_text)

    # Combined Authenticity Score
    plag_risk = report["internal"]["risk_score"]
    ai_score = report["ai_detection"]["ai_probability"]
    authenticity = max(0, 100 - (plag_risk * 0.5 + ai_score * 0.5))
    report["authenticity"] = {
        "score": round(authenticity, 1),
        "label": "Authentic" if authenticity >= 70 else "Suspicious" if authenticity >= 40 else "Likely AI/Copied",
        "color": "#00E676" if authenticity >= 70 else "#FFA726" if authenticity >= 40 else "#EF5350",
    }

    return report


# ═══════════════════════════════════════════════════════════════════
# AI Content Detection (NEW — V4)
# ═══════════════════════════════════════════════════════════════════

def detect_ai_content(text):
    """
    Detect AI-generated content using heuristic analysis.
    Checks: vocabulary entropy, sentence uniformity, word complexity,
    repetitive patterns, and formulaic structures.
    """
    import math
    sentences = split_into_sentences(text)
    words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())

    if len(words) < 30 or len(sentences) < 3:
        return {
            "ai_probability": 0,
            "label": "Insufficient text",
            "signals": [],
            "color": "#666",
        }

    signals = []
    score = 0

    # 1. Vocabulary Entropy (AI tends to be more uniform)
    freq = Counter(words)
    total = len(words)
    entropy = -sum((c / total) * math.log2(c / total) for c in freq.values() if c > 0)
    max_entropy = math.log2(len(freq)) if len(freq) > 1 else 1
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

    if normalized_entropy > 0.92:
        score += 15
        signals.append("Very uniform vocabulary distribution (AI signal)")
    elif normalized_entropy > 0.85:
        score += 8

    # 2. Sentence Length Uniformity (AI = very consistent lengths)
    if len(sentences) >= 5:
        lengths = [len(s.split()) for s in sentences]
        import numpy as np
        cv = np.std(lengths) / max(1, np.mean(lengths))  # Coefficient of variation

        if cv < 0.20:
            score += 20
            signals.append("Very uniform sentence lengths (strong AI signal)")
        elif cv < 0.30:
            score += 10
            signals.append("Low sentence length variation")

    # 3. Formulaic transitions (AI loves these)
    formulaic = [
        "in conclusion", "furthermore", "moreover", "additionally",
        "it is important to note", "it is worth mentioning",
        "in today's world", "in this article", "let's dive",
        "without further ado", "that being said", "having said that",
        "it goes without saying", "needless to say",
    ]
    text_lower = text.lower()
    formulaic_count = sum(1 for f in formulaic if f in text_lower)
    if formulaic_count >= 4:
        score += 15
        signals.append(f"High formulaic phrase density ({formulaic_count} found)")
    elif formulaic_count >= 2:
        score += 8
        signals.append(f"Some formulaic phrases ({formulaic_count} found)")

    # 4. Average word complexity (AI avoids very simple or very complex)
    avg_word_len = sum(len(w) for w in words) / total
    if 4.5 <= avg_word_len <= 5.5:
        score += 10
        signals.append("Very average word complexity (AI tends to be mid-range)")

    # 5. Paragraph start patterns (AI often starts paragraphs similarly)
    paragraphs = [p.strip() for p in text.split("\n") if len(p.strip()) > 20]
    if len(paragraphs) >= 4:
        starts = [p.split()[0].lower() if p.split() else "" for p in paragraphs]
        start_freq = Counter(starts)
        top_start = start_freq.most_common(1)[0] if start_freq else ("", 0)
        if top_start[1] >= 3:
            score += 10
            signals.append(f"Repetitive paragraph openings ('{top_start[0]}' used {top_start[1]}x)")

    # 6. Lack of personal voice markers
    personal_markers = [
        "i think", "i believe", "in my experience", "personally",
        "i've seen", "i noticed", "honestly", "frankly",
        "my take", "i'd argue", "i feel",
    ]
    personal_count = sum(1 for m in personal_markers if m in text_lower)
    if personal_count == 0 and len(words) > 200:
        score += 10
        signals.append("No personal voice markers detected")

    # Cap at 100
    ai_probability = min(100, score)

    if ai_probability >= 60:
        label = "Likely AI-Generated"
        color = "#EF5350"
    elif ai_probability >= 35:
        label = "Mixed / Possibly AI-Assisted"
        color = "#FFA726"
    elif ai_probability >= 15:
        label = "Mostly Human"
        color = "#66BB6A"
    else:
        label = "Likely Human-Written"
        color = "#00E676"

    return {
        "ai_probability": ai_probability,
        "label": label,
        "color": color,
        "signals": signals,
        "details": {
            "entropy": round(normalized_entropy, 3),
            "avg_word_length": round(avg_word_len, 2),
            "formulaic_count": formulaic_count,
            "personal_markers": personal_count,
        },
    }

