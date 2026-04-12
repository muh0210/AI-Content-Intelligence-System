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
    Generate comprehensive plagiarism risk report.
    """
    report = {
        "internal": internal_similarity_check(text),
    }

    if reference_text and reference_text.strip():
        report["cross_document"] = cross_document_similarity(text, reference_text)

    return report
