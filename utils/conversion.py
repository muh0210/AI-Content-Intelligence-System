"""
AI Content Intelligence System — Conversion Probability Score (V4)
Score marketing/business content on persuasion principles: 0–100.
"""

import re
from collections import Counter


# ═══════════════════════════════════════════════════════════════════
# Persuasion Signal Detectors
# ═══════════════════════════════════════════════════════════════════

def detect_scarcity(text):
    """Detect scarcity/urgency signals."""
    keywords = [
        "limited", "exclusive", "only", "last chance", "hurry",
        "deadline", "expires", "running out", "few remaining",
        "act now", "don't miss", "rare", "once in a lifetime",
        "while supplies last", "limited time", "today only",
    ]
    text_lower = text.lower()
    found = [kw for kw in keywords if kw in text_lower]
    score = min(100, len(found) * 20)
    return {"score": score, "signals": found, "label": "Scarcity & Urgency"}


def detect_social_proof(text):
    """Detect social proof signals."""
    keywords = [
        "customers", "users", "people", "trusted by", "rated",
        "reviewed", "testimonial", "case study", "million",
        "thousand", "percent", "survey", "research shows",
        "according to", "experts", "recommended", "popular",
        "best-selling", "award", "recognized", "featured in",
    ]
    # Also detect numbers (statistics)
    numbers = re.findall(r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?%?\b", text)

    text_lower = text.lower()
    found = [kw for kw in keywords if kw in text_lower]
    score = min(100, (len(found) * 12) + (len(numbers) * 5))
    return {"score": score, "signals": found[:8], "stats_found": len(numbers),
            "label": "Social Proof"}


def detect_authority(text):
    """Detect authority signals."""
    keywords = [
        "expert", "leading", "authority", "certified", "accredited",
        "years of experience", "industry", "professional", "specialist",
        "phd", "doctor", "professor", "published", "peer-reviewed",
        "harvard", "stanford", "mit", "research", "study",
        "founded", "ceo", "director", "partner",
    ]
    text_lower = text.lower()
    found = [kw for kw in keywords if kw in text_lower]
    score = min(100, len(found) * 15)
    return {"score": score, "signals": found, "label": "Authority"}


def detect_cta_strength(text):
    """Detect call-to-action strength."""
    cta_patterns = [
        "sign up", "subscribe", "buy now", "get started", "learn more",
        "download", "try free", "book a demo", "contact us", "join",
        "register", "claim", "grab", "start", "discover",
        "click here", "apply now", "order", "reserve", "schedule",
    ]
    imperative_verbs = [
        "discover", "unlock", "transform", "boost", "maximize",
        "accelerate", "achieve", "master", "dominate", "crush",
    ]

    text_lower = text.lower()
    ctas = [p for p in cta_patterns if p in text_lower]
    imperatives = [v for v in imperative_verbs if v in text_lower]

    score = min(100, (len(ctas) * 20) + (len(imperatives) * 10))
    return {"score": score, "ctas": ctas, "imperatives": imperatives,
            "label": "CTA Strength"}


def detect_benefit_clarity(text):
    """Detect benefit-focused language."""
    benefit_words = [
        "save", "increase", "improve", "boost", "reduce", "eliminate",
        "faster", "easier", "better", "more efficient", "streamline",
        "automate", "simplify", "enhance", "optimize", "maximize",
        "profit", "revenue", "growth", "results", "outcome",
        "benefit", "advantage", "value", "solution", "free",
    ]
    text_lower = text.lower()
    found = [w for w in benefit_words if w in text_lower]
    score = min(100, len(found) * 10)
    return {"score": score, "signals": found, "label": "Benefit Clarity"}


def detect_emotional_triggers(text):
    """Detect emotional trigger words for conversion."""
    triggers = [
        "imagine", "picture", "feel", "dream", "deserve",
        "finally", "never again", "breakthrough", "secret",
        "exclusive", "proven", "guaranteed", "risk-free",
        "life-changing", "game-changer", "revolutionary",
    ]
    text_lower = text.lower()
    found = [t for t in triggers if t in text_lower]
    score = min(100, len(found) * 15)
    return {"score": score, "signals": found, "label": "Emotional Triggers"}


def get_conversion_score(text):
    """
    Compute overall conversion probability score (0-100)
    based on persuasion principles.
    """
    scarcity = detect_scarcity(text)
    social = detect_social_proof(text)
    authority = detect_authority(text)
    cta = detect_cta_strength(text)
    benefit = detect_benefit_clarity(text)
    emotional = detect_emotional_triggers(text)

    components = [scarcity, social, authority, cta, benefit, emotional]

    # Weighted score
    weights = {
        "Scarcity & Urgency": 0.12,
        "Social Proof": 0.20,
        "Authority": 0.15,
        "CTA Strength": 0.20,
        "Benefit Clarity": 0.20,
        "Emotional Triggers": 0.13,
    }

    overall = sum(c["score"] * weights.get(c["label"], 0.15) for c in components)
    overall = max(0, min(100, overall))

    # Verdict
    if overall >= 70:
        verdict = "High conversion potential — strong persuasion signals"
        color = "#00E676"
    elif overall >= 45:
        verdict = "Moderate potential — strengthen weak areas"
        color = "#FFA726"
    elif overall >= 25:
        verdict = "Low potential — missing key persuasion elements"
        color = "#EF5350"
    else:
        verdict = "Very low — content needs significant persuasion upgrade"
        color = "#B71C1C"

    return {
        "overall_score": round(overall, 1),
        "verdict": verdict,
        "color": color,
        "components": {
            "scarcity": scarcity,
            "social_proof": social,
            "authority": authority,
            "cta_strength": cta,
            "benefit_clarity": benefit,
            "emotional_triggers": emotional,
        },
    }
