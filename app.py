"""
AI Content Intelligence System — Premium Streamlit Application
Production-grade content analysis, scoring, and rewriting platform.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_TITLE, APP_ICON, APP_VERSION, AUDIENCE_PRESETS
from utils.cleaner import clean_text, get_text_stats
from utils.readability import get_readability_report
from utils.tone import get_tone_report
from utils.scoring import compute_content_score, get_score_label
from utils.seo import get_seo_report
from utils.rewrite import rule_based_rewrite, ai_rewrite, thesis_helper
from utils.plagiarism import get_plagiarism_report
from utils.insights import generate_insights

# ─── Page Configuration ─────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Premium CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global ── */
*, html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Hide Streamlit branding ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Main container ── */
.main .block-container {
    padding: 1.5rem 2rem 2rem 2rem;
    max-width: 1400px;
}

/* ── Glassmorphism card ── */
.glass-card {
    background: rgba(26, 29, 41, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(124, 77, 255, 0.15);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
.glass-card:hover {
    border-color: rgba(124, 77, 255, 0.35);
    box-shadow: 0 12px 40px rgba(124, 77, 255, 0.1);
    transform: translateY(-2px);
}

/* ── Hero header ── */
.hero-header {
    background: linear-gradient(135deg, #1a1d29 0%, #0e1117 50%, #1a1035 100%);
    border: 1px solid rgba(124, 77, 255, 0.2);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(124, 77, 255, 0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-header::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: -10%;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(0, 230, 118, 0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7C4DFF, #B388FF, #00E676);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.3rem 0;
    position: relative;
    z-index: 1;
}
.hero-subtitle {
    font-size: 1rem;
    color: #9E9E9E;
    font-weight: 400;
    position: relative;
    z-index: 1;
}

/* ── Metric cards ── */
.metric-card {
    background: linear-gradient(135deg, rgba(26, 29, 41, 0.8), rgba(14, 17, 23, 0.9));
    border: 1px solid rgba(124, 77, 255, 0.12);
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
    transition: all 0.3s ease;
}
.metric-card:hover {
    border-color: rgba(124, 77, 255, 0.3);
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(124, 77, 255, 0.08);
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0;
    line-height: 1.2;
}
.metric-label {
    font-size: 0.8rem;
    color: #9E9E9E;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.3rem;
}

/* ── Score gauge colors ── */
.score-excellent { color: #00E676; }
.score-good { color: #66BB6A; }
.score-average { color: #FFA726; }
.score-below { color: #EF5350; }
.score-poor { color: #B71C1C; }

/* ── Insight cards ── */
.insight-strength {
    background: rgba(0, 230, 118, 0.08);
    border-left: 3px solid #00E676;
    padding: 0.8rem 1rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}
.insight-weakness {
    background: rgba(239, 83, 80, 0.08);
    border-left: 3px solid #EF5350;
    padding: 0.8rem 1rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}
.insight-tip {
    background: rgba(255, 167, 38, 0.08);
    border-left: 3px solid #FFA726;
    padding: 0.8rem 1rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}

/* ── Tabs styling ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(26, 29, 41, 0.5);
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7C4DFF, #651FFF) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7C4DFF, #651FFF);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.8rem;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(124, 77, 255, 0.3);
}
.stButton > button:hover {
    box-shadow: 0 6px 25px rgba(124, 77, 255, 0.5);
    transform: translateY(-2px);
}

/* ── Text area ── */
.stTextArea textarea {
    background: rgba(26, 29, 41, 0.8) !important;
    border: 1px solid rgba(124, 77, 255, 0.2) !important;
    border-radius: 12px !important;
    color: #E0E0E0 !important;
    font-size: 0.95rem !important;
}
.stTextArea textarea:focus {
    border-color: #7C4DFF !important;
    box-shadow: 0 0 0 2px rgba(124, 77, 255, 0.15) !important;
}

/* ── File uploader ── */
.stFileUploader {
    border: 2px dashed rgba(124, 77, 255, 0.25) !important;
    border-radius: 12px !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0E1117 0%, #1A1D29 100%);
    border-right: 1px solid rgba(124, 77, 255, 0.1);
}

/* ── Comparison layout ── */
.comparison-card {
    background: rgba(26, 29, 41, 0.6);
    border: 1px solid rgba(124, 77, 255, 0.1);
    border-radius: 12px;
    padding: 1.2rem;
}
.comparison-header {
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.8rem;
}
.original-header { color: #EF5350; }
.improved-header { color: #00E676; }

/* ── Badge ── */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.badge-green { background: rgba(0, 230, 118, 0.15); color: #00E676; }
.badge-yellow { background: rgba(255, 167, 38, 0.15); color: #FFA726; }
.badge-red { background: rgba(239, 83, 80, 0.15); color: #EF5350; }
.badge-purple { background: rgba(124, 77, 255, 0.15); color: #B388FF; }

/* ── Divider ── */
.custom-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(124, 77, 255, 0.3), transparent);
    margin: 1.5rem 0;
}

/* ── Animation keyframes ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.animate-in {
    animation: fadeInUp 0.5s ease forwards;
}
</style>
""", unsafe_allow_html=True)


