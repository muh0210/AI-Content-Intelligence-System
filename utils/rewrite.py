"""
AI Content Intelligence System — AI Rewrite Engine
Rule-based improvements + optional OpenAI-powered rewriting.
"""

import re
from config import AUDIENCE_PRESETS


# ─── Rule-Based Rewrite Engine ─────────────────────────────────

def fix_common_issues(text):
    """Apply rule-based text improvements."""
    improved = text

    # Fix double spaces
    improved = re.sub(r"  +", " ", improved)

    # Capitalize first letter of sentences
    improved = re.sub(
        r"((?:^|[.!?]\s+))([a-z])",
        lambda m: m.group(1) + m.group(2).upper(),
        improved,
    )

    # Fix common redundancies
    redundancies = {
        r"\bin order to\b": "to",
        r"\bdue to the fact that\b": "because",
        r"\bat this point in time\b": "now",
        r"\bin the event that\b": "if",
        r"\bit is important to note that\b": "notably",
        r"\bin the near future\b": "soon",
        r"\bfor the purpose of\b": "to",
        r"\bin spite of the fact that\b": "although",
        r"\bon a daily basis\b": "daily",
        r"\bwith regard to\b": "regarding",
        r"\bin the process of\b": "while",
        r"\bhas the ability to\b": "can",
        r"\bis able to\b": "can",
        r"\bmake a decision\b": "decide",
        r"\btake into consideration\b": "consider",
        r"\bgive consideration to\b": "consider",
        r"\bcome to the conclusion\b": "conclude",
        r"\bhas a tendency to\b": "tends to",
        r"\bthe majority of\b": "most",
        r"\ba large number of\b": "many",
        r"\bin close proximity to\b": "near",
    }

    for pattern, replacement in redundancies.items():
        improved = re.sub(pattern, replacement, improved, flags=re.IGNORECASE)

    return improved


def improve_passive_voice(text):
    """Flag and suggest passive voice improvements."""
    passive_patterns = [
        (r"\bwas (\w+ed)\b", "Consider using active voice"),
        (r"\bwere (\w+ed)\b", "Consider using active voice"),
        (r"\bbeen (\w+ed)\b", "Consider using active voice"),
        (r"\bis being (\w+ed)\b", "Consider using active voice"),
    ]

    suggestions = []
    for pattern, msg in passive_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            suggestions.append({
                "text": match.group(),
                "suggestion": msg,
                "position": match.start(),
            })

    return suggestions


def enhance_transitions(text):
    """Add transition suggestions between sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) <= 1:
        return text

    transition_options = [
        "Furthermore, ", "Moreover, ", "Additionally, ",
        "In addition, ", "Consequently, ", "As a result, ",
        "However, ", "On the other hand, ", "Nevertheless, ",
    ]

    # Don't actually modify — return suggestions
    suggestions = []
    for i in range(1, len(sentences)):
        # Check if sentence already starts with a transition
        has_transition = any(
            sentences[i].lower().startswith(t.lower().strip(", "))
            for t in transition_options
        )
        if not has_transition and len(sentences[i].split()) > 5:
            suggestions.append({
                "after_sentence": i,
                "options": transition_options[:3],
            })

    return suggestions


def rule_based_rewrite(text):
    """
    Perform comprehensive rule-based rewriting.
    Returns improved text and list of changes made.
    """
    changes = []
    improved = text

    # Step 1: Fix common issues
    fixed = fix_common_issues(improved)
    if fixed != improved:
        changes.append("✅ Fixed redundant phrases and common writing issues")
        improved = fixed

    # Step 2: Get passive voice suggestions
    passive_suggestions = improve_passive_voice(improved)
    if passive_suggestions:
        changes.append(f"⚠️ Found {len(passive_suggestions)} passive voice instance(s)")

    # Step 3: Get transition suggestions
    transition_suggestions = enhance_transitions(improved)
    if isinstance(transition_suggestions, list) and transition_suggestions:
        changes.append(f"💡 {len(transition_suggestions)} transition opportunity(s) detected")

    if not changes:
        changes.append("✨ Text is already well-written — minimal changes needed")

    return {
        "improved_text": improved,
        "changes": changes,
        "passive_suggestions": passive_suggestions if passive_suggestions else [],
        "transition_suggestions": transition_suggestions if isinstance(transition_suggestions, list) else [],
    }


# ─── AI-Powered Rewrite Engine ──────────────────────────────────

def ai_rewrite(text, api_key, audience="business", model="gpt-4"):
    """
    Rewrite text using OpenAI API.
    Audience: 'academic', 'business', 'casual'
    """
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        preset = AUDIENCE_PRESETS.get(audience, AUDIENCE_PRESETS["business"])
        prompt = f"""{preset['prompt_modifier']}

Original text:
\"\"\"
{text}
\"\"\"

Provide the improved version only, without any explanations or prefixes."""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert content editor and writing improvement specialist.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        return {
            "success": True,
            "improved_text": response.choices[0].message.content.strip(),
            "audience": preset["label"],
            "model": model,
        }

    except ImportError:
        return {"success": False, "error": "OpenAI package not installed."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def thesis_helper(text, api_key=None):
    """
    Thesis helper mode: structure suggestions and abstract improvement.
    Works with or without API key.
    """
    suggestions = []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    words = text.split()
    word_count = len(words)

    # Structure analysis
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    # Check for thesis structure components
    structure_keywords = {
        "introduction": ["introduction", "background", "context", "this paper", "this study", "this research"],
        "methodology": ["method", "methodology", "approach", "procedure", "data collection"],
        "results": ["results", "findings", "analysis", "data shows", "we found"],
        "conclusion": ["conclusion", "summary", "in conclusion", "to summarize", "in summary"],
    }

    found_sections = {}
    text_lower = text.lower()
    for section, keywords in structure_keywords.items():
        found_sections[section] = any(kw in text_lower for kw in keywords)

    missing_sections = [s for s, found in found_sections.items() if not found]
    if missing_sections:
        suggestions.append(
            f"📋 Consider adding these sections: {', '.join(missing_sections).title()}"
        )

    # Abstract length check
    if word_count < 150:
        suggestions.append("📝 Abstract/content is quite short. Aim for at least 150–300 words.")
    elif word_count > 500:
        suggestions.append("📝 Consider condensing. Academic abstracts typically are 150–300 words.")

    # Check for hedging language
    hedging_words = ["might", "could", "possibly", "perhaps", "may", "seems"]
    hedging_count = sum(1 for w in words if w.lower() in hedging_words)
    if hedging_count > 3:
        suggestions.append(
            "⚡ Reduce hedging language for stronger academic tone. "
            f"Found {hedging_count} instances."
        )

    # Citation check
    citation_patterns = [r"\(\d{4}\)", r"\[\d+\]", r"et al\."]
    has_citations = any(re.search(p, text) for p in citation_patterns)
    if not has_citations:
        suggestions.append("📚 No citations detected. Consider adding references to support claims.")

    # First person check
    first_person = ["i think", "i believe", "in my opinion", "i feel"]
    if any(fp in text_lower for fp in first_person):
        suggestions.append("🎓 Avoid first-person opinions in academic writing. Use objective language.")

    if not suggestions:
        suggestions.append("✅ Content follows good academic structure!")

    result = {
        "suggestions": suggestions,
        "found_sections": found_sections,
        "word_count": word_count,
        "paragraph_count": len(paragraphs),
    }

    # If API key provided, offer AI-powered abstract improvement
    if api_key:
        ai_result = ai_rewrite(text, api_key, audience="academic")
        if ai_result["success"]:
            result["ai_improved"] = ai_result["improved_text"]

    return result
