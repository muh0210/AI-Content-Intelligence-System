"""
AI Content Intelligence System — Content Readiness Certificate (V4 Elite)
Generate branded, professional-grade PDF report certifying content quality.
Features: decorative borders, visual score bars, watermarks, modern typography.
"""

import io
import math
from datetime import datetime

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False


def _score_color(score):
    """Return RGB tuple based on score."""
    if score >= 80:
        return (0, 200, 100)
    elif score >= 65:
        return (76, 175, 80)
    elif score >= 50:
        return (255, 167, 38)
    else:
        return (239, 83, 80)


def _grade_label(score):
    """Return grade label and emoji-safe text."""
    if score >= 90:
        return "OUTSTANDING", "A+"
    elif score >= 80:
        return "EXCELLENT", "A"
    elif score >= 70:
        return "GOOD", "B+"
    elif score >= 60:
        return "ABOVE AVERAGE", "B"
    elif score >= 50:
        return "AVERAGE", "C"
    else:
        return "NEEDS IMPROVEMENT", "D"


class CertificatePDF(FPDF):
    """Custom branded PDF with premium visual design."""

    def header(self):
        # Full dark background
        self.set_fill_color(15, 17, 23)
        self.rect(0, 0, 210, 297, 'F')

        # Top gradient accent bar
        for i in range(6):
            alpha = 255 - (i * 30)
            self.set_fill_color(min(255, 90 + i * 7), min(255, 50 + i * 5), min(255, 220 + i * 8))
            self.rect(0, i * 0.8, 210, 0.8, 'F')

        # Bottom accent bar
        for i in range(3):
            self.set_fill_color(min(255, 90 + i * 10), min(255, 50 + i * 8), min(255, 220 + i * 10))
            self.rect(0, 293 + i * 1.3, 210, 1.3, 'F')

        # Subtle side accents
        self.set_fill_color(124, 77, 255)
        self.rect(0, 5, 2, 287, 'F')
        self.rect(208, 5, 2, 287, 'F')

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(80, 80, 100)
        self.cell(0, 5, f"AI Content Intelligence System v4.0  |  Certificate ID: CIS-{datetime.now().strftime('%Y%m%d%H%M%S')}", 0, 1, "C")
        self.cell(0, 5, f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}  |  This certificate is auto-generated", 0, 0, "C")


def _draw_score_bar(pdf, x, y, width, score, label, height=8):
    """Draw a visual score bar with label."""
    color = _score_color(score)

    # Label
    pdf.set_xy(x, y - 5)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(140, 140, 160)
    pdf.cell(width, 5, label, 0, 0, "L")

    # Score value on right
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*color)
    pdf.cell(0, 5, f"{score}/100", 0, 0, "R")

    # Background bar
    pdf.set_fill_color(30, 32, 45)
    pdf.rect(x, y, width, height, 'F')

    # Filled bar
    fill_width = max(1, (score / 100) * width)
    pdf.set_fill_color(*color)
    pdf.rect(x, y, fill_width, height, 'F')

    # Rounded caps (using small circles at ends)
    r = height / 2
    pdf.set_fill_color(30, 32, 45)


def _draw_metric_row(pdf, label, value, y=None, value_color=(220, 220, 240)):
    """Draw a clean metric row with dot leader."""
    if y:
        pdf.set_y(y)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(140, 140, 160)

    # Calculate label width
    label_width = pdf.get_string_width(label) + 2

    pdf.cell(label_width, 6, label, 0, 0, "L")

    # Dot leader
    dots_width = 100 - label_width
    if dots_width > 5:
        pdf.set_text_color(50, 50, 70)
        dot_text = "." * int(dots_width / 1.5)
        pdf.cell(dots_width, 6, dot_text, 0, 0, "L")

    # Value
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*value_color)
    pdf.cell(0, 6, str(value), 0, 1, "R")