# ─── Helper Functions ────────────────────────────────────────────

def create_gauge_chart(value, title, max_val=100):
    """Create a premium animated gauge chart."""
    if value >= 70:
        color = "#00E676"
    elif value >= 50:
        color = "#FFA726"
    else:
        color = "#EF5350"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 14, "color": "#9E9E9E"}},
        number={"font": {"size": 42, "color": color, "family": "Inter"}, "suffix": ""},
        gauge={
            "axis": {"range": [0, max_val], "tickwidth": 0, "tickcolor": "rgba(0,0,0,0)", "dtick": 25},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(26,29,41,0.5)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(239,83,80,0.08)"},
                {"range": [40, 70], "color": "rgba(255,167,38,0.08)"},
                {"range": [70, 100], "color": "rgba(0,230,118,0.08)"},
            ],
            "threshold": {
                "line": {"color": "#B388FF", "width": 2},
                "thickness": 0.8,
                "value": value,
            },
        },
    ))
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter"},
    )
    return fig


def create_radar_chart(scores):
    """Create a premium radar chart for content scores."""
    categories = ["Readability", "Engagement", "Clarity", "SEO"]
    values = [
        scores["readability"],
        scores["engagement"],
        scores["clarity"],
        scores["seo"],
    ]
    values.append(values[0])  # close the polygon
    categories.append(categories[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor="rgba(124, 77, 255, 0.15)",
        line=dict(color="#7C4DFF", width=2),
        marker=dict(size=8, color="#B388FF"),
        name="Scores",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor="rgba(124,77,255,0.1)",
                linecolor="rgba(124,77,255,0.1)",
                tickfont=dict(size=10, color="#666"),
            ),
            angularaxis=dict(
                gridcolor="rgba(124,77,255,0.1)",
                linecolor="rgba(124,77,255,0.1)",
                tickfont=dict(size=12, color="#B388FF", family="Inter"),
            ),
        ),
        showlegend=False,
        height=320,
        margin=dict(l=60, r=60, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_sentiment_bar(sentence_data):
    """Create sentiment breakdown bar chart."""
    if not sentence_data:
        return None

    labels = [f"S{i+1}" for i in range(len(sentence_data))]
    polarities = [s["polarity"] for s in sentence_data]
    colors = ["#00E676" if p > 0.1 else "#EF5350" if p < -0.1 else "#FFA726" for p in polarities]

    fig = go.Figure(go.Bar(
        x=labels,
        y=polarities,
        marker_color=colors,
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Polarity: %{y:.3f}<extra></extra>",
    ))
    fig.update_layout(
        height=200,
        margin=dict(l=40, r=20, t=10, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(124,77,255,0.05)", tickfont=dict(size=10, color="#666")),
        yaxis=dict(
            gridcolor="rgba(124,77,255,0.08)",
            tickfont=dict(size=10, color="#666"),
            title="Polarity",
            titlefont=dict(size=11, color="#9E9E9E"),
            zeroline=True,
            zerolinecolor="rgba(124,77,255,0.2)",
        ),
    )
    return fig


def create_keyword_chart(keywords):
    """Create keyword density bar chart."""
    if not keywords:
        return None

    kw_data = keywords[:10]
    words = [k["keyword"] for k in kw_data]
    densities = [k["density"] for k in kw_data]

    fig = go.Figure(go.Bar(
        x=densities,
        y=words,
        orientation="h",
        marker=dict(
            color=densities,
            colorscale=[[0, "#7C4DFF"], [0.5, "#B388FF"], [1, "#00E676"]],
            line_width=0,
        ),
        hovertemplate="<b>%{y}</b><br>Density: %{x:.2f}%<extra></extra>",
    ))
    fig.update_layout(
        height=max(200, len(kw_data) * 35),
        margin=dict(l=10, r=20, t=10, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            gridcolor="rgba(124,77,255,0.08)",
            tickfont=dict(size=10, color="#666"),
            title="Density %",
            titlefont=dict(size=11, color="#9E9E9E"),
        ),
        yaxis=dict(
            tickfont=dict(size=11, color="#B388FF"),
            autorange="reversed",
        ),
    )
    return fig


# ─── Sidebar ─────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <span style="font-size: 2.5rem;">🧠</span>
        <h2 style="background: linear-gradient(135deg, #7C4DFF, #B388FF);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-weight: 800; margin: 0.5rem 0 0.2rem 0;">
            Content AI
        </h2>
        <p style="color: #666; font-size: 0.8rem;">v{version}</p>
    </div>
    """.format(version=APP_VERSION), unsafe_allow_html=True)

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # OpenAI API Key
    st.markdown("#### ⚙️ Settings")
    api_key = st.text_input(
        "OpenAI API Key (optional)",
        type="password",
        help="Provide your API key for AI-powered rewriting. Leave empty for rule-based mode.",
        placeholder="sk-...",
    )

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Sample text
    st.markdown("#### 📝 Quick Demo")
    sample_texts = {
        "Select a sample...": "",
        "📰 News Article": (
            "The rapid advancement of artificial intelligence has transformed "
            "industries across the globe. From healthcare to finance, AI-powered "
            "systems are now capable of analyzing vast amounts of data and making "
            "decisions that were once the exclusive domain of human experts. "
            "However, this technological revolution has also raised important "
            "questions about ethics, employment, and the future of human creativity.\n\n"
            "Recent studies show that companies implementing AI solutions report "
            "an average productivity increase of 40 percent. Despite these gains, "
            "experts warn that the transition must be managed carefully to avoid "
            "displacing workers without providing adequate retraining opportunities.\n\n"
            "What does the future hold? Many researchers believe that the key lies "
            "not in replacing human workers, but in augmenting their capabilities. "
            "By combining human creativity with machine efficiency, organizations "
            "can achieve outcomes that neither could accomplish alone."
        ),
        "🎓 Academic Abstract": (
            "This study investigates the impact of social media usage on academic "
            "performance among university students. A cross-sectional survey was "
            "conducted with 500 participants from three major universities. The "
            "results indicate a statistically significant negative correlation "
            "between daily social media consumption exceeding four hours and "
            "grade point average. Furthermore, the analysis reveals that "
            "platforms with predominantly visual content exhibit a stronger "
            "negative association compared to text-based platforms. These findings "
            "suggest that educational institutions should develop targeted "
            "digital literacy programs to help students manage their online habits "
            "effectively while maintaining academic excellence."
        ),
        "💼 Business Email": (
            "Dear Team,\n\n"
            "I wanted to share some exciting news regarding our Q3 performance. "
            "We have exceeded our revenue targets by 15%, driven primarily by "
            "the successful launch of our new product line. This achievement "
            "reflects the hard work and dedication of every team member.\n\n"
            "Moving forward, I'd like to outline our priorities for Q4:\n"
            "1. Expand into two new market segments\n"
            "2. Improve customer retention by 10%\n"
            "3. Launch the updated mobile application\n\n"
            "Please review the attached report for detailed figures. I look "
            "forward to discussing our strategy in next week's all-hands meeting.\n\n"
            "Best regards"
        ),
    }
    selected_sample = st.selectbox("Load sample text", options=list(sample_texts.keys()))

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Insights panel placeholder
    st.markdown("#### 🔮 Smart Insights")
    insights_placeholder = st.empty()


# ─── Hero Header ─────────────────────────────────────────────────

st.markdown("""
<div class="hero-header">
    <h1 class="hero-title">🧠 AI Content Intelligence System</h1>
    <p class="hero-subtitle">
        Evaluate, improve, and optimize your content with advanced NLP — built for writers, students, and businesses.
    </p>
</div>
""", unsafe_allow_html=True)


# ─── Input Section ───────────────────────────────────────────────

col_input, col_upload = st.columns([3, 1])

with col_input:
    default_text = sample_texts.get(selected_sample, "")
    user_text = st.text_area(
        "✍️ Paste your content here",
        value=default_text,
        height=200,
        placeholder="Enter or paste your text for analysis... (articles, essays, blog posts, CV content, etc.)",
        key="main_text_input",
    )

with col_upload:
    st.markdown("#### 📎 Upload Document")
    uploaded_file = st.file_uploader(
        "Upload file",
        type=["pdf", "docx", "txt", "md"],
        help="Supported: PDF, DOCX, TXT, MD",
        label_visibility="collapsed",
    )

    if uploaded_file:
        try:
            from utils.extractor import extract_text
            extracted = extract_text(uploaded_file)
            if extracted and not extracted.startswith("[Error"):
                user_text = extracted
                st.success(f"✅ Extracted from {uploaded_file.name}")
            else:
                st.error(f"❌ {extracted}")
        except Exception as e:
            st.error(f"❌ Extraction error: {e}")

    # Title input for SEO analysis
    content_title = st.text_input(
        "📌 Content Title (for SEO)",
        placeholder="Your headline...",
    )


# ─── Analysis Trigger ───────────────────────────────────────────

analyze_col1, analyze_col2, analyze_col3 = st.columns([1, 1, 2])
with analyze_col1:
    analyze_btn = st.button("🚀 Analyze Content", use_container_width=True, type="primary")

if not user_text or not user_text.strip():
    if not analyze_btn:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <p style="font-size: 3rem; margin-bottom: 1rem;">✨</p>
            <h3 style="color: #B388FF; margin-bottom: 0.5rem;">Ready to Analyze</h3>
            <p style="color: #666;">Paste your content or upload a document to get started.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

if not analyze_btn and "analysis_results" not in st.session_state:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 3rem;">
        <p style="font-size: 3rem; margin-bottom: 1rem;">✨</p>
        <h3 style="color: #B388FF; margin-bottom: 0.5rem;">Content Ready</h3>
        <p style="color: #666;">Click <b>🚀 Analyze Content</b> to begin.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─── Run Analysis ───────────────────────────────────────────────

with st.spinner("🧠 Analyzing your content with NLP engines..."):
    cleaned = clean_text(user_text)

    if len(cleaned) < 30:
        st.warning("⚠️ Content is too short for meaningful analysis. Please provide more text.")
        st.stop()

    text_stats = get_text_stats(cleaned)
    readability_report = get_readability_report(cleaned)
    tone_report = get_tone_report(cleaned)
    scores = compute_content_score(cleaned)
    seo_report = get_seo_report(cleaned, title=content_title)
    score_label = get_score_label(scores["overall"])

    # Generate insights
    insights = generate_insights(scores, readability_report, tone_report, seo_report, text_stats)

    # Store in session
    st.session_state["analysis_results"] = {
        "text": cleaned,
        "stats": text_stats,
        "readability": readability_report,
        "tone": tone_report,
        "scores": scores,
        "seo": seo_report,
        "score_label": score_label,
        "insights": insights,
    }


# ─── Results ─────────────────────────────────────────────────────

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ─── Quick Stats Bar ────────────────────────────────────────────
qs1, qs2, qs3, qs4, qs5 = st.columns(5)

def score_class(val):
    if val >= 85: return "score-excellent"
    if val >= 70: return "score-good"
    if val >= 55: return "score-average"
    if val >= 40: return "score-below"
    return "score-poor"

with qs1:
    sc = score_class(scores["overall"])
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value {sc}">{scores['overall']}</p>
        <p class="metric-label">Overall Score</p>
    </div>
    """, unsafe_allow_html=True)

with qs2:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value" style="color: #B388FF;">{text_stats['words']}</p>
        <p class="metric-label">Words</p>
    </div>
    """, unsafe_allow_html=True)

with qs3:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value" style="color: #B388FF;">{text_stats['sentences']}</p>
        <p class="metric-label">Sentences</p>
    </div>
    """, unsafe_allow_html=True)

