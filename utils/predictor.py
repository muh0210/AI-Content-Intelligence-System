"""
AI Content Intelligence System — Pre-Write Content Predictor (V4)
Predict difficulty, reading level, tone guide, and structure BEFORE writing.
"""

import re
from collections import Counter


# ═══════════════════════════════════════════════════════════════════
# Topic Complexity Analysis
# ═══════════════════════════════════════════════════════════════════

COMPLEX_DOMAINS = {
    "technical": ["algorithm", "machine learning", "neural", "quantum", "blockchain",
                  "cryptocurrency", "api", "framework", "infrastructure", "architecture",
                  "kubernetes", "microservices", "devops", "cloud computing"],
    "academic": ["research", "methodology", "hypothesis", "literature review",
                 "empirical", "theoretical", "dissertation", "thesis", "peer-reviewed",
                 "statistical", "qualitative", "quantitative"],
    "legal": ["compliance", "regulation", "statutory", "jurisdiction", "liability",
              "contractual", "litigation", "arbitration", "intellectual property"],
    "financial": ["portfolio", "derivatives", "amortization", "hedge fund",
                  "capital gains", "securities", "valuation", "fiscal", "monetary policy"],
    "medical": ["diagnosis", "pathology", "pharmacology", "clinical trial",
                "prognosis", "therapeutic", "epidemiology", "oncology"],
    "marketing": ["conversion", "engagement", "brand awareness", "funnel",
                  "retargeting", "ctr", "roi", "lead generation", "seo"],
}

SIMPLE_DOMAINS = {
    "lifestyle": ["recipe", "travel", "fashion", "fitness", "wellness", "hobby"],
    "casual": ["tips", "tricks", "how to", "guide", "beginner", "easy", "simple", "fun"],
}


def detect_topic_domain(topic):
    """Detect which domain a topic belongs to."""
    topic_lower = topic.lower()
    scores = {}

    for domain, keywords in COMPLEX_DOMAINS.items():
        score = sum(1 for kw in keywords if kw in topic_lower)
        if score > 0:
            scores[domain] = score

    for domain, keywords in SIMPLE_DOMAINS.items():
        score = sum(1 for kw in keywords if kw in topic_lower)
        if score > 0:
            scores[domain] = score

    if not scores:
        return "general", 0

    best = max(scores, key=scores.get)
    return best, scores[best]


def predict_difficulty(topic):
    """
    Predict content difficulty score (0-100) based on topic.
    Higher = harder to write well.
    """
    domain, match_strength = detect_topic_domain(topic)
    words = topic.lower().split()
    word_count = len(words)

    # Base difficulty by domain
    domain_difficulty = {
        "technical": 75, "academic": 80, "legal": 85, "financial": 78,
        "medical": 82, "marketing": 55, "lifestyle": 30, "casual": 25,
        "general": 50,
    }
    base = domain_difficulty.get(domain, 50)

    # Adjust by topic length (more specific = harder)
    if word_count > 8:
        base += 10
    elif word_count > 5:
        base += 5

    # Adjust by word complexity
    avg_word_len = sum(len(w) for w in words) / max(1, len(words))
    if avg_word_len > 7:
        base += 10
    elif avg_word_len > 5:
        base += 5

    return max(10, min(100, base))


def recommend_reading_level(difficulty):
    """Recommend target reading level based on difficulty."""
    if difficulty >= 75:
        return {
            "grade": "College+",
            "flesch_target": "30–50",
            "audience": "Experts, professionals, academics",
            "emoji": "🎓",
        }
    elif difficulty >= 55:
        return {
            "grade": "Grade 10–12",
            "flesch_target": "50–65",
            "audience": "Informed readers, business professionals",
            "emoji": "💼",
        }
    elif difficulty >= 35:
        return {
            "grade": "Grade 7–9",
            "flesch_target": "65–80",
            "audience": "General public, blog readers",
            "emoji": "📰",
        }
    else:
        return {
            "grade": "Grade 5–6",
            "flesch_target": "80–95",
            "audience": "Casual readers, social media users",
            "emoji": "💬",
        }


