"""
AI Content Intelligence System — AI Rewrite Engine (V2 — Upgraded)
Rule-based + Grammar correction + optional OpenAI rewriting.
Includes change explanations, audience-aware rewriting, and thesis helper.
"""

import re
from config import AUDIENCE_PRESETS


# ═══════════════════════════════════════════════════════════════════
# Grammar Correction Engine (FREE — No API Key)
# ═══════════════════════════════════════════════════════════════════

def grammar_check(text):
    """
    Check grammar using LanguageTool (free, local).
    Returns corrected text and list of corrections with explanations.
    """
    try:
        import language_tool_python
        tool = language_tool_python.LanguageTool("en-US")
        matches = tool.check(text)
        corrected = language_tool_python.utils.correct(text, matches)

        corrections = []
        for match in matches[:15]:  # limit to avoid overload
            corrections.append({
                "original": text[match.offset:match.offset + match.errorLength],
                "suggestion": match.replacements[0] if match.replacements else "—",
                "rule": match.ruleId,
                "reason": match.message,
                "category": match.category,
                "context": match.context,
            })

        tool.close()

        return {
            "corrected_text": corrected,
            "corrections": corrections,
            "total_issues": len(matches),
            "available": True,
        }
    except ImportError:
        return {
            "corrected_text": text,
            "corrections": [],
            "total_issues": 0,
            "available": False,
            "error": "language_tool_python not installed. Install with: pip install language_tool_python",
        }
    except Exception as e:
        return {
            "corrected_text": text,
            "corrections": [],
            "total_issues": 0,
            "available": False,
            "error": str(e),
        }


# ═══════════════════════════════════════════════════════════════════
# Rule-Based Rewrite Engine (Enhanced V2)
# ═══════════════════════════════════════════════════════════════════

def fix_common_issues(text):
    """Apply rule-based text improvements with change tracking."""
    improved = text
    changes_detail = []

    # Fix double spaces
    new = re.sub(r"  +", " ", improved)
    if new != improved:
        changes_detail.append({
            "type": "whitespace",
            "reason": "Removed extra whitespace for cleaner formatting.",
        })
        improved = new

    # Capitalize first letter of sentences
    new = re.sub(
        r"((?:^|[.!?]\s+))([a-z])",
        lambda m: m.group(1) + m.group(2).upper(),
        improved,
    )
    if new != improved:
        changes_detail.append({
            "type": "capitalization",
            "reason": "Capitalized sentence beginnings for proper grammar.",
        })
        improved = new

    # Fix common redundancies (with explanations)
    redundancies = {
        r"\bin order to\b": ("to", "Simplified verbose phrase 'in order to' → 'to'"),
        r"\bdue to the fact that\b": ("because", "Replaced wordy 'due to the fact that' → 'because'"),
        r"\bat this point in time\b": ("now", "Simplified 'at this point in time' → 'now'"),
        r"\bin the event that\b": ("if", "Simplified 'in the event that' → 'if'"),
        r"\bit is important to note that\b": ("notably", "Removed filler phrase 'it is important to note that'"),
        r"\bin the near future\b": ("soon", "Simplified 'in the near future' → 'soon'"),
        r"\bfor the purpose of\b": ("to", "Simplified 'for the purpose of' → 'to'"),
        r"\bin spite of the fact that\b": ("although", "Simplified wordy connector"),
        r"\bon a daily basis\b": ("daily", "Simplified 'on a daily basis' → 'daily'"),
        r"\bwith regard to\b": ("regarding", "Simplified 'with regard to' → 'regarding'"),
        r"\bin the process of\b": ("while", "Simplified 'in the process of' → 'while'"),
        r"\bhas the ability to\b": ("can", "Simplified 'has the ability to' → 'can'"),
        r"\bis able to\b": ("can", "Simplified 'is able to' → 'can'"),
        r"\bmake a decision\b": ("decide", "Replaced noun form 'make a decision' → 'decide'"),
        r"\btake into consideration\b": ("consider", "Simplified 'take into consideration' → 'consider'"),
        r"\bgive consideration to\b": ("consider", "Simplified to active verb"),
        r"\bcome to the conclusion\b": ("conclude", "Simplified 'come to the conclusion' → 'conclude'"),
        r"\bhas a tendency to\b": ("tends to", "Simplified 'has a tendency to' → 'tends to'"),
        r"\bthe majority of\b": ("most", "Simplified 'the majority of' → 'most'"),
        r"\ba large number of\b": ("many", "Simplified 'a large number of' → 'many'"),
        r"\bin close proximity to\b": ("near", "Simplified 'in close proximity to' → 'near'"),
        r"\buntil such time as\b": ("until", "Simplified 'until such time as' → 'until'"),
        r"\bwith reference to\b": ("about", "Simplified 'with reference to' → 'about'"),
        r"\bit goes without saying\b": ("clearly", "Removed filler 'it goes without saying'"),
        r"\bas a matter of fact\b": ("in fact", "Simplified 'as a matter of fact' → 'in fact'"),
    }

    for pattern, (replacement, explanation) in redundancies.items():
        new = re.sub(pattern, replacement, improved, flags=re.IGNORECASE)
        if new != improved:
            changes_detail.append({
                "type": "redundancy",
                "reason": explanation,
            })
            improved = new

    return improved, changes_detail