with qs4:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value" style="color: {readability_report['interpretation']['color']};">{readability_report['flesch_reading_ease']}</p>
        <p class="metric-label">Readability</p>
    </div>
    """, unsafe_allow_html=True)

with qs5:
    tone_color = tone_report["tone"]["color"]
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value" style="font-size: 1.5rem; color: {tone_color};">{tone_report['tone']['emoji']} {tone_report['tone']['tone']}</p>
        <p class="metric-label">Tone</p>
    </div>
    """, unsafe_allow_html=True)


# ─── Sidebar Insights ───────────────────────────────────────────
with insights_placeholder.container():
    if insights["strengths"]:
        for s in insights["strengths"][:3]:
            st.markdown(f'<div class="insight-strength">{s["icon"]} {s["text"]}</div>', unsafe_allow_html=True)

    if insights["weaknesses"]:
        for w in insights["weaknesses"][:3]:
            st.markdown(f'<div class="insight-weakness">{w["icon"]} {w["text"]}</div>', unsafe_allow_html=True)

    if insights["tips"]:
        for t in insights["tips"][:4]:
            st.markdown(f'<div class="insight-tip">{t["icon"]} {t["text"]}</div>', unsafe_allow_html=True)


# ─── Main Tabs ───────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Analysis Dashboard",
    "🔍 SEO Analysis",
    "🧠 AI Rewrite Engine",
    "🚨 Plagiarism Check",
    "🎓 Thesis Helper",
])


