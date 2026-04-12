"""
AI Content Intelligence System — Tone Detection Module
Sentiment analysis & formality detection using TextBlob.
"""

from textblob import TextBlob
from utils.cleaner import split_sentences, average_word_length


def analyze_sentiment(text):
    """
    Analyze sentiment polarity and subjectivity.
    Returns polarity (-1 to 1) and subjectivity (0 to 1).
    """
    blob = TextBlob(text)
    return {
        "polarity": round(blob.sentiment.polarity, 3),
        "subjectivity": round(blob.sentiment.subjectivity, 3),
    }


def classify_tone(polarity):
    """Classify tone based on polarity value."""
    if polarity > 0.3:
        return {"tone": "Very Positive", "emoji": "😊", "color": "#00E676"}
    elif polarity > 0.1:
        return {"tone": "Positive", "emoji": "🙂", "color": "#66BB6A"}
    elif polarity > -0.1:
        return {"tone": "Neutral", "emoji": "😐", "color": "#FFA726"}
    elif polarity > -0.3:
        return {"tone": "Negative", "emoji": "😟", "color": "#EF5350"}
    else:
        return {"tone": "Very Negative", "emoji": "😠", "color": "#B71C1C"}


def classify_subjectivity(subjectivity):
    """Classify subjectivity level."""
    if subjectivity > 0.6:
        return {"level": "Highly Subjective", "description": "Opinion-heavy, personal perspective", "color": "#FF7043"}
    elif subjectivity > 0.4:
        return {"level": "Moderately Subjective", "description": "Mix of facts and opinions", "color": "#FFA726"}
    elif subjectivity > 0.2:
        return {"level": "Fairly Objective", "description": "Mostly factual with some opinion", "color": "#66BB6A"}
    else:
        return {"level": "Very Objective", "description": "Fact-based, minimal personal opinion", "color": "#00E676"}


def detect_formality(text):
    """
    Estimate formality level using word-length heuristics
    and vocabulary complexity analysis.
    """
    avg_len = average_word_length(text)
    sentences = split_sentences(text)

    # Formal indicators
    formal_markers = [
        "however", "therefore", "furthermore", "consequently",
        "nevertheless", "moreover", "whereas", "hereby",
        "accordingly", "thus", "hence", "notwithstanding",
    ]
    informal_markers = [
        "gonna", "wanna", "kinda", "gotta", "yeah", "nah",
        "cool", "awesome", "stuff", "things", "lol", "btw",
        "hey", "ok", "okay", "yep", "nope", "wow",
    ]

    text_lower = text.lower()
    formal_count = sum(1 for m in formal_markers if m in text_lower)
    informal_count = sum(1 for m in informal_markers if m in text_lower)

    # Scoring formality
    formality_score = 50  # base
    formality_score += formal_count * 8
    formality_score -= informal_count * 10
    formality_score += (avg_len - 4.5) * 10  # longer words = more formal

    formality_score = max(0, min(100, formality_score))

    if formality_score >= 75:
        level = {"level": "Highly Formal", "color": "#7C4DFF"}
    elif formality_score >= 50:
        level = {"level": "Formal", "color": "#42A5F5"}
    elif formality_score >= 30:
        level = {"level": "Semi-Formal", "color": "#FFA726"}
    else:
        level = {"level": "Informal", "color": "#FF7043"}

    return {
        "score": round(formality_score, 1),
        **level,
    }


def get_tone_report(text):
    """
    Generate a comprehensive tone & sentiment report.
    """
    sentiment = analyze_sentiment(text)
    tone = classify_tone(sentiment["polarity"])
    subjectivity = classify_subjectivity(sentiment["subjectivity"])
    formality = detect_formality(text)

    # Sentence-level sentiment breakdown
    sentences = split_sentences(text)
    sentence_sentiments = []
    for sent in sentences[:20]:  # limit to avoid long processing
        s = analyze_sentiment(sent)
        t = classify_tone(s["polarity"])
        sentence_sentiments.append({
            "sentence": sent[:100] + ("..." if len(sent) > 100 else ""),
            "polarity": s["polarity"],
            "tone": t["tone"],
            "emoji": t["emoji"],
        })

    return {
        "overall_polarity": sentiment["polarity"],
        "overall_subjectivity": sentiment["subjectivity"],
        "tone": tone,
        "subjectivity": subjectivity,
        "formality": formality,
        "sentence_breakdown": sentence_sentiments,
    }