def detect_passive_voice(text):
    """Detect passive voice instances with context and suggestions."""
    passive_patterns = [
        (r"\b(was\s+\w+ed)\b", "active voice", "Passive → Active: Rewrite to specify the subject."),
        (r"\b(were\s+\w+ed)\b", "active voice", "Passive → Active: Rewrite to specify the subject."),
        (r"\b(been\s+\w+ed)\b", "active voice", "Passive → Active: Consider rephrasing."),
        (r"\b(is being\s+\w+ed)\b", "active voice", "Passive → Active: Use present tense instead."),
        (r"\b(are being\s+\w+ed)\b", "active voice", "Passive → Active: Make the subject clear."),
    ]

    suggestions = []
    for pattern, fix_type, explanation in passive_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            suggestions.append({
                "text": match.group(),
                "suggestion": fix_type,
                "reason": explanation,
                "position": match.start(),
            })

    return suggestions


def suggest_transitions(text):
    """Suggest transition words between sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) <= 1:
        return []

    transition_map = {
        "addition": ["Furthermore, ", "Moreover, ", "Additionally, ", "In addition, "],
        "contrast": ["However, ", "On the other hand, ", "Nevertheless, ", "Conversely, "],
        "cause": ["Consequently, ", "As a result, ", "Therefore, ", "Thus, "],
        "example": ["For example, ", "For instance, ", "Specifically, ", "In particular, "],
    }

    existing_transitions = [
        "however", "therefore", "moreover", "furthermore",
        "additionally", "consequently", "nevertheless", "specifically",
        "in addition", "for example", "as a result", "on the other hand",
    ]

    suggestions = []
    for i in range(1, min(len(sentences), 10)):
        has_transition = any(
            sentences[i].lower().startswith(t) for t in existing_transitions
        )
        if not has_transition and len(sentences[i].split()) > 5:
            suggestions.append({
                "after_sentence": i,
                "sentence_preview": sentences[i][:60] + "...",
                "options": {
                    cat: opts[0] for cat, opts in transition_map.items()
                },
            })

    return suggestions


def generate_diff(original, improved):
    """
    Generate a word-level diff between original and improved text.
    Returns list of diff segments: unchanged, added, removed.
    """
    original_words = original.split()
    improved_words = improved.split()

    from difflib import SequenceMatcher
    matcher = SequenceMatcher(None, original_words, improved_words)

    diff_segments = []
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            diff_segments.append({
                "type": "unchanged",
                "text": " ".join(original_words[i1:i2]),
            })
        elif op == "replace":
            diff_segments.append({
                "type": "removed",
                "text": " ".join(original_words[i1:i2]),
            })
            diff_segments.append({
                "type": "added",
                "text": " ".join(improved_words[j1:j2]),
            })
        elif op == "insert":
            diff_segments.append({
                "type": "added",
                "text": " ".join(improved_words[j1:j2]),
            })
        elif op == "delete":
            diff_segments.append({
                "type": "removed",
                "text": " ".join(original_words[i1:i2]),
            })

    return diff_segments


def rule_based_rewrite(text):
    """
    Comprehensive rule-based rewriting with explanations.
    Returns improved text, changes, diff, and suggestions.
    """
    changes = []
    original = text

    # Step 1: Fix redundancies and common issues
    improved, detail_changes = fix_common_issues(text)
    if detail_changes:
        changes.append(f"✅ Fixed {len(detail_changes)} writing issue(s)")

    # Step 2: Grammar correction (free, no API)
    grammar_result = grammar_check(improved)
    if grammar_result["available"] and grammar_result["total_issues"] > 0:
        improved = grammar_result["corrected_text"]
        changes.append(f"📝 Corrected {grammar_result['total_issues']} grammar issue(s)")

    # Step 3: Passive voice detection
    passive = detect_passive_voice(improved)
    if passive:
        changes.append(f"⚠️ Found {len(passive)} passive voice instance(s)")

    # Step 4: Transition suggestions
    transitions = suggest_transitions(improved)
    if transitions:
        changes.append(f"💡 {len(transitions)} transition opportunity(s) detected")

    if not changes:
        changes.append("✨ Text is already well-written — minimal changes needed")

    # Generate diff
    diff = generate_diff(original, improved)

    return {
        "improved_text": improved,
        "changes": changes,
        "change_details": detail_changes,
        "grammar": grammar_result,
        "passive_suggestions": passive,
        "transition_suggestions": transitions,
        "diff": diff,
    }


# ═══════════════════════════════════════════════════════════════════
# AI-Powered Rewrite Engine (Optional — OpenAI)
# ═══════════════════════════════════════════════════════════════════

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

        improved = response.choices[0].message.content.strip()
        diff = generate_diff(text, improved)

        return {
            "success": True,
            "improved_text": improved,
            "audience": preset["label"],
            "model": model,
            "diff": diff,
        }

    except ImportError:
        return {"success": False, "error": "OpenAI package not installed."}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════
# Thesis Helper Mode (Enhanced V2)
# ═══════════════════════════════════════════════════════════════════

def check_citation_format(text):
    """Detect and classify citation format used in text."""
    formats = {
        "APA": {
            "patterns": [r"\([A-Z][a-z]+,\s*\d{4}\)", r"\([A-Z][a-z]+\s+(?:&|and)\s+[A-Z][a-z]+,\s*\d{4}\)"],
            "example": "(Author, 2024)",
            "found": [],
        },
        "Harvard": {
            "patterns": [r"[A-Z][a-z]+\s+\(\d{4}\)", r"[A-Z][a-z]+\s+and\s+[A-Z][a-z]+\s+\(\d{4}\)"],
            "example": "Author (2024)",
            "found": [],
        },
        "IEEE": {
            "patterns": [r"\[\d+\]"],
            "example": "[1]",
            "found": [],
        },
        "Vancouver": {
            "patterns": [r"\(\d+\)", r"(?<!\w)\d+(?:\.\s)"],
            "example": "(1)",
            "found": [],
        },
    }

    detected = {}
    for fmt, info in formats.items():
        count = 0
        for pattern in info["patterns"]:
            matches = re.findall(pattern, text)
            count += len(matches)
            info["found"].extend(matches[:3])
        if count > 0:
            detected[fmt] = {"count": count, "examples": info["found"][:3]}

    return detected


def analyze_argument_coherence(text):
    """Analyze argument structure and coherence."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    issues = []
    score = 70  # base

    # Check for claim markers
    claim_words = ["argue", "claim", "suggest", "propose", "assert", "demonstrate", "show", "prove"]
    evidence_words = ["evidence", "data", "study", "research", "findings", "results", "analysis"]
    conclusion_words = ["therefore", "thus", "consequently", "hence", "conclude", "in conclusion"]

    text_lower = text.lower()
    has_claims = any(w in text_lower for w in claim_words)
    has_evidence = any(w in text_lower for w in evidence_words)
    has_conclusion = any(w in text_lower for w in conclusion_words)

    if has_claims and has_evidence:
        score += 15
    elif has_claims:
        issues.append("🔍 Claims detected but no supporting evidence found. Add data or citations.")
        score -= 10
    elif has_evidence:
        issues.append("📊 Evidence present but no clear claims. State your argument explicitly.")
        score -= 5

    if not has_conclusion and len(sentences) > 5:
        issues.append("📌 No conclusion markers found. Consider adding a concluding statement.")
        score -= 5

    # Check logical connectors
    logical_connectors = [
        "because", "since", "as a result", "therefore", "however",
        "moreover", "furthermore", "in contrast", "on the other hand",
    ]
    connector_count = sum(1 for c in logical_connectors if c in text_lower)
    if connector_count >= 3:
        score += 10
    elif connector_count == 0 and len(sentences) > 3:
        issues.append("🔗 No logical connectors found. Use words like 'however', 'therefore', 'moreover'.")
        score -= 10

    return {
        "score": max(0, min(100, score)),
        "has_claims": has_claims,
        "has_evidence": has_evidence,
        "has_conclusion": has_conclusion,
        "connector_count": connector_count,
        "issues": issues,
    }