# ═══════════════════════════════════════════════════════════════════
# TAB 1: Analysis Dashboard
# ═══════════════════════════════════════════════════════════════════

with tab1:
    # Score gauge + Radar
    col_gauge, col_radar = st.columns([1, 1])

    with col_gauge:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h4 style="color: #B388FF; margin-bottom: 0;">Content Quality Score</h4>
            <span class="badge badge-{'green' if scores['overall'] >= 70 else 'yellow' if scores['overall'] >= 50 else 'red'}">
                {score_label['emoji']} {score_label['label']}
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(create_gauge_chart(scores["overall"], ""), use_container_width=True)

    with col_radar:
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: #B388FF; margin-bottom: 0;">Score Breakdown</h4>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(create_radar_chart(scores), use_container_width=True)

    # Readability section
    st.markdown("### 📖 Readability Analysis")
    r1, r2, r3, r4 = st.columns(4)
    interp = readability_report["interpretation"]

    with r1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value" style="color: {interp['color']};">{readability_report['flesch_reading_ease']}</p>
            <p class="metric-label">Flesch Reading Ease</p>
            <p style="color: {interp['color']}; font-size: 0.8rem; margin:0;">{interp['label']}</p>
        </div>
        """, unsafe_allow_html=True)
    with r2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value" style="color: #B388FF;">{readability_report['flesch_kincaid_grade']}</p>
            <p class="metric-label">Grade Level</p>
        </div>
        """, unsafe_allow_html=True)
    with r3:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value" style="color: #B388FF;">{readability_report['gunning_fog']}</p>
            <p class="metric-label">Gunning Fog</p>
        </div>
        """, unsafe_allow_html=True)
    with r4:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value" style="color: #B388FF;">{readability_report['smog_index']}</p>
            <p class="metric-label">SMOG Index</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card">
        <p>{interp['icon']} <b>Reading Level:</b> {interp['label']} — {interp['description']}</p>
        <p>📚 <b>Target Audience:</b> {interp['audience']}</p>
        <p>📋 <b>Consensus Grade:</b> {readability_report['consensus_grade']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Tone & Sentiment section
    st.markdown("### 🎭 Tone & Sentiment")
    t1, t2, t3 = st.columns(3)

    tone_data = tone_report["tone"]
    subj_data = tone_report["subjectivity"]
    form_data = tone_report["formality"]

    with t1:
        st.markdown(f"""
        <div class="metric-card">
            <p style="font-size: 2rem; margin: 0;">{tone_data['emoji']}</p>
            <p class="metric-value" style="font-size: 1.3rem; color: {tone_data['color']};">{tone_data['tone']}</p>
            <p class="metric-label">Sentiment</p>
            <p style="font-size: 0.8rem; color: #666; margin: 0;">Polarity: {tone_report['overall_polarity']}</p>
        </div>
        """, unsafe_allow_html=True)
    with t2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value" style="font-size: 1.3rem; color: {subj_data['color']};">{subj_data['level']}</p>
            <p class="metric-label">Objectivity</p>
            <p style="font-size: 0.8rem; color: #666; margin: 0;">{subj_data['description']}</p>
        </div>
        """, unsafe_allow_html=True)
    with t3:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value" style="font-size: 1.3rem; color: {form_data['color']};">{form_data['level']}</p>
            <p class="metric-label">Formality</p>
            <p style="font-size: 0.8rem; color: #666; margin: 0;">Score: {form_data['score']}/100</p>
        </div>
        """, unsafe_allow_html=True)

    # Sentence-level sentiment
    sent_data = tone_report.get("sentence_breakdown", [])
    if sent_data:
        st.markdown("#### Sentence-Level Sentiment")
        fig_sent = create_sentiment_bar(sent_data)
        if fig_sent:
            st.plotly_chart(fig_sent, use_container_width=True)

    # Text statistics
    st.markdown("### 📐 Text Statistics")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("Characters", f"{text_stats['characters']:,}")
    with s2:
        st.metric("Avg Word Length", f"{text_stats['avg_word_length']} chars")
    with s3:
        st.metric("Avg Sentence Length", f"{text_stats['avg_sentence_length']} words")
    with s4:
        st.metric("Reading Time", f"{text_stats['reading_time_min']} min")


# ═══════════════════════════════════════════════════════════════════
# TAB 2: SEO Analysis
# ═══════════════════════════════════════════════════════════════════

with tab2:
    # Headline analysis
    if content_title:
        st.markdown("### 📰 Headline Analysis")
        headline = seo_report.get("headline_analysis", {})
        if headline:
            hcol1, hcol2, hcol3 = st.columns(3)
            with hcol1:
                h_sc = headline.get("score", 0)
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-value {score_class(h_sc)}">{h_sc}</p>
                    <p class="metric-label">Headline Score</p>
                </div>
                """, unsafe_allow_html=True)
            with hcol2:
                st.metric("Word Count", headline.get("word_count", 0))
            with hcol3:
                st.metric("Character Count", headline.get("char_count", 0))

            for suggestion in headline.get("suggestions", []):
                st.info(f"💡 {suggestion}")

    st.markdown("### 🔑 Top Keywords")
    kw_col, stats_col = st.columns([2, 1])

    with kw_col:
        fig_kw = create_keyword_chart(seo_report.get("keywords", []))
        if fig_kw:
            st.plotly_chart(fig_kw, use_container_width=True)
        else:
            st.info("No significant keywords found.")

    with stats_col:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color: #B388FF;">📊 SEO Stats</h4>
            <p>📝 <b>Total Words:</b> {seo_report.get('total_words', 0)}</p>
            <p>🔤 <b>Unique Words:</b> {seo_report.get('unique_words', 0)}</p>
            <p>📚 <b>Vocabulary Richness:</b> {seo_report.get('vocabulary_richness', 0)}%</p>
        </div>
        """, unsafe_allow_html=True)

    # Bigrams
    bigrams = seo_report.get("bigrams", [])
    if bigrams:
        st.markdown("### 🔗 Top Phrases (Bigrams)")
        bigram_cols = st.columns(min(5, len(bigrams)))
        for idx, bg in enumerate(bigrams[:5]):
            with bigram_cols[idx]:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-value" style="font-size: 1rem; color: #B388FF;">{bg['phrase']}</p>
                    <p class="metric-label">{bg['count']}× used</p>
                </div>
                """, unsafe_allow_html=True)

    # Keyword density table
    keywords = seo_report.get("keywords", [])
    if keywords:
        st.markdown("### 📋 Keyword Density Table")
        import pandas as pd
        df = pd.DataFrame(keywords)
        df.columns = ["Keyword", "Count", "Density (%)"]
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Density (%)": st.column_config.ProgressColumn(
                    min_value=0,
                    max_value=max(df["Density (%)"].max() * 1.5, 5),
                    format="%.2f%%",
                ),
            },
        )