def _draw_section_header(pdf, title, y=None):
    """Draw elegant section header."""
    if y:
        pdf.set_y(y)

    current_y = pdf.get_y()

    # Section line
    pdf.set_draw_color(124, 77, 255)
    pdf.set_line_width(0.5)
    pdf.line(15, current_y, 195, current_y)

    pdf.ln(3)

    # Section title
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(124, 77, 255)
    pdf.cell(0, 7, title.upper(), 0, 1, "L")
    pdf.ln(2)


def generate_certificate(data):
    """
    Generate a premium Content Readiness Certificate PDF.

    data: dict with keys:
        - title: content title
        - scores: {overall, readability, engagement, clarity, seo}
        - word_count: int
        - tone: str
        - readability_label: str
        - plagiarism_risk: str
        - ai_detection: str (optional)
        - seo_intent: str (optional)
        - conversion_score: float (optional)
    """
    if not HAS_FPDF:
        return None

    try:
        pdf = CertificatePDF()
        pdf.set_auto_page_break(auto=True, margin=25)
        pdf.add_page()

        scores = data.get("scores", {})
        overall = scores.get("overall", 0)
        if isinstance(overall, float):
            overall = round(overall, 1)
        color = _score_color(overall)
        grade_label, grade_letter = _grade_label(overall)

        # ═══ TITLE SECTION ═══
        pdf.set_y(12)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(124, 77, 255)
        pdf.cell(0, 5, "AI CONTENT INTELLIGENCE SYSTEM", 0, 1, "C")

        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(230, 230, 245)
        pdf.cell(0, 12, "Content Readiness Certificate", 0, 1, "C")

        # Decorative line under title
        pdf.set_draw_color(124, 77, 255)
        pdf.set_line_width(0.8)
        line_y = pdf.get_y() + 1
        pdf.line(60, line_y, 150, line_y)
        pdf.ln(5)

        # Date
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(120, 120, 140)
        pdf.cell(0, 5, f"Issued {datetime.now().strftime('%B %d, %Y')}", 0, 1, "C")
        pdf.ln(4)

        # ═══ CONTENT TITLE BOX ═══
        box_y = pdf.get_y()
        pdf.set_fill_color(25, 27, 38)
        pdf.rect(15, box_y, 180, 14, 'F')
        # Left accent
        pdf.set_fill_color(124, 77, 255)
        pdf.rect(15, box_y, 3, 14, 'F')

        pdf.set_xy(22, box_y + 2)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(100, 100, 120)
        pdf.cell(0, 4, "CONTENT ANALYZED", 0, 1, "L")
        pdf.set_x(22)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(220, 220, 240)
        title_text = str(data.get("title", "Untitled Content"))[:80]
        pdf.cell(0, 6, title_text, 0, 1, "L")
        pdf.ln(4)

        # ═══ OVERALL SCORE SECTION ═══
        score_box_y = pdf.get_y()
        pdf.set_fill_color(25, 27, 38)
        pdf.rect(15, score_box_y, 180, 36, 'F')

        # Score number
        pdf.set_xy(25, score_box_y + 3)
        pdf.set_font("Helvetica", "B", 32)
        pdf.set_text_color(*color)
        pdf.cell(50, 15, f"{overall}", 0, 0, "L")

        pdf.set_font("Helvetica", "", 14)
        pdf.set_text_color(100, 100, 120)
        pdf.cell(15, 15, "/100", 0, 0, "L")

        # Grade badge
        pdf.set_xy(100, score_box_y + 5)
        pdf.set_fill_color(*color)
        pdf.rect(100, score_box_y + 6, 85, 10, 'F')
        pdf.set_xy(100, score_box_y + 6)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(85, 10, f"GRADE: {grade_letter}  -  {grade_label}", 0, 0, "C")

        # Overall Score label
        pdf.set_xy(25, score_box_y + 20)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(100, 100, 120)
        pdf.cell(60, 5, "OVERALL QUALITY SCORE", 0, 0, "L")

        # Word count + Tone
        pdf.set_xy(100, score_box_y + 20)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(140, 140, 160)
        wc = data.get("word_count", 0)
        tone = data.get("tone", "N/A")
        pdf.cell(85, 5, f"{wc} words  |  Tone: {tone}", 0, 0, "C")

        # Verdict bar
        pdf.set_y(score_box_y + 28)
        if overall >= 70:
            vcolor = (0, 200, 100)
            vlabel = "CERTIFIED: Content meets quality standards"
        elif overall >= 50:
            vcolor = (255, 167, 38)
            vlabel = "CONDITIONAL: Minor improvements recommended"
        else:
            vcolor = (239, 83, 80)
            vlabel = "NOT READY: Significant revision required"

        pdf.set_fill_color(*vcolor)
        pdf.rect(15, score_box_y + 28, 180, 7, 'F')
        pdf.set_xy(15, score_box_y + 28)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(180, 7, vlabel, 0, 1, "C")
        pdf.ln(5)

        # ═══ QUALITY SCORES (Visual Bars) ═══
        _draw_section_header(pdf, "Quality Breakdown")

        bar_x = 15
        bar_width = 180
        bar_y = pdf.get_y()

        score_items = [
            ("Readability", scores.get("readability", 0)),
            ("Engagement", scores.get("engagement", 0)),
            ("Clarity", scores.get("clarity", 0)),
            ("SEO Optimization", scores.get("seo", 0)),
        ]

        for label, sc in score_items:
            sc_val = round(sc) if isinstance(sc, float) else sc
            _draw_score_bar(pdf, bar_x, pdf.get_y(), bar_width, sc_val, label, height=6)
            pdf.ln(12)

        # ═══ CONTENT ANALYSIS ═══
        _draw_section_header(pdf, "Content Analysis")

        rl = data.get("readability_label", "N/A")
        _draw_metric_row(pdf, "Reading Level", rl)
        _draw_metric_row(pdf, "Word Count", f"{data.get('word_count', 0):,}")
        _draw_metric_row(pdf, "Detected Tone", data.get("tone", "N/A"))

        if data.get("seo_intent") and data["seo_intent"] != "N/A":
            _draw_metric_row(pdf, "Search Intent", data["seo_intent"])

        pdf.ln(2)

        # ═══ AUTHENTICITY ═══
        _draw_section_header(pdf, "Authenticity & Compliance")

        plag_risk = str(data.get("plagiarism_risk", "N/A"))
        if "Low" in plag_risk:
            pc = (0, 200, 100)
        elif "Medium" in plag_risk:
            pc = (255, 167, 38)
        elif "Not checked" in plag_risk:
            pc = (140, 140, 160)
        else:
            pc = (239, 83, 80)
        _draw_metric_row(pdf, "Plagiarism Risk", plag_risk, value_color=pc)

        ai_label = str(data.get("ai_detection", "N/A"))
        if "Human" in ai_label or "Likely Human" in ai_label:
            ac = (0, 200, 100)
        elif "Mixed" in ai_label:
            ac = (255, 167, 38)
        elif "Not checked" in ai_label or "N/A" in ai_label:
            ac = (140, 140, 160)
        else:
            ac = (239, 83, 80)
        _draw_metric_row(pdf, "AI Content Detection", ai_label, value_color=ac)

        # Optional conversion score
        if data.get("conversion_score") is not None:
            pdf.ln(2)
            _draw_section_header(pdf, "Business Metrics")
            conv = data["conversion_score"]
            _draw_metric_row(pdf, "Conversion Probability", f"{conv}/100", value_color=_score_color(conv))

        # ═══ WATERMARK TEXT (subtle diagonal) ═══
        pdf.set_font("Helvetica", "B", 60)
        pdf.set_text_color(30, 32, 45)
        pdf.rotate(35, 105, 200)
        pdf.text(40, 220, "CERTIFIED")
        pdf.rotate(0)

        # Return as bytes
        pdf_bytes = pdf.output()
        return bytes(pdf_bytes)

    except Exception as e:
        # Fallback: return None if any generation error
        print(f"Certificate generation error: {e}")
        return None