def recommend_tone(domain, topic):
    """Recommend ideal tone for the topic."""
    tone_map = {
        "technical": {"tone": "Precise & Authoritative", "emoji": "🔬",
                      "tips": ["Use technical terminology accurately", "Include code examples or data",
                               "Be concise but thorough", "Define jargon for mixed audiences"]},
        "academic": {"tone": "Formal & Analytical", "emoji": "📚",
                     "tips": ["Use third person perspective", "Support claims with citations",
                              "Maintain objectivity", "Use hedging language (suggests, indicates)"]},
        "legal": {"tone": "Precise & Formal", "emoji": "⚖️",
                  "tips": ["Use exact legal terminology", "Avoid ambiguity",
                           "Reference specific statutes/regulations", "Use passive voice where appropriate"]},
        "financial": {"tone": "Analytical & Data-Driven", "emoji": "📊",
                      "tips": ["Include quantitative data", "Use financial terminology correctly",
                               "Present balanced analysis", "Cite sources for projections"]},
        "medical": {"tone": "Clinical & Evidence-Based", "emoji": "🏥",
                    "tips": ["Reference clinical evidence", "Use medical terminology precisely",
                             "Include dosage/measurement details", "Note limitations and caveats"]},
        "marketing": {"tone": "Persuasive & Engaging", "emoji": "🎯",
                      "tips": ["Lead with benefits", "Use power words", "Include social proof",
                               "End with clear CTAs", "Keep sentences punchy"]},
        "lifestyle": {"tone": "Friendly & Relatable", "emoji": "🌟",
                      "tips": ["Use personal anecdotes", "Be conversational", "Include practical tips",
                               "Use sensory language"]},
        "casual": {"tone": "Conversational & Fun", "emoji": "💬",
                   "tips": ["Use simple language", "Add humor where appropriate", "Be direct",
                            "Use lists and bullets"]},
    }

    return tone_map.get(domain, {
        "tone": "Clear & Balanced", "emoji": "📝",
        "tips": ["Write for your audience", "Use active voice", "Keep paragraphs short",
                 "Include examples"]
    })


def recommend_structure(domain, difficulty):
    """Recommend content structure."""
    if difficulty >= 70:
        return {
            "word_count": "1500–3000",
            "paragraphs": "10–20",
            "sections": ["Introduction", "Background/Context", "Main Analysis",
                         "Supporting Evidence", "Discussion", "Conclusion"],
            "tips": ["Use H2/H3 headings", "Include data tables or charts",
                     "Add a summary/TL;DR at top", "Include references section"],
        }
    elif difficulty >= 45:
        return {
            "word_count": "800–1500",
            "paragraphs": "6–12",
            "sections": ["Hook/Introduction", "Key Points (3–5)", "Examples",
                         "Takeaways", "Conclusion/CTA"],
            "tips": ["Use subheadings every 200 words", "Include bullet points",
                     "Add images/infographics", "End with actionable advice"],
        }
    else:
        return {
            "word_count": "400–800",
            "paragraphs": "4–8",
            "sections": ["Catchy Opening", "Main Content", "Tips/List", "Wrap-up"],
            "tips": ["Keep it scannable", "Use numbered lists", "Add emojis if appropriate",
                     "Include a hook in the first sentence"],
        }


def get_prediction_report(topic):
    """Generate full pre-write prediction report."""
    domain, match_strength = detect_topic_domain(topic)
    difficulty = predict_difficulty(topic)
    reading_level = recommend_reading_level(difficulty)
    tone = recommend_tone(domain, topic)
    structure = recommend_structure(domain, difficulty)

    return {
        "topic": topic,
        "domain": domain,
        "difficulty": difficulty,
        "reading_level": reading_level,
        "tone": tone,
        "structure": structure,
    }