# ═══════════════════════════════════════════════════════════════════
# TAB 3: AI Rewrite Engine
# ═══════════════════════════════════════════════════════════════════

with tab3:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: #B388FF; margin: 0;">🧠 AI Content Improvement Engine</h3>
        <p style="color: #9E9E9E; margin: 0.5rem 0 0 0;">
            Enhance your content with rule-based optimization or AI-powered rewriting.
        </p>
    </div>
    """, unsafe_allow_html=True)

    rw_col1, rw_col2 = st.columns(2)

    with rw_col1:
        rewrite_mode = st.radio(
            "Rewrite Mode",
            options=["⚡ Rule-Based (Free)", "🤖 AI-Powered (API Key)"],
            horizontal=True,
        )

    with rw_col2:
        audience = st.selectbox(
            "Target Audience",
            options=list(AUDIENCE_PRESETS.keys()),
            format_func=lambda x: AUDIENCE_PRESETS[x]["label"],
        )
        st.caption(AUDIENCE_PRESETS[audience]["description"])

    if st.button("✨ Improve Content", use_container_width=True, type="primary", key="rewrite_btn"):
        if "Rule-Based" in rewrite_mode:
            with st.spinner("⚡ Applying rule-based improvements..."):
                result = rule_based_rewrite(cleaned)

            # Changes summary
            st.markdown("### 📋 Changes Applied")
            for change in result["changes"]:
                st.markdown(f"- {change}")

            # Side-by-side comparison
            st.markdown("### 📝 Comparison")
            cmp1, cmp2 = st.columns(2)
            with cmp1:
                st.markdown('<p class="comparison-header original-header">❌ ORIGINAL</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="comparison-card">{cleaned[:1000]}</div>', unsafe_allow_html=True)
            with cmp2:
                st.markdown('<p class="comparison-header improved-header">✅ IMPROVED</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="comparison-card">{result["improved_text"][:1000]}</div>', unsafe_allow_html=True)

            # Passive voice suggestions
            if result.get("passive_suggestions"):
                st.markdown("### ⚠️ Passive Voice Instances")
                for ps in result["passive_suggestions"][:5]:
                    st.warning(f"**\"{ps['text']}\"** — {ps['suggestion']}")

        else:
            # AI-Powered rewrite
            if not api_key:
                st.warning("⚠️ Please enter your OpenAI API key in the sidebar to use AI-powered rewriting.")
            else:
                with st.spinner("🤖 AI is rewriting your content..."):
                    result = ai_rewrite(cleaned, api_key, audience=audience)

                if result["success"]:
                    st.markdown("### 📝 AI-Improved Version")
                    st.markdown(f'<span class="badge badge-purple">{result["audience"]}</span>', unsafe_allow_html=True)

                    cmp1, cmp2 = st.columns(2)
                    with cmp1:
                        st.markdown('<p class="comparison-header original-header">❌ ORIGINAL</p>', unsafe_allow_html=True)
                        st.markdown(f'<div class="comparison-card">{cleaned[:1500]}</div>', unsafe_allow_html=True)
                    with cmp2:
                        st.markdown('<p class="comparison-header improved-header">✅ AI IMPROVED</p>', unsafe_allow_html=True)
                        st.markdown(f'<div class="comparison-card">{result["improved_text"][:1500]}</div>', unsafe_allow_html=True)
                else:
                    st.error(f"❌ Error: {result['error']}")


# ═══════════════════════════════════════════════════════════════════
# TAB 4: Plagiarism Check
# ═══════════════════════════════════════════════════════════════════

with tab4:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: #B388FF; margin: 0;">🚨 Plagiarism Risk Indicator</h3>
        <p style="color: #9E9E9E; margin: 0.5rem 0 0 0;">
            Analyze internal content repetition and cross-document similarity.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Reference text for cross-document check
    ref_text = st.text_area(
        "📄 Reference text for comparison (optional)",
        height=120,
        placeholder="Paste reference text to compare against...",
    )

    if st.button("🔍 Check Plagiarism Risk", use_container_width=True, key="plag_btn"):
        with st.spinner("🔍 Analyzing content similarity..."):
            plag_report = get_plagiarism_report(cleaned, ref_text if ref_text else None)

        internal = plag_report["internal"]

        # Risk gauge
        p1, p2 = st.columns([1, 2])
        with p1:
            st.plotly_chart(
                create_gauge_chart(100 - internal["risk_score"], "Originality"),
                use_container_width=True,
            )
        with p2:
            risk_badge = "badge-green" if internal["risk_level"] == "Low" else "badge-yellow" if internal["risk_level"] == "Medium" else "badge-red"
            st.markdown(f"""
            <div class="glass-card">
                <h4>Risk Assessment</h4>
                <p><span class="badge {risk_badge}">{internal['risk_level']} Risk</span></p>
                <p>{internal['message']}</p>
                <p style="color: #666; font-size: 0.85rem;">
                    📝 Sentences analyzed: {internal['total_sentences']} |
                    🔄 Comparisons made: {internal['total_comparisons']}
                </p>
            </div>
            """, unsafe_allow_html=True)

        # Similar pairs
        if internal["similar_pairs"]:
            st.markdown("### ⚠️ Flagged Similar Sentences")
            for pair in internal["similar_pairs"][:5]:
                with st.expander(f"🔗 Similarity: {pair['similarity']}% — Sentences {pair['index_a']} & {pair['index_b']}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Sentence {pair['index_a']}:** {pair['sentence_a']}")
                    with c2:
                        st.markdown(f"**Sentence {pair['index_b']}:** {pair['sentence_b']}")

        # Cross-document results
        if "cross_document" in plag_report:
            st.markdown("### 📊 Cross-Document Comparison")
            cross = plag_report["cross_document"]
            st.markdown(f"""
            <div class="glass-card">
                <p style="font-size: 1.5rem; font-weight: 800; color: {cross['color']};">
                    {cross['similarity_score']}% Similarity
                </p>
                <p>Level: <span class="badge" style="background: {cross['color']}20; color: {cross['color']};">{cross['level']}</span></p>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 5: Thesis Helper