def thesis_helper(text, api_key=None):
    """
    Enhanced thesis helper: structure analysis, citation checks,
    coherence scoring, and academic suggestions.
    """
    suggestions = []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    words = text.split()
    word_count = len(words)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    text_lower = text.lower()

    # ── Structure Analysis ──
    structure_keywords = {
        "introduction": ["introduction", "background", "context", "this paper", "this study", "this research", "aim of"],
        "literature_review": ["literature", "previous studies", "existing research", "prior work", "review of"],
        "methodology": ["method", "methodology", "approach", "procedure", "data collection", "participants", "sample"],
        "results": ["results", "findings", "analysis", "data shows", "we found", "table", "figure"],
        "discussion": ["discussion", "implications", "interpretation", "explains", "suggests that"],
        "conclusion": ["conclusion", "summary", "in conclusion", "to summarize", "in summary", "future work"],
    }

    found_sections = {}
    for section, keywords in structure_keywords.items():
        found_sections[section] = any(kw in text_lower for kw in keywords)

    missing = [s.replace("_", " ").title() for s, found in found_sections.items() if not found]
    if missing:
        suggestions.append(f"📋 Missing sections: {', '.join(missing)}")

    # ── Citation Analysis ──
    citations = check_citation_format(text)
    if citations:
        formats_found = list(citations.keys())
        if len(formats_found) > 1:
            suggestions.append(
                f"⚠️ Mixed citation formats detected: {', '.join(formats_found)}. "
                "Use one consistent format."
            )
        else:
            total = sum(c["count"] for c in citations.values())
            suggestions.append(f"📚 {total} citations found ({formats_found[0]} format)")
    else:
        suggestions.append("📚 No citations detected. Add references to support your claims.")

    # ── Argument Coherence ──
    coherence = analyze_argument_coherence(text)
    if coherence["issues"]:
        suggestions.extend(coherence["issues"])

    # ── Word Count Check ──
    if word_count < 150:
        suggestions.append("📝 Content is short. Aim for 150–300 words for an abstract, 2000+ for a full paper.")
    elif word_count > 500 and not found_sections.get("methodology"):
        suggestions.append("📝 Long text without methodology section. Consider adding research methods.")

    # ── Hedging Language ──
    hedging_words = ["might", "could", "possibly", "perhaps", "may", "seems", "appears"]
    hedging_count = sum(1 for w in words if w.lower() in hedging_words)
    if hedging_count > 3:
        suggestions.append(f"⚡ Reduce hedging language ({hedging_count} instances). Use stronger assertions.")

    # ── First Person Check ──
    first_person = ["i think", "i believe", "in my opinion", "i feel"]
    if any(fp in text_lower for fp in first_person):
        suggestions.append("🎓 Avoid first-person opinions. Use objective language (e.g., 'The data suggests...').")

    # ── Sentence Length ──
    if sentences:
        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_len > 30:
            suggestions.append(f"📐 Average sentence length is {avg_len:.0f} words. Academic writing works best at 20–25 words.")

    if not suggestions:
        suggestions.append("✅ Content follows good academic structure!")

    result = {
        "suggestions": suggestions,
        "found_sections": found_sections,
        "word_count": word_count,
        "paragraph_count": len(paragraphs),
        "citations": citations,
        "coherence": coherence,
    }

    # AI improvement (optional)
    if api_key:
        ai_result = ai_rewrite(text, api_key, audience="academic")
        if ai_result["success"]:
            result["ai_improved"] = ai_result["improved_text"]

    return result
