"""
AI Content Intelligence System — Emotional Impact Mapping (V4)
Map content to 8 core emotions at paragraph level using NRC-style lexicon.
"""

import re
from collections import Counter, defaultdict

# ═══════════════════════════════════════════════════════════════════
# NRC-Style Emotion Lexicon (Curated subset)
# ═══════════════════════════════════════════════════════════════════

EMOTION_LEXICON = {
    "trust": [
        "trust", "reliable", "honest", "integrity", "genuine", "authentic",
        "credible", "dependable", "faithful", "loyal", "secure", "safe",
        "proven", "verified", "certified", "guaranteed", "committed",
        "professional", "ethical", "transparent", "consistent", "stable",
        "confident", "assure", "promise", "believe", "support", "protect",
    ],
    "anticipation": [
        "expect", "predict", "forecast", "upcoming", "future", "soon",
        "plan", "prepare", "hope", "exciting", "anticipate", "looking forward",
        "next", "tomorrow", "opportunity", "potential", "promising", "aspire",
        "goal", "vision", "roadmap", "milestone", "launch", "reveal",
        "announce", "preview", "trend", "emerging",
    ],
    "fear": [
        "fear", "danger", "risk", "threat", "warning", "alarm", "panic",
        "anxiety", "worry", "concern", "crisis", "emergency", "urgent",
        "critical", "devastating", "catastrophe", "volatile", "uncertain",
        "vulnerable", "exposed", "beware", "caution", "hazard", "peril",
    ],
    "surprise": [
        "surprise", "unexpected", "shocking", "astonishing", "remarkable",
        "incredible", "unbelievable", "stunning", "revolutionary", "breakthrough",
        "unprecedented", "extraordinary", "dramatic", "sudden", "reveal",
        "discover", "uncover", "twist", "amazingly", "surprisingly",
    ],
    "joy": [
        "happy", "joy", "celebrate", "success", "triumph", "win", "achieve",
        "excellent", "wonderful", "fantastic", "brilliant", "outstanding",
        "delighted", "thrilled", "excited", "love", "enjoy", "perfect",
        "beautiful", "amazing", "great", "awesome", "superb", "magnificent",
        "reward", "benefit", "profit", "growth", "flourish",
    ],
    "sadness": [
        "sad", "loss", "decline", "fail", "unfortunate", "tragic", "suffer",
        "struggle", "difficult", "challenge", "setback", "disappoint",
        "regret", "miss", "lack", "shortage", "deficit", "downturn",
        "recession", "collapse", "bankruptcy", "poverty", "grief",
    ],
    "disgust": [
        "disgust", "horrible", "terrible", "awful", "unacceptable", "corrupt",
        "fraud", "scam", "waste", "toxic", "harmful", "offensive",
        "unethical", "exploit", "abuse", "deceive", "manipulate",
        "misleading", "dishonest", "incompetent", "negligent",
    ],
    "anger": [
        "angry", "outrage", "furious", "frustrate", "demand", "protest",
        "condemn", "criticize", "blame", "attack", "fight", "oppose",
        "reject", "refuse", "deny", "violate", "unfair", "injustice",
        "exploit", "betray", "destroy", "aggressive", "hostile",
    ],
}

EMOTION_COLORS = {
    "trust": "#42A5F5",
    "anticipation": "#AB47BC",
    "fear": "#EF5350",
    "surprise": "#FF7043",
    "joy": "#66BB6A",
    "sadness": "#78909C",
    "disgust": "#8D6E63",
    "anger": "#E53935",
}

EMOTION_EMOJIS = {
    "trust": "🤝",
    "anticipation": "🔮",
    "fear": "😨",
    "surprise": "😲",
    "joy": "😊",
    "sadness": "😢",
    "disgust": "🤢",
    "anger": "😡",
}


def analyze_emotions(text):
    """Analyze emotions in full text."""
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    emotion_counts = {}

    for emotion, keywords in EMOTION_LEXICON.items():
        count = sum(1 for w in words if w in keywords)
        emotion_counts[emotion] = count

    total_matches = sum(emotion_counts.values())
    if total_matches == 0:
        total_matches = 1  # avoid division by zero

    emotion_scores = {}
    for emotion, count in emotion_counts.items():
        emotion_scores[emotion] = {
            "count": count,
            "percentage": round(count / total_matches * 100, 1),
            "intensity": round(count / max(1, len(words)) * 1000, 1),
            "color": EMOTION_COLORS[emotion],
            "emoji": EMOTION_EMOJIS[emotion],
        }

    # Dominant emotion
    dominant = max(emotion_counts, key=emotion_counts.get)

    return {
        "emotions": emotion_scores,
        "dominant": {
            "emotion": dominant,
            "emoji": EMOTION_EMOJIS[dominant],
            "color": EMOTION_COLORS[dominant],
        },
        "total_signals": total_matches,
    }


def paragraph_emotions(text):
    """Analyze emotions at paragraph level."""
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 20]
    if len(paragraphs) < 2:
        paragraphs = [p.strip() for p in text.split("\n") if len(p.strip()) > 20]

    results = []
    for i, para in enumerate(paragraphs[:15]):  # Limit
        analysis = analyze_emotions(para)
        dom = analysis["dominant"]
        results.append({
            "paragraph": i + 1,
            "preview": para[:100] + ("..." if len(para) > 100 else ""),
            "dominant_emotion": dom["emotion"],
            "emoji": dom["emoji"],
            "color": dom["color"],
            "emotions": {k: v["percentage"] for k, v in analysis["emotions"].items()},
        })

    return results


def emotion_alignment(text, goal="trust"):
    """
    Check if emotional profile aligns with content goal.
    Goal can be: trust, excitement (joy+anticipation), urgency (fear+anticipation), etc.
    """
    analysis = analyze_emotions(text)
    emotions = analysis["emotions"]

    goal_map = {
        "trust": ["trust"],
        "excitement": ["joy", "anticipation", "surprise"],
        "urgency": ["fear", "anticipation"],
        "authority": ["trust", "anger"],
        "empathy": ["sadness", "joy", "trust"],
        "motivation": ["joy", "anticipation", "trust"],
    }

    target_emotions = goal_map.get(goal, ["trust"])
    target_score = sum(emotions[e]["percentage"] for e in target_emotions if e in emotions)
    total_score = sum(v["percentage"] for v in emotions.values())

    alignment = round(target_score / max(1, total_score) * 100, 1)

    if alignment > 60:
        verdict = f"Strong alignment with '{goal}' goal"
        color = "#00E676"
    elif alignment > 35:
        verdict = f"Moderate alignment with '{goal}' goal"
        color = "#FFA726"
    else:
        verdict = f"Weak alignment with '{goal}' goal — consider adjusting tone"
        color = "#EF5350"

    return {
        "goal": goal,
        "alignment_score": alignment,
        "verdict": verdict,
        "color": color,
        "target_emotions": target_emotions,
    }


def get_emotion_report(text, goal="trust"):
    """Generate full emotional impact report."""
    return {
        "overall": analyze_emotions(text),
        "paragraphs": paragraph_emotions(text),
        "alignment": emotion_alignment(text, goal),
    }