# ═══════════════════════════════════════════════════════════════════

with tab5:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: #B388FF; margin: 0;">🎓 Thesis Helper Mode</h3>
        <p style="color: #9E9E9E; margin: 0.5rem 0 0 0;">
            Get structure suggestions, abstract improvements, and academic writing tips.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🎓 Analyze for Academic Writing", use_container_width=True, key="thesis_btn"):
        with st.spinner("🎓 Analyzing academic structure..."):
            thesis_result = thesis_helper(cleaned, api_key if api_key else None)

        # Structure analysis
        st.markdown("### 📋 Structure Analysis")
        sections = thesis_result.get("found_sections", {})
        struct_cols = st.columns(4)
        for idx, (section, found) in enumerate(sections.items()):
            with struct_cols[idx]:
                emoji = "✅" if found else "❌"
                color = "#00E676" if found else "#EF5350"
                st.markdown(f"""
                <div class="metric-card">
                    <p style="font-size: 1.5rem; margin: 0;">{emoji}</p>
                    <p class="metric-label" style="color: {color};">{section.title()}</p>
                </div>
                """, unsafe_allow_html=True)

        # Suggestions
        st.markdown("### 💡 Suggestions")
        for suggestion in thesis_result.get("suggestions", []):
            st.markdown(f"""
            <div class="insight-tip">{suggestion}</div>
            """, unsafe_allow_html=True)

        # Stats
        st.markdown(f"""
        <div class="glass-card">
            <p>📝 <b>Word Count:</b> {thesis_result.get('word_count', 0)}</p>
            <p>📄 <b>Paragraphs:</b> {thesis_result.get('paragraph_count', 0)}</p>
        </div>
        """, unsafe_allow_html=True)

        # AI-improved version
        if thesis_result.get("ai_improved"):
            st.markdown("### 🤖 AI-Improved Academic Version")
            st.markdown(f"""
            <div class="comparison-card">{thesis_result['ai_improved'][:2000]}</div>
            """, unsafe_allow_html=True)


# ─── Footer ──────────────────────────────────────────────────────
st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; padding: 1rem; color: #666;">
    <p style="margin: 0;">🧠 <b>AI Content Intelligence System</b> v{APP_VERSION}</p>
    <p style="margin: 0; font-size: 0.8rem;">Powered by NLP • Built for Writers, Students & Businesses</p>
</div>
""", unsafe_allow_html=True)
