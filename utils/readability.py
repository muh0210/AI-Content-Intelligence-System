"""
AI Content Intelligence System — Readability Engine
Computes multiple readability metrics with human-readable interpretation.
"""

import textstat


def flesch_reading_ease(text):
    """Compute Flesch Reading Ease score (0–100)."""
    score = textstat.flesch_reading_ease(text)
    return max(0, min(100, score))


def flesch_kincaid_grade(text):
    """Compute Flesch-Kincaid Grade Level."""
    return textstat.flesch_kincaid_grade(text)


def gunning_fog(text):
    """Compute Gunning Fog Index."""
    return textstat.gunning_fog(text)


def smog_index(text):
    """Compute SMOG Index."""
    return textstat.smog_index(text)


def coleman_liau(text):
    """Compute Coleman-Liau Index."""
    return textstat.coleman_liau_index(text)


def automated_readability(text):
    """Compute Automated Readability Index."""
    return textstat.automated_readability_index(text)


def interpret_flesch(score):
    """Interpret Flesch Reading Ease score into human-readable label."""
    if score >= 90:
        return {"label": "Very Easy", "description": "Easily understood by an average 11-year-old", "color": "#00E676", "icon": "🟢", "audience": "General public, elementary"}
    elif score >= 70:
        return {"label": "Easy", "description": "Conversational English, easily understood", "color": "#66BB6A", "icon": "🟢", "audience": "General public"}
    elif score >= 50:
        return {"label": "Moderate", "description": "Fairly difficult, best for high school+", "color": "#FFA726", "icon": "🟡", "audience": "High school students"}
    elif score >= 30:
        return {"label": "Difficult", "description": "Best understood by college graduates", "color": "#EF5350", "icon": "🔴", "audience": "College graduates"}
    else:
        return {"label": "Very Difficult", "description": "Professional / academic level text", "color": "#B71C1C", "icon": "🔴", "audience": "Professionals, academics"}


def get_readability_report(text):
    """
    Generate a comprehensive readability report.
    Returns dict with all scores and interpretation.
    """
    fre = flesch_reading_ease(text)
    interpretation = interpret_flesch(fre)

    return {
        "flesch_reading_ease": round(fre, 1),
        "flesch_kincaid_grade": round(flesch_kincaid_grade(text), 1),
        "gunning_fog": round(gunning_fog(text), 1),
        "smog_index": round(smog_index(text), 1),
        "coleman_liau": round(coleman_liau(text), 1),
        "automated_readability": round(automated_readability(text), 1),
        "interpretation": interpretation,
        "consensus_grade": textstat.text_standard(text, float_output=False),
    }
