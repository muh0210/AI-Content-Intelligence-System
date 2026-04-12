"""
AI Content Intelligence System — Plagiarism Risk Indicator
Internal similarity analysis and cross-document comparison.
"""

import re
from difflib import SequenceMatcher
from config import PLAGIARISM_THRESHOLDS


def split_into_sentences(text):
    """Split text into sentences for comparison."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def sentence_similarity(a, b):
    """Compute similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def internal_similarity_check(text):
    """
    Check for internal plagiarism / repetitive content.
    Compares all sentence pairs within the document.
    """
    sentences = split_into_sentences(text)

    if len(sentences) < 2:
        return {
            "risk_level": "Low",
            "risk_score": 0,
            "color": "#00E676",
            "similar_pairs": [],
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

    # Calculate risk score
    if total_comparisons == 0:
        risk_score = 0
    else:
        risk_score = min(100, (high_similarity_count / total_comparisons) * 100 * 5)

    # Determine risk level
    if risk_score > 60:
        risk_level = "High"
        color = "#B71C1C"
        message = "⚠️ High internal repetition detected. Consider diversifying your content."
    elif risk_score > 30:
        risk_level = "Medium"
        color = "#FFA726"
        message = "⚡ Some repetitive patterns found. Review flagged sentence pairs."
    else:
        risk_level = "Low"
        color = "#00E676"
        message = "✅ Content shows good variety with minimal repetition."

    return {
        "risk_level": risk_level,
        "risk_score": round(risk_score, 1),
        "color": color,
        "similar_pairs": sorted(similar_pairs, key=lambda x: x["similarity"], reverse=True)[:10],
        "total_sentences": len(sentences),
        "total_comparisons": total_comparisons,
        "message": message,
    }


def cross_document_similarity(text_a, text_b):
    """
    Compare two documents for similarity using TF-IDF cosine similarity.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

        if similarity > PLAGIARISM_THRESHOLDS["high"]:
            level = "Very High"
            color = "#B71C1C"
        elif similarity > PLAGIARISM_THRESHOLDS["medium"]:
            level = "High"
            color = "#EF5350"
        elif similarity > PLAGIARISM_THRESHOLDS["low"]:
            level = "Moderate"
            color = "#FFA726"
        else:
            level = "Low"
            color = "#00E676"

        return {
            "similarity_score": round(similarity * 100, 1),
            "level": level,
            "color": color,
        }

    except ImportError:
        # Fallback to SequenceMatcher
        sim = SequenceMatcher(None, text_a.lower(), text_b.lower()).ratio()
        return {
            "similarity_score": round(sim * 100, 1),
            "level": "Moderate" if sim > 0.5 else "Low",
            "color": "#FFA726" if sim > 0.5 else "#00E676",
        }


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
