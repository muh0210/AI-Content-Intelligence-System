"""
AI Content Intelligence System — Smart Insights Engine
Generates categorized, priority-ranked recommendations.
"""


def generate_insights(scores, readability_report, tone_report, seo_report, text_stats):
    """
    Generate smart insights based on all analysis results.
    Returns categorized suggestions: Strengths, Weaknesses, Tips.
    """
    strengths = []
    weaknesses = []
    tips = []

    overall_score = scores.get("overall", 0)
    readability_score = scores.get("readability", 0)
    engagement_score = scores.get("engagement", 0)
    clarity_score = scores.get("clarity", 0)
    seo_score = scores.get("seo", 0)

    # ─── Overall Score Insights ──────────────────────────────
    if overall_score >= 80:
        strengths.append({
            "icon": "🏆",
            "text": "Excellent overall content quality!",
            "priority": 1,
        })
    elif overall_score >= 60:
        tips.append({
            "icon": "💡",
            "text": "Good content — a few tweaks could push it to excellent.",
            "priority": 2,
        })
    else:
        weaknesses.append({
            "icon": "📉",
            "text": f"Overall quality score is {overall_score}/100. Significant improvements needed.",
            "priority": 1,
        })

    # ─── Readability Insights ────────────────────────────────
    fre = readability_report.get("flesch_reading_ease", 50)
    if fre >= 70:
        strengths.append({
            "icon": "📖",
            "text": "Content is very readable and accessible.",
            "priority": 2,
        })
    elif fre >= 50:
        tips.append({
            "icon": "📝",
            "text": "Readability is moderate. Simplify some sentences for broader appeal.",
            "priority": 3,
        })
    else:
        weaknesses.append({
            "icon": "🔴",
            "text": "Content is difficult to read. Use shorter sentences and simpler words.",
            "priority": 2,
        })

    grade = readability_report.get("flesch_kincaid_grade", 0)
    if grade > 14:
        weaknesses.append({
            "icon": "🎓",
            "text": f"Reading level is Grade {grade} — only suitable for advanced readers.",
            "priority": 3,
        })

    # ─── Tone Insights ───────────────────────────────────────
    tone = tone_report.get("tone", {})
    tone_label = tone.get("tone", "Neutral")
    formality = tone_report.get("formality", {})
    formality_level = formality.get("level", "Formal")

    if tone_label in ["Positive", "Very Positive"]:
        strengths.append({
            "icon": "😊",
            "text": f"Tone is {tone_label.lower()} — great for engaging readers.",
            "priority": 3,
        })
    elif tone_label in ["Negative", "Very Negative"]:
        tips.append({
            "icon": "🎭",
            "text": f"Tone detected as {tone_label.lower()}. Consider softening the language.",
            "priority": 2,
        })

    subjectivity = tone_report.get("subjectivity", {})
    subj_level = subjectivity.get("level", "")
    if subj_level == "Highly Subjective":
        tips.append({
            "icon": "⚖️",
            "text": "Content is highly subjective. Add data or facts to strengthen arguments.",
            "priority": 3,
        })

    # ─── Engagement Insights ─────────────────────────────────
    if engagement_score >= 75:
        strengths.append({
            "icon": "🔥",
            "text": "Content structure is engaging with good variety.",
            "priority": 2,
        })
    elif engagement_score < 50:
        weaknesses.append({
            "icon": "😴",
            "text": "Content lacks engagement. Vary sentence lengths and add questions.",
            "priority": 2,
        })

    # ─── Clarity Insights ────────────────────────────────────
    if clarity_score >= 75:
        strengths.append({
            "icon": "💎",
            "text": "Writing is clear and well-structured.",
            "priority": 2,
        })
    elif clarity_score < 50:
        weaknesses.append({
            "icon": "🌫️",
            "text": "Clarity needs work. Reduce passive voice and add transition words.",
            "priority": 2,
        })

    # ─── SEO Insights ────────────────────────────────────────
    if seo_score >= 70:
        strengths.append({
            "icon": "🔍",
            "text": "Good basic SEO structure.",
            "priority": 3,
        })
    elif seo_score < 50:
        tips.append({
            "icon": "🔍",
            "text": "Improve SEO: aim for 300+ words, clear paragraphs, and keyword focus.",
            "priority": 3,
        })

    # ─── Text Statistics Insights ────────────────────────────
    word_count = text_stats.get("words", 0)
    avg_sent_len = text_stats.get("avg_sentence_length", 0)

    if word_count < 100:
        tips.append({
            "icon": "📏",
            "text": f"Content is short ({word_count} words). Expand for better analysis and SEO.",
            "priority": 2,
        })
    elif word_count > 2500:
        tips.append({
            "icon": "✂️",
            "text": f"Content is lengthy ({word_count} words). Consider breaking into sections.",
            "priority": 4,
        })

    if avg_sent_len > 25:
        tips.append({
            "icon": "📐",
            "text": f"Average sentence length is {avg_sent_len} words. Aim for 15–20.",
            "priority": 3,
        })
    elif 0 < avg_sent_len < 10:
        tips.append({
            "icon": "📐",
            "text": "Sentences are very short. Combine some for better flow.",
            "priority": 4,
        })

    # ─── SEO Keyword Insights ────────────────────────────────
    keywords = seo_report.get("keywords", [])
    if keywords:
        top_kw = keywords[0]
        if top_kw["density"] > 5:
            tips.append({
                "icon": "🔑",
                "text": f"Keyword '{top_kw['keyword']}' density is {top_kw['density']}% — may be too high.",
                "priority": 3,
            })
        elif top_kw["density"] < 1:
            tips.append({
                "icon": "🔑",
                "text": "No dominant keyword detected. Focus on a primary keyword for SEO.",
                "priority": 3,
            })

    vocab_richness = seo_report.get("vocabulary_richness", 0)
    if vocab_richness > 70:
        strengths.append({
            "icon": "📚",
            "text": f"Excellent vocabulary variety ({vocab_richness}% unique words).",
            "priority": 3,
        })
    elif vocab_richness < 40:
        tips.append({
            "icon": "📚",
            "text": "Vocabulary is repetitive. Use synonyms to improve variety.",
            "priority": 4,
        })

    # Sort by priority
    strengths.sort(key=lambda x: x["priority"])
    weaknesses.sort(key=lambda x: x["priority"])
    tips.sort(key=lambda x: x["priority"])

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "tips": tips,
        "total_insights": len(strengths) + len(weaknesses) + len(tips),
    }
