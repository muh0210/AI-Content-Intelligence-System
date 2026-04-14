"""
AI Content Intelligence System — Unit Tests
Tests for core NLP modules using pytest.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.cleaner import clean_text, get_text_stats, split_sentences, count_words
from utils.readability import get_readability_report, flesch_reading_ease, interpret_flesch
from utils.tone import get_tone_report, analyze_sentiment, classify_tone, detect_formality
from utils.scoring import compute_content_score, get_score_label, DOMAIN_PRESETS
from utils.seo import keyword_density, extract_bigrams, tfidf_keywords, analyze_headline, get_seo_report
from utils.plagiarism import internal_similarity_check, sentence_similarity, ngram_fingerprint, fingerprint_similarity
from utils.rewrite import rule_based_rewrite, fix_common_issues, detect_passive_voice, generate_diff


SAMPLE_TEXT = (
    "The rapid advancement of artificial intelligence has transformed "
    "industries across the globe. From healthcare to finance, AI-powered "
    "systems are now capable of analyzing vast amounts of data and making "
    "decisions that were once the exclusive domain of human experts. "
    "However, this technological revolution has also raised important "
    "questions about ethics, employment, and the future of human creativity."
)

SAMPLE_ACADEMIC = (
    "This study investigates the impact of social media usage on academic "
    "performance among university students. A cross-sectional survey was "
    "conducted with 500 participants from three major universities. The "
    "results indicate a statistically significant negative correlation "
    "between daily social media consumption exceeding four hours and "
    "grade point average (Smith, 2024)."
)


# ═══════════════════════════════════════════════════════════════════
# Cleaner Tests
# ═══════════════════════════════════════════════════════════════════

class TestCleaner:
    def test_clean_text_removes_extra_spaces(self):
        assert "hello world" in clean_text("hello   world")

    def test_clean_text_strips_whitespace(self):
        assert clean_text("  hello  ") == "hello"

    def test_clean_text_handles_empty(self):
        assert clean_text("") == ""
        assert clean_text("   ") == ""

    def test_count_words(self):
        assert count_words("hello world foo") == 3
        assert count_words("") == 0

    def test_get_text_stats(self):
        stats = get_text_stats(SAMPLE_TEXT)
        assert stats["words"] > 0
        assert stats["sentences"] > 0
        assert stats["characters"] > 0
        assert stats["reading_time_min"] > 0

    def test_split_sentences(self):
        sents = split_sentences("Hello world. How are you? I'm fine!")
        assert len(sents) == 3


# ═══════════════════════════════════════════════════════════════════
# Readability Tests
# ═══════════════════════════════════════════════════════════════════

class TestReadability:
    def test_flesch_returns_number(self):
        score = flesch_reading_ease(SAMPLE_TEXT)
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100

    def test_interpret_flesch_easy(self):
        result = interpret_flesch(85)
        assert result["label"] == "Easy"

    def test_interpret_flesch_difficult(self):
        result = interpret_flesch(25)
        assert result["label"] == "Very Difficult"

    def test_readability_report_keys(self):
        report = get_readability_report(SAMPLE_TEXT)
        assert "flesch_reading_ease" in report
        assert "flesch_kincaid_grade" in report
        assert "interpretation" in report
        assert "consensus_grade" in report


# ═══════════════════════════════════════════════════════════════════
# Tone Tests
# ═══════════════════════════════════════════════════════════════════

class TestTone:
    def test_analyze_sentiment_returns_dict(self):
        result = analyze_sentiment(SAMPLE_TEXT)
        assert "polarity" in result
        assert "subjectivity" in result
        assert -1 <= result["polarity"] <= 1

    def test_classify_tone_positive(self):
        result = classify_tone(0.5)
        assert result["tone"] == "Very Positive"

    def test_classify_tone_negative(self):
        result = classify_tone(-0.5)
        assert result["tone"] == "Very Negative"

    def test_classify_tone_neutral(self):
        result = classify_tone(0.0)
        assert result["tone"] == "Neutral"

    def test_detect_formality(self):
        result = detect_formality(SAMPLE_ACADEMIC)
        assert "score" in result
        assert "level" in result

    def test_tone_report_keys(self):
        report = get_tone_report(SAMPLE_TEXT)
        assert "tone" in report
        assert "formality" in report
        assert "sentence_breakdown" in report


# ═══════════════════════════════════════════════════════════════════
# Scoring Tests
# ═══════════════════════════════════════════════════════════════════

class TestScoring:
    def test_compute_score_returns_all_keys(self):
        scores = compute_content_score(SAMPLE_TEXT)
        assert "overall" in scores
        assert "readability" in scores
        assert "engagement" in scores
        assert "clarity" in scores
        assert "seo" in scores
        assert 0 <= scores["overall"] <= 100

    def test_domain_presets_exist(self):
        assert "general" in DOMAIN_PRESETS
        assert "academic" in DOMAIN_PRESETS
        assert "blog" in DOMAIN_PRESETS
        assert "business" in DOMAIN_PRESETS
        assert "seo" in DOMAIN_PRESETS

    def test_domain_scoring_differs(self):
        general = compute_content_score(SAMPLE_TEXT, domain="general")
        academic = compute_content_score(SAMPLE_TEXT, domain="academic")
        assert general["overall"] != academic["overall"]

    def test_custom_weights(self):
        custom = {"readability": 0.5, "engagement": 0.2, "clarity": 0.2, "seo": 0.1}
        scores = compute_content_score(SAMPLE_TEXT, custom_weights=custom)
        assert scores["weights_used"] == custom

    def test_score_label(self):
        assert get_score_label(90)["label"] == "Excellent"
        assert get_score_label(75)["label"] == "Good"
        assert get_score_label(60)["label"] == "Average"
        assert get_score_label(45)["label"] == "Below Average"
        assert get_score_label(20)["label"] == "Poor"


# ═══════════════════════════════════════════════════════════════════
# SEO Tests
# ═══════════════════════════════════════════════════════════════════

class TestSEO:
    def test_keyword_density_returns_list(self):
        result = keyword_density(SAMPLE_TEXT)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_keyword_has_required_keys(self):
        result = keyword_density(SAMPLE_TEXT)
        kw = result[0]
        assert "keyword" in kw
        assert "count" in kw
        assert "density" in kw

    def test_extract_bigrams(self):
        result = extract_bigrams(SAMPLE_TEXT)
        assert isinstance(result, list)

    def test_tfidf_keywords(self):
        result = tfidf_keywords(SAMPLE_TEXT)
        assert isinstance(result, list)

    def test_analyze_headline(self):
        result = analyze_headline("7 Best AI Tools for Content Writing in 2024")
        assert "score" in result
        assert result["score"] > 50  # good headline

    def test_seo_report_keys(self):
        report = get_seo_report(SAMPLE_TEXT, title="AI Revolution")
        assert "keywords" in report
        assert "tfidf_keywords" in report
        assert "topic_clusters" in report
        assert "headline_analysis" in report


# ═══════════════════════════════════════════════════════════════════
# Plagiarism Tests
# ═══════════════════════════════════════════════════════════════════

class TestPlagiarism:
    def test_sentence_similarity_identical(self):
        sim = sentence_similarity("hello world", "hello world")
        assert sim == 1.0

    def test_sentence_similarity_different(self):
        sim = sentence_similarity("hello world", "foobar baz")
        assert sim < 0.5

    def test_ngram_fingerprint(self):
        fp = ngram_fingerprint("This is a test sentence with enough words to extract ngrams from")
        assert isinstance(fp, set)
        assert len(fp) > 0

    def test_internal_similarity_check(self):
        report = internal_similarity_check(SAMPLE_TEXT)
        assert "risk_level" in report
        assert "risk_score" in report
        assert report["risk_level"] in ["Low", "Medium", "High"]

    def test_fingerprint_similarity_identical(self):
        sim = fingerprint_similarity(SAMPLE_TEXT, SAMPLE_TEXT)
        assert sim == 1.0

    def test_fingerprint_similarity_different(self):
        sim = fingerprint_similarity(SAMPLE_TEXT, SAMPLE_ACADEMIC)
        assert sim < 1.0


# ═══════════════════════════════════════════════════════════════════
# Rewrite Tests
# ═══════════════════════════════════════════════════════════════════

class TestRewrite:
    def test_fix_common_issues(self):
        text = "We need to make a decision in order to proceed"
        improved, changes = fix_common_issues(text)
        assert "decide" in improved or "to" in improved

    def test_detect_passive_voice(self):
        text = "The experiment was conducted in the lab and was repeated twice"
        result = detect_passive_voice(text)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_generate_diff(self):
        diff = generate_diff("hello world", "hello beautiful world")
        assert isinstance(diff, list)
        assert any(d["type"] == "added" for d in diff)

    def test_rule_based_rewrite_returns_keys(self):
        result = rule_based_rewrite(SAMPLE_TEXT)
        assert "improved_text" in result
        assert "changes" in result
        assert "diff" in result
        assert "grammar" in result


# ═══════════════════════════════════════════════════════════════════
# V4 Modules — Predictor Tests
# ═══════════════════════════════════════════════════════════════════

from utils.predictor import get_prediction_report

class TestPredictor:
    def test_prediction_returns_keys(self):
        result = get_prediction_report("artificial intelligence in healthcare")
        assert "difficulty" in result
        assert "reading_level" in result
        assert "tone" in result
        assert "structure" in result
        assert "domain" in result

    def test_prediction_difficulty_range(self):
        result = get_prediction_report("machine learning")
        assert 0 <= result["difficulty"] <= 100

    def test_prediction_structure_has_word_count(self):
        result = get_prediction_report("content marketing strategy")
        assert "word_count" in result["structure"]
        assert "sections" in result["structure"]


# ═══════════════════════════════════════════════════════════════════
# V4 Modules — Content DNA Tests
# ═══════════════════════════════════════════════════════════════════

from utils.content_dna import get_content_dna

class TestContentDNA:
    def test_dna_returns_radar(self):
        dna = get_content_dna(SAMPLE_TEXT)
        assert "radar" in dna
        assert isinstance(dna["radar"], dict)

    def test_dna_returns_vocabulary(self):
        dna = get_content_dna(SAMPLE_TEXT)
        assert "vocabulary" in dna
        assert "ttr" in dna["vocabulary"]

    def test_dna_returns_voice(self):
        dna = get_content_dna(SAMPLE_TEXT)
        assert "voice" in dna
        assert "active_pct" in dna["voice"]


# ═══════════════════════════════════════════════════════════════════
# V4 Modules — Emotions Tests
# ═══════════════════════════════════════════════════════════════════

from utils.emotions import get_emotion_report

class TestEmotions:
    def test_emotion_report_keys(self):
        emo = get_emotion_report(SAMPLE_TEXT, goal="trust")
        assert "overall" in emo
        assert "alignment" in emo

    def test_emotion_overall_has_dominant(self):
        emo = get_emotion_report(SAMPLE_TEXT, goal="trust")
        assert "dominant" in emo["overall"]

    def test_emotion_paragraphs(self):
        emo = get_emotion_report(SAMPLE_TEXT, goal="trust")
        assert "paragraphs" in emo


# ═══════════════════════════════════════════════════════════════════
# V4 Modules — Conversion Tests
# ═══════════════════════════════════════════════════════════════════

from utils.conversion import get_conversion_score

class TestConversion:
    def test_conversion_score_range(self):
        conv = get_conversion_score(SAMPLE_TEXT)
        assert 0 <= conv["overall_score"] <= 100

    def test_conversion_has_components(self):
        conv = get_conversion_score(SAMPLE_TEXT)
        assert "components" in conv
        assert isinstance(conv["components"], dict)

    def test_conversion_has_verdict(self):
        conv = get_conversion_score(SAMPLE_TEXT)
        assert "verdict" in conv
        assert "color" in conv


# ═══════════════════════════════════════════════════════════════════
# V4 Modules — ROI Tests
# ═══════════════════════════════════════════════════════════════════

from utils.roi import get_roi_report

class TestROI:
    def test_roi_returns_traffic(self):
        scores = compute_content_score(SAMPLE_TEXT)
        roi = get_roi_report(scores, 500)
        assert "traffic" in roi
        assert "low" in roi["traffic"]
        assert "high" in roi["traffic"]

    def test_roi_returns_value(self):
        scores = compute_content_score(SAMPLE_TEXT)
        roi = get_roi_report(scores, 500)
        assert "value" in roi
        assert "monthly_value" in roi["value"]

    def test_roi_returns_tips(self):
        scores = compute_content_score(SAMPLE_TEXT)
        roi = get_roi_report(scores, 500)
        assert "tips" in roi
        assert isinstance(roi["tips"], list)


# ═══════════════════════════════════════════════════════════════════
# V4 Modules — Certificate Tests
# ═══════════════════════════════════════════════════════════════════

from utils.certificate import generate_certificate, HAS_FPDF

class TestCertificate:
    def test_certificate_generates_bytes(self):
        if not HAS_FPDF:
            return  # Skip if fpdf2 not installed
        cert_data = {
            "title": "Test Article",
            "scores": {"overall": 75, "readability": 80, "engagement": 70, "clarity": 72, "seo": 65},
            "word_count": 500,
            "tone": "Positive",
            "readability_label": "Easy",
            "plagiarism_risk": "Low",
            "ai_detection": "Likely Human",
            "seo_intent": "Informational",
            "conversion_score": None,
        }
        result = generate_certificate(cert_data)
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 100

    def test_certificate_without_fpdf_returns_none(self):
        # Verify graceful fallback behavior
        cert_data = {"title": "Test", "scores": {"overall": 50}}
        if not HAS_FPDF:
            result = generate_certificate(cert_data)
            assert result is None


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
