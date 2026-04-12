"""
AI Content Intelligence System — Content Readiness Certificate (V4)
Generate branded PDF report certifying content quality.
"""

import io
from datetime import datetime

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False


class CertificatePDF(FPDF):
    """Custom PDF with branding."""

    def header(self):
        self.set_fill_color(20, 20, 35)
        self.rect(0, 0, 210, 297, 'F')
        self.set_fill_color(124, 77, 255)
        self.rect(0, 0, 210, 4, 'F')

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 120)
        self.cell(0, 10, f"AI Content Intelligence System | Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 0, "C")


def _add_section(pdf, title, y_start=None):
    """Add section header."""
    if y_start:
        pdf.set_y(y_start)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(124, 77, 255)
    pdf.cell(0, 8, title, 0, 1, "L")
    pdf.set_draw_color(124, 77, 255)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)


def _add_metric(pdf, label, value, color=(255, 255, 255)):
    """Add metric row."""
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(160, 160, 180)
    pdf.cell(70, 6, label, 0, 0, "L")
    pdf.set_text_color(*color)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, str(value), 0, 1, "L")


def _score_color(score):
    """Return RGB tuple based on score."""
    if score >= 70:
        return (0, 230, 118)
    elif score >= 50:
        return (255, 167, 38)
    else:
        return (239, 83, 80)


def generate_certificate(data):
    """
    Generate Content Readiness Certificate PDF.

    data: dict with keys:
        - title: content title
        - scores: {overall, readability, engagement, clarity, seo}
        - word_count: int
        - tone: str
        - readability_label: str
        - plagiarism_risk: str
        - ai_detection: str (optional)
        - seo_intent: str (optional)
        - content_dna: dict (optional)
        - emotions: dict (optional)
        - conversion_score: float (optional)
    """
    if not HAS_FPDF:
        return None

    pdf = CertificatePDF()
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(124, 77, 255)
    pdf.cell(0, 15, "Content Readiness Certificate", 0, 1, "C")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(160, 160, 180)
    pdf.cell(0, 6, f"Issued: {datetime.now().strftime('%B %d, %Y at %H:%M')}", 0, 1, "C")
    pdf.ln(5)

    # Content title
    pdf.set_fill_color(30, 30, 50)
    pdf.rect(10, pdf.get_y(), 190, 14, 'F')
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(255, 255, 255)
    title_text = data.get("title", "Untitled Content")[:80]
    pdf.cell(0, 14, f"  {title_text}", 0, 1, "L")
    pdf.ln(5)

    # Overall Score (large)
    overall = data.get("scores", {}).get("overall", 0)
    color = _score_color(overall)

    pdf.set_fill_color(30, 30, 50)
    pdf.rect(10, pdf.get_y(), 190, 30, 'F')
    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(*color)
    pdf.cell(80, 30, f"  {overall}/100", 0, 0, "L")
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(200, 200, 220)
    grade = "EXCELLENT" if overall >= 85 else "GOOD" if overall >= 70 else "AVERAGE" if overall >= 55 else "NEEDS WORK"
    pdf.cell(0, 30, f"Grade: {grade}", 0, 1, "L")
    pdf.ln(5)

    # Quality Scores
    _add_section(pdf, "Quality Scores")
    scores = data.get("scores", {})
    _add_metric(pdf, "Readability Score:", f"{scores.get('readability', 0)}/100", _score_color(scores.get('readability', 0)))
    _add_metric(pdf, "Engagement Score:", f"{scores.get('engagement', 0)}/100", _score_color(scores.get('engagement', 0)))
    _add_metric(pdf, "Clarity Score:", f"{scores.get('clarity', 0)}/100", _score_color(scores.get('clarity', 0)))
    _add_metric(pdf, "SEO Score:", f"{scores.get('seo', 0)}/100", _score_color(scores.get('seo', 0)))
    pdf.ln(3)

    # Content Details
    _add_section(pdf, "Content Analysis")
    _add_metric(pdf, "Word Count:", str(data.get("word_count", 0)))
    _add_metric(pdf, "Tone:", data.get("tone", "N/A"))
    _add_metric(pdf, "Reading Level:", data.get("readability_label", "N/A"))
    if data.get("seo_intent"):
        _add_metric(pdf, "Search Intent:", data["seo_intent"])
    pdf.ln(3)

    # Authenticity
    _add_section(pdf, "Authenticity & Compliance")
    plag_risk = data.get("plagiarism_risk", "N/A")
    plag_color = (0, 230, 118) if "Low" in str(plag_risk) else (255, 167, 38) if "Medium" in str(plag_risk) else (239, 83, 80)
    _add_metric(pdf, "Plagiarism Risk:", plag_risk, plag_color)
    if data.get("ai_detection"):
        ai_label = data["ai_detection"]
        ai_color = (0, 230, 118) if "Human" in str(ai_label) else (255, 167, 38) if "Mixed" in str(ai_label) else (239, 83, 80)
        _add_metric(pdf, "AI Detection:", ai_label, ai_color)
    pdf.ln(3)

    # Optional: Conversion Score
    if data.get("conversion_score") is not None:
        _add_section(pdf, "Business Metrics")
        conv = data["conversion_score"]
        _add_metric(pdf, "Conversion Probability:", f"{conv}/100", _score_color(conv))
    pdf.ln(3)

    # Verdict
    pdf.ln(5)
    pdf.set_fill_color(124, 77, 255)
    if overall >= 70:
        pdf.rect(10, pdf.get_y(), 190, 18, 'F')
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 18, "  CERTIFIED: Content meets quality standards for publication", 0, 1, "L")
    elif overall >= 50:
        pdf.set_fill_color(255, 167, 38)
        pdf.rect(10, pdf.get_y(), 190, 18, 'F')
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 18, "  CONDITIONAL: Content needs minor improvements before publication", 0, 1, "L")
    else:
        pdf.set_fill_color(239, 83, 80)
        pdf.rect(10, pdf.get_y(), 190, 18, 'F')
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 18, "  NOT READY: Content requires significant revision", 0, 1, "L")

    # Return as bytes
    pdf_bytes = pdf.output()
    return bytes(pdf_bytes)
