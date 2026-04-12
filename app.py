"""
AI Content Intelligence System — Premium Streamlit Application (V3 — Elite)
Production-grade AI-powered content analysis, scoring, and rewriting platform.
Features: embeddings, ML scoring, semantic coherence, search intent, grammar correction, diff view.
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
from utils.scoring import compute_content_score, get_score_label, get_domain_presets
from utils.seo import get_seo_report
from utils.rewrite import rule_based_rewrite, ai_rewrite, thesis_helper, grammar_check
from utils.plagiarism import get_plagiarism_report
from utils.insights import generate_insights

# V3: Embeddings (lazy-loaded, optional)
try:
    from utils.embeddings import get_semantic_report, is_available as embeddings_available
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    def embeddings_available(): return False
    def get_semantic_report(text): return {"available": False}

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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*, html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.main .block-container { padding: 1.5rem 2rem 2rem 2rem; max-width: 1400px; }

.glass-card {
    background: rgba(26, 29, 41, 0.7); backdrop-filter: blur(20px);
    border: 1px solid rgba(124, 77, 255, 0.15); border-radius: 16px;
    padding: 1.5rem; margin-bottom: 1rem; transition: all 0.3s ease;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
.glass-card:hover { border-color: rgba(124, 77, 255, 0.35); box-shadow: 0 12px 40px rgba(124, 77, 255, 0.1); transform: translateY(-2px); }

.hero-header {
    background: linear-gradient(135deg, #1a1d29 0%, #0e1117 50%, #1a1035 100%);
    border: 1px solid rgba(124, 77, 255, 0.2); border-radius: 20px;
    padding: 2rem 2.5rem; margin-bottom: 1.5rem; position: relative; overflow: hidden;
}
.hero-header::before { content: ''; position: absolute; top: -50%; right: -20%; width: 300px; height: 300px; background: radial-gradient(circle, rgba(124, 77, 255, 0.12) 0%, transparent 70%); border-radius: 50%; }
.hero-title { font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, #7C4DFF, #B388FF, #00E676); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0 0 0.3rem 0; position: relative; z-index: 1; }
.hero-subtitle { font-size: 1rem; color: #9E9E9E; font-weight: 400; position: relative; z-index: 1; }

.metric-card {
    background: linear-gradient(135deg, rgba(26, 29, 41, 0.8), rgba(14, 17, 23, 0.9));
    border: 1px solid rgba(124, 77, 255, 0.12); border-radius: 14px;
    padding: 1.2rem; text-align: center; transition: all 0.3s ease;
}
.metric-card:hover { border-color: rgba(124, 77, 255, 0.3); transform: translateY(-3px); box-shadow: 0 8px 25px rgba(124, 77, 255, 0.08); }
.metric-value { font-size: 2.2rem; font-weight: 800; margin: 0; line-height: 1.2; }
.metric-label { font-size: 0.8rem; color: #9E9E9E; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.3rem; }

.score-excellent { color: #00E676; } .score-good { color: #66BB6A; }
.score-average { color: #FFA726; } .score-below { color: #EF5350; } .score-poor { color: #B71C1C; }

.insight-strength { background: rgba(0, 230, 118, 0.08); border-left: 3px solid #00E676; padding: 0.8rem 1rem; border-radius: 0 8px 8px 0; margin-bottom: 0.5rem; font-size: 0.9rem; }
.insight-weakness { background: rgba(239, 83, 80, 0.08); border-left: 3px solid #EF5350; padding: 0.8rem 1rem; border-radius: 0 8px 8px 0; margin-bottom: 0.5rem; font-size: 0.9rem; }
.insight-tip { background: rgba(255, 167, 38, 0.08); border-left: 3px solid #FFA726; padding: 0.8rem 1rem; border-radius: 0 8px 8px 0; margin-bottom: 0.5rem; font-size: 0.9rem; }

.stTabs [data-baseweb="tab-list"] { gap: 8px; background: rgba(26, 29, 41, 0.5); border-radius: 12px; padding: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 20px; font-weight: 600; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #7C4DFF, #651FFF) !important; }

.stButton > button { background: linear-gradient(135deg, #7C4DFF, #651FFF); color: white; border: none; border-radius: 10px; padding: 0.6rem 1.8rem; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(124, 77, 255, 0.3); }
.stButton > button:hover { box-shadow: 0 6px 25px rgba(124, 77, 255, 0.5); transform: translateY(-2px); }

.stTextArea textarea { background: rgba(26, 29, 41, 0.8) !important; border: 1px solid rgba(124, 77, 255, 0.2) !important; border-radius: 12px !important; color: #E0E0E0 !important; }
.stTextArea textarea:focus { border-color: #7C4DFF !important; box-shadow: 0 0 0 2px rgba(124, 77, 255, 0.15) !important; }

section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0E1117 0%, #1A1D29 100%); border-right: 1px solid rgba(124, 77, 255, 0.1); }

.diff-added { background: rgba(0, 230, 118, 0.15); color: #00E676; padding: 2px 4px; border-radius: 4px; text-decoration: none; }
.diff-removed { background: rgba(239, 83, 80, 0.15); color: #EF5350; padding: 2px 4px; border-radius: 4px; text-decoration: line-through; }

.badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.badge-green { background: rgba(0, 230, 118, 0.15); color: #00E676; }
.badge-yellow { background: rgba(255, 167, 38, 0.15); color: #FFA726; }
.badge-red { background: rgba(239, 83, 80, 0.15); color: #EF5350; }
.badge-purple { background: rgba(124, 77, 255, 0.15); color: #B388FF; }

.custom-divider { border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(124, 77, 255, 0.3), transparent); margin: 1.5rem 0; }

.grammar-fix { background: rgba(124, 77, 255, 0.08); border: 1px solid rgba(124, 77, 255, 0.15); border-radius: 10px; padding: 0.8rem 1rem; margin-bottom: 0.5rem; }

/* Fix file uploader - completely fix the duplicate label */
[data-testid="stFileUploader"] { background: rgba(26, 29, 41, 0.6); border: 1px dashed rgba(124, 77, 255, 0.25); border-radius: 12px; padding: 0.8rem; }
[data-testid="stFileUploader"] > label,
[data-testid="stFileUploader"] > div > label,
[data-testid="stWidgetLabel"],
[data-testid="stFileUploader"] [data-testid="stWidgetLabel"] { display: none !important; height: 0 !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important; position: absolute !important; }
[data-testid="stFileUploaderDropzone"] { border: 1px dashed rgba(124, 77, 255, 0.3) !important; border-radius: 10px !important; background: rgba(14, 17, 23, 0.5) !important; }
[data-testid="stFileUploaderDropzone"] button { background: linear-gradient(135deg, #7C4DFF, #651FFF) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 0.4rem 1.2rem !important; }
[data-testid="stFileUploaderDropzone"] button span,
[data-testid="stFileUploaderDropzone"] button p { font-size: 0 !important; }
[data-testid="stFileUploaderDropzone"] button::after { content: 'Browse Files'; font-size: 0.875rem !important; }
[data-testid="stFileUploaderDropzone"] small { color: #9E9E9E !important; }

.coherence-bar { height: 6px; border-radius: 3px; margin: 0.3rem 0; }

@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)


# ─── Cached Analysis Functions ───────────────────────────────────

@st.cache_data(show_spinner=False)
def cached_text_stats(text):
    return get_text_stats(text)

@st.cache_data(show_spinner=False)
def cached_readability(text):
    return get_readability_report(text)

@st.cache_data(show_spinner=False)
def cached_tone(text):
    return get_tone_report(text)

@st.cache_data(show_spinner=False)
def cached_seo(text, title):
    return get_seo_report(text, title=title)

@st.cache_resource(show_spinner=False)
def cached_semantic(text):
    return get_semantic_report(text)


# ─── Helper Functions ────────────────────────────────────────────

def create_gauge_chart(value, title, max_val=100):
    color = "#00E676" if value >= 70 else "#FFA726" if value >= 50 else "#EF5350"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        title={"text": title, "font": {"size": 14, "color": "#9E9E9E"}},
        number={"font": {"size": 42, "color": color, "family": "Inter"}},
        gauge={
            "axis": {"range": [0, max_val], "tickwidth": 0, "tickcolor": "rgba(0,0,0,0)", "dtick": 25},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(26,29,41,0.5)", "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(239,83,80,0.08)"},
                {"range": [40, 70], "color": "rgba(255,167,38,0.08)"},
                {"range": [70, 100], "color": "rgba(0,230,118,0.08)"},
            ],
            "threshold": {"line": {"color": "#B388FF", "width": 2}, "thickness": 0.8, "value": value},
        },
    ))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

def create_radar_chart(scores):
    categories = ["Readability", "Engagement", "Clarity", "SEO"]
    values = [scores["readability"], scores["engagement"], scores["clarity"], scores["seo"]]
    values.append(values[0]); categories.append(categories[0])
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill="toself", fillcolor="rgba(124, 77, 255, 0.15)", line=dict(color="#7C4DFF", width=2), marker=dict(size=8, color="#B388FF")))
    fig.update_layout(
        polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(124,77,255,0.1)"), angularaxis=dict(gridcolor="rgba(124,77,255,0.1)", tickfont=dict(size=12, color="#B388FF"))),
        showlegend=False, height=320, margin=dict(l=60, r=60, t=30, b=30), paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig

def create_sentiment_bar(sentence_data):
    if not sentence_data: return None
    labels = [f"S{i+1}" for i in range(len(sentence_data))]
    polarities = [s["polarity"] for s in sentence_data]
    colors = ["#00E676" if p > 0.1 else "#EF5350" if p < -0.1 else "#FFA726" for p in polarities]
    fig = go.Figure(go.Bar(x=labels, y=polarities, marker_color=colors, hovertemplate="<b>%{x}</b><br>Polarity: %{y:.3f}<extra></extra>"))
    fig.update_layout(height=200, margin=dict(l=40, r=20, t=10, b=30), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(tickfont=dict(size=10, color="#666")), yaxis=dict(gridcolor="rgba(124,77,255,0.08)", tickfont=dict(size=10, color="#666"), zeroline=True, zerolinecolor="rgba(124,77,255,0.2)"))
    return fig

def create_keyword_chart(keywords):
    if not keywords: return None
    kw_data = keywords[:10]
    fig = go.Figure(go.Bar(x=[k["density"] for k in kw_data], y=[k["keyword"] for k in kw_data], orientation="h", marker=dict(color=[k["density"] for k in kw_data], colorscale=[[0, "#7C4DFF"], [0.5, "#B388FF"], [1, "#00E676"]])))
    fig.update_layout(height=max(200, len(kw_data) * 35), margin=dict(l=10, r=20, t=10, b=30), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(gridcolor="rgba(124,77,255,0.08)", tickfont=dict(size=10, color="#666"), title="Density %"), yaxis=dict(tickfont=dict(size=11, color="#B388FF"), autorange="reversed"))
    return fig

def render_diff_html(diff_segments):
    """Render diff segments as colored HTML."""
    html_parts = []
    for seg in diff_segments:
        if seg["type"] == "unchanged":
            html_parts.append(seg["text"])
        elif seg["type"] == "added":
            html_parts.append(f'<span class="diff-added">{seg["text"]}</span>')
        elif seg["type"] == "removed":
            html_parts.append(f'<span class="diff-removed">{seg["text"]}</span>')
    return " ".join(html_parts)

def score_class(val):
    if val >= 85: return "score-excellent"
    if val >= 70: return "score-good"
    if val >= 55: return "score-average"
    if val >= 40: return "score-below"
    return "score-poor"


# ─── Sidebar ─────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding: 1rem 0;">
        <span style="font-size: 2.5rem;">🧠</span>
        <h2 style="background: linear-gradient(135deg, #7C4DFF, #B388FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; margin: 0.5rem 0 0.2rem 0;">Content AI</h2>
        <p style="color: #666; font-size: 0.8rem;">v{APP_VERSION}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Goal-Based Optimization
    st.markdown("#### 🎯 Optimization Goal")
    domain_presets = get_domain_presets()
    selected_domain = st.selectbox(
        "Content Type", options=list(domain_presets.keys()),
        format_func=lambda x: domain_presets[x]["label"],
    )

    # Dynamic Scoring Weights
    st.markdown("#### ⚙️ Scoring Weights")
    use_custom = st.checkbox("Customize weights", value=False)
    custom_weights = None
    if use_custom:
        w_read = st.slider("Readability", 0, 100, 30, key="w_r") / 100
        w_eng = st.slider("Engagement", 0, 100, 25, key="w_e") / 100
        w_clar = st.slider("Clarity", 0, 100, 25, key="w_c") / 100
        w_seo = st.slider("SEO", 0, 100, 20, key="w_s") / 100
        total = w_read + w_eng + w_clar + w_seo
        if total > 0:
            custom_weights = {"readability": w_read/total, "engagement": w_eng/total, "clarity": w_clar/total, "seo": w_seo/total}

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # OpenAI API Key (optional premium)
    st.markdown("#### 🔑 Premium (Optional)")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...", help="Optional — for AI-powered rewriting")

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Quick Demo
    st.markdown("#### 📝 Quick Demo")
    sample_texts = {
        "Select a sample...": "",
        "📰 News Article": "The rapid advancement of artificial intelligence has transformed industries across the globe. From healthcare to finance, AI-powered systems are now capable of analyzing vast amounts of data and making decisions that were once the exclusive domain of human experts. However, this technological revolution has also raised important questions about ethics, employment, and the future of human creativity.\n\nRecent studies show that companies implementing AI solutions report an average productivity increase of 40 percent. Despite these gains, experts warn that the transition must be managed carefully to avoid displacing workers without providing adequate retraining opportunities.\n\nWhat does the future hold? Many researchers believe that the key lies not in replacing human workers, but in augmenting their capabilities. By combining human creativity with machine efficiency, organizations can achieve outcomes that neither could accomplish alone.",
        "🎓 Academic Abstract": "This study investigates the impact of social media usage on academic performance among university students. A cross-sectional survey was conducted with 500 participants from three major universities. The results indicate a statistically significant negative correlation between daily social media consumption exceeding four hours and grade point average. Furthermore, the analysis reveals that platforms with predominantly visual content exhibit a stronger negative association compared to text-based platforms. These findings suggest that educational institutions should develop targeted digital literacy programs to help students manage their online habits effectively while maintaining academic excellence.",
        "💼 Business Email": "Dear Team,\n\nI wanted to share some exciting news regarding our Q3 performance. We have exceeded our revenue targets by 15%, driven primarily by the successful launch of our new product line. This achievement reflects the hard work and dedication of every team member.\n\nMoving forward, I'd like to outline our priorities for Q4:\n1. Expand into two new market segments\n2. Improve customer retention by 10%\n3. Launch the updated mobile application\n\nPlease review the attached report for detailed figures. I look forward to discussing our strategy in next week's all-hands meeting.\n\nBest regards",
    }
    selected_sample = st.selectbox("Load sample text", options=list(sample_texts.keys()))

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Document Upload (moved to sidebar for clean UI)
    st.markdown("#### 📎 Upload Document")
    uploaded_file = st.file_uploader(
        "Document file",
        type=["pdf", "docx", "txt", "md"],
    )

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Insights panel
    st.markdown("#### 🔮 Smart Insights")
    insights_placeholder = st.empty()


# ─── Hero Header ─────────────────────────────────────────────────

st.markdown("""
<div class="hero-header">
    <h1 class="hero-title">🧠 AI Content Intelligence System</h1>
    <p class="hero-subtitle">Evaluate, improve, and optimize your content with advanced NLP — built for writers, students, and businesses.</p>
</div>
""", unsafe_allow_html=True)


# ─── Input Section ───────────────────────────────────────────────

col_input, col_title = st.columns([3, 1])

with col_input:
    default_text = sample_texts.get(selected_sample, "")
    user_text = st.text_area("✍️ Paste your content here", value=default_text, height=200, placeholder="Enter or paste your text for analysis...", key="main_text_input")

with col_title:
    content_title = st.text_input("📌 Content Title (for SEO)", placeholder="Your headline...")
    st.markdown('<p style="color:#9E9E9E;font-size:0.75rem;">Optional — used for headline analysis</p>', unsafe_allow_html=True)

# Handle uploaded document
if uploaded_file:
    try:
        from utils.extractor import extract_text
        extracted = extract_text(uploaded_file)
        if extracted and not extracted.startswith("[Error"):
            user_text = extracted
            st.success(f"✅ Extracted text from **{uploaded_file.name}**")
        else:
            st.error(f"❌ {extracted}")
    except Exception as e:
        st.error(f"❌ Extraction error: {e}")


# ─── Analyze Button ──────────────────────────────────────────────

ac1, ac2, ac3 = st.columns([1, 1, 2])
with ac1:
    analyze_btn = st.button("🚀 Analyze Content", use_container_width=True, type="primary")

if not user_text or not user_text.strip():
    st.markdown('<div class="glass-card" style="text-align:center;padding:3rem;"><p style="font-size:3rem;">✨</p><h3 style="color:#B388FF;">Ready to Analyze</h3><p style="color:#666;">Paste your content or upload a document.</p></div>', unsafe_allow_html=True)
    st.stop()

if not analyze_btn and "analysis_done" not in st.session_state:
    st.markdown('<div class="glass-card" style="text-align:center;padding:3rem;"><p style="font-size:3rem;">✨</p><h3 style="color:#B388FF;">Content Ready</h3><p style="color:#666;">Click <b>🚀 Analyze Content</b> to begin.</p></div>', unsafe_allow_html=True)
    st.stop()


# ─── Run Analysis (Cached) ──────────────────────────────────────

with st.spinner("🧠 Analyzing with NLP engines..."):
    cleaned = clean_text(user_text)
    if len(cleaned) < 30:
        st.warning("⚠️ Content too short. Please provide more text.")
        st.stop()

    text_stats = cached_text_stats(cleaned)
    readability_report = cached_readability(cleaned)
    tone_report = cached_tone(cleaned)
    scores = compute_content_score(cleaned, domain=selected_domain, custom_weights=custom_weights)
    seo_report = cached_seo(cleaned, content_title)
    score_label = get_score_label(scores["overall"])
    insights = generate_insights(scores, readability_report, tone_report, seo_report, text_stats)
    st.session_state["analysis_done"] = True


# ─── Quick Stats Bar ────────────────────────────────────────────

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

qs1, qs2, qs3, qs4, qs5 = st.columns(5)
with qs1:
    st.markdown(f'<div class="metric-card"><p class="metric-value {score_class(scores["overall"])}">{scores["overall"]}</p><p class="metric-label">Overall Score</p></div>', unsafe_allow_html=True)
with qs2:
    st.markdown(f'<div class="metric-card"><p class="metric-value" style="color:#B388FF;">{text_stats["words"]}</p><p class="metric-label">Words</p></div>', unsafe_allow_html=True)
with qs3:
    st.markdown(f'<div class="metric-card"><p class="metric-value" style="color:#B388FF;">{text_stats["sentences"]}</p><p class="metric-label">Sentences</p></div>', unsafe_allow_html=True)
with qs4:
    st.markdown(f'<div class="metric-card"><p class="metric-value" style="color:{readability_report["interpretation"]["color"]};">{readability_report["flesch_reading_ease"]}</p><p class="metric-label">Readability</p></div>', unsafe_allow_html=True)
with qs5:
    tc = tone_report["tone"]
    st.markdown(f'<div class="metric-card"><p class="metric-value" style="font-size:1.5rem;color:{tc["color"]};">{tc["emoji"]} {tc["tone"]}</p><p class="metric-label">Tone</p></div>', unsafe_allow_html=True)

# Domain badge
st.markdown(f'<div style="text-align:center;"><span class="badge badge-purple">🎯 {scores["domain_label"]}</span></div>', unsafe_allow_html=True)


# ─── Sidebar Insights ───────────────────────────────────────────

with insights_placeholder.container():
    for s in insights.get("strengths", [])[:3]:
        st.markdown(f'<div class="insight-strength">{s["icon"]} {s["text"]}</div>', unsafe_allow_html=True)
    for w in insights.get("weaknesses", [])[:3]:
        st.markdown(f'<div class="insight-weakness">{w["icon"]} {w["text"]}</div>', unsafe_allow_html=True)
    for t in insights.get("tips", [])[:4]:
        st.markdown(f'<div class="insight-tip">{t["icon"]} {t["text"]}</div>', unsafe_allow_html=True)


# ─── Main Tabs ───────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Dashboard", "🔍 SEO Analysis", "🧠 AI Rewrite", "🚨 Plagiarism", "🎓 Thesis Helper", "🤖 AI Intelligence"])


# ═══════════════ TAB 1: DASHBOARD ═══════════════════════════════

with tab1:
    cg, cr = st.columns([1, 1])
    with cg:
        st.markdown(f'<div class="glass-card" style="text-align:center;"><h4 style="color:#B388FF;">Content Quality Score</h4><span class="badge badge-{"green" if scores["overall"]>=70 else "yellow" if scores["overall"]>=50 else "red"}">{score_label["emoji"]} {score_label["label"]}</span></div>', unsafe_allow_html=True)
        st.plotly_chart(create_gauge_chart(scores["overall"], ""), use_container_width=True)
    with cr:
        st.markdown('<div class="glass-card"><h4 style="color:#B388FF;">Score Breakdown</h4></div>', unsafe_allow_html=True)
        st.plotly_chart(create_radar_chart(scores), use_container_width=True)

    # Readability
    st.markdown("### 📖 Readability Analysis")
    r1, r2, r3, r4 = st.columns(4)
    interp = readability_report["interpretation"]
    with r1:
        st.markdown(f'<div class="metric-card"><p class="metric-value" style="color:{interp["color"]};">{readability_report["flesch_reading_ease"]}</p><p class="metric-label">Flesch Reading Ease</p><p style="color:{interp["color"]};font-size:0.8rem;margin:0;">{interp["label"]}</p></div>', unsafe_allow_html=True)
    with r2:
        st.markdown(f'<div class="metric-card"><p class="metric-value" style="color:#B388FF;">{readability_report["flesch_kincaid_grade"]}</p><p class="metric-label">Grade Level</p></div>', unsafe_allow_html=True)
    with r3:
        st.markdown(f'<div class="metric-card"><p class="metric-value" style="color:#B388FF;">{readability_report["gunning_fog"]}</p><p class="metric-label">Gunning Fog</p></div>', unsafe_allow_html=True)
    with r4:
        st.markdown(f'<div class="metric-card"><p class="metric-value" style="color:#B388FF;">{readability_report["smog_index"]}</p><p class="metric-label">SMOG Index</p></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="glass-card"><p>{interp["icon"]} <b>Reading Level:</b> {interp["label"]} — {interp["description"]}</p><p>📚 <b>Audience:</b> {interp["audience"]}</p><p>📋 <b>Consensus Grade:</b> {readability_report["consensus_grade"]}</p></div>', unsafe_allow_html=True)

    # Tone
    st.markdown("### 🎭 Tone & Sentiment")
    t1, t2, t3 = st.columns(3)
    td, sd, fd = tone_report["tone"], tone_report["subjectivity"], tone_report["formality"]
    with t1:
        st.markdown(f'<div class="metric-card"><p style="font-size:2rem;margin:0;">{td["emoji"]}</p><p class="metric-value" style="font-size:1.3rem;color:{td["color"]};">{td["tone"]}</p><p class="metric-label">Sentiment</p></div>', unsafe_allow_html=True)
    with t2:
        st.markdown(f'<div class="metric-card"><p class="metric-value" style="font-size:1.3rem;color:{sd["color"]};">{sd["level"]}</p><p class="metric-label">Objectivity</p><p style="font-size:0.8rem;color:#666;margin:0;">{sd["description"]}</p></div>', unsafe_allow_html=True)
    with t3:
        st.markdown(f'<div class="metric-card"><p class="metric-value" style="font-size:1.3rem;color:{fd["color"]};">{fd["level"]}</p><p class="metric-label">Formality</p><p style="font-size:0.8rem;color:#666;margin:0;">Score: {fd["score"]}/100</p></div>', unsafe_allow_html=True)

    sent_data = tone_report.get("sentence_breakdown", [])
    if sent_data:
        st.markdown("#### Sentence-Level Sentiment")
        fig_sent = create_sentiment_bar(sent_data)
        if fig_sent:
            st.plotly_chart(fig_sent, use_container_width=True)

    # Text stats
    st.markdown("### 📐 Text Statistics")
    s1, s2, s3, s4 = st.columns(4)
    with s1: st.metric("Characters", f"{text_stats['characters']:,}")
    with s2: st.metric("Avg Word Length", f"{text_stats['avg_word_length']} chars")
    with s3: st.metric("Avg Sentence", f"{text_stats['avg_sentence_length']} words")
    with s4: st.metric("Reading Time", f"{text_stats['reading_time_min']} min")


# ═══════════════ TAB 2: SEO ═════════════════════════════════════

with tab2:
    if content_title:
        st.markdown("### 📰 Headline Analysis")
        hl = seo_report.get("headline_analysis", {})
        if hl:
            hc1, hc2, hc3 = st.columns(3)
            with hc1:
                st.markdown(f'<div class="metric-card"><p class="metric-value {score_class(hl.get("score",0))}">{hl.get("score",0)}</p><p class="metric-label">Headline Score</p></div>', unsafe_allow_html=True)
            with hc2: st.metric("Word Count", hl.get("word_count", 0))
            with hc3: st.metric("Char Count", hl.get("char_count", 0))
            for sug in hl.get("suggestions", []):
                st.info(f"💡 {sug}")

    # Search Intent (V3 NEW)
    intent = seo_report.get("search_intent", {})
    if intent:
        st.markdown("### 🎯 Search Intent Detection")
        pi = intent.get("primary", {})
        ic1, ic2 = st.columns(2)
        with ic1:
            st.markdown(f'<div class="metric-card"><p style="font-size:2rem;margin:0;">{pi.get("emoji","📚")}</p><p class="metric-value" style="font-size:1.3rem;color:#B388FF;">{pi.get("intent","Unknown")}</p><p class="metric-label">Primary Intent</p><p style="color:#666;font-size:0.8rem;margin:0;">{pi.get("description","")}</p></div>', unsafe_allow_html=True)
        with ic2:
            si = intent.get("secondary")
            if si:
                st.markdown(f'<div class="metric-card"><p style="font-size:2rem;margin:0;">{si.get("emoji","📚")}</p><p class="metric-value" style="font-size:1.3rem;color:#9E9E9E;">{si.get("intent","—")}</p><p class="metric-label">Secondary Intent</p></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="metric-card"><p style="color:#666;margin:0;">No secondary intent detected</p></div>', unsafe_allow_html=True)

    # TF-IDF Keywords
    tfidf = seo_report.get("tfidf_keywords", [])
    if tfidf:
        st.markdown("### 🏆 TF-IDF Important Keywords")
        tfidf_cols = st.columns(min(5, len(tfidf)))
        for idx, kw in enumerate(tfidf[:5]):
            with tfidf_cols[idx]:
                imp_color = "#00E676" if kw["importance"] == "high" else "#FFA726" if kw["importance"] == "medium" else "#666"
                st.markdown(f'<div class="metric-card"><p class="metric-value" style="font-size:1rem;color:{imp_color};">{kw["keyword"]}</p><p class="metric-label">TF-IDF: {kw["tfidf_score"]}</p></div>', unsafe_allow_html=True)

    st.markdown("### 🔑 Top Keywords")
    kw_col, stats_col = st.columns([2, 1])
    with kw_col:
        fig_kw = create_keyword_chart(seo_report.get("keywords", []))
        if fig_kw: st.plotly_chart(fig_kw, use_container_width=True)
    with stats_col:
        st.markdown(f'<div class="glass-card"><h4 style="color:#B388FF;">📊 SEO Stats</h4><p>📝 <b>Total Words:</b> {seo_report.get("total_words",0)}</p><p>🔤 <b>Unique Words:</b> {seo_report.get("unique_words",0)}</p><p>📚 <b>Vocabulary Richness:</b> {seo_report.get("vocabulary_richness",0)}%</p></div>', unsafe_allow_html=True)

    # Topic Clusters (NEW)
    clusters = seo_report.get("topic_clusters", [])
    if clusters:
        st.markdown("### 🧩 Topic Clusters")
        for cl in clusters:
            st.markdown(f'<div class="glass-card"><p style="color:#B388FF;font-weight:600;">{cl.get("label","")}</p><p style="color:#9E9E9E;">Keywords: {", ".join(cl.get("keywords",[]))}</p></div>', unsafe_allow_html=True)

    # SEO Suggestions (NEW)
    seo_suggestions = seo_report.get("seo_suggestions", [])
    if seo_suggestions:
        st.markdown("### 💡 SEO Recommendations")
        for sug in seo_suggestions:
            badge_cls = "badge-red" if sug["priority"] == "high" else "badge-yellow" if sug["priority"] == "medium" else "badge-green"
            st.markdown(f'{sug["icon"]} {sug["text"]} <span class="badge {badge_cls}">{sug["priority"]}</span>', unsafe_allow_html=True)

    # Keyword table
    keywords = seo_report.get("keywords", [])
    if keywords:
        st.markdown("### 📋 Keyword Density Table")
        import pandas as pd
        df = pd.DataFrame(keywords)
        df.columns = ["Keyword", "Count", "Density (%)"]
        st.dataframe(df, use_container_width=True, hide_index=True, column_config={"Density (%)": st.column_config.ProgressColumn(min_value=0, max_value=max(df["Density (%)"].max()*1.5, 5), format="%.2f%%")})


# ═══════════════ TAB 3: AI REWRITE ══════════════════════════════

with tab3:
    st.markdown('<div class="glass-card"><h3 style="color:#B388FF;margin:0;">🧠 AI Content Improvement Engine</h3><p style="color:#9E9E9E;margin:0.5rem 0 0 0;">Free grammar correction + rule-based optimization. Optional AI-powered rewriting with OpenAI.</p></div>', unsafe_allow_html=True)

    rw1, rw2 = st.columns(2)
    with rw1:
        rewrite_mode = st.radio("Mode", ["⚡ Rule-Based + Grammar (Free)", "🤖 AI-Powered (API Key)"], horizontal=True)
    with rw2:
        audience = st.selectbox("Audience", list(AUDIENCE_PRESETS.keys()), format_func=lambda x: AUDIENCE_PRESETS[x]["label"])
        st.caption(AUDIENCE_PRESETS[audience]["description"])

    if st.button("✨ Improve Content", use_container_width=True, type="primary", key="rewrite_btn"):
        if "Rule-Based" in rewrite_mode:
            with st.spinner("⚡ Applying improvements + grammar check..."):
                result = rule_based_rewrite(cleaned)

            # Changes summary
            st.markdown("### 📋 Changes Applied")
            for change in result["changes"]:
                st.markdown(f"- {change}")

            # Grammar corrections detail
            grammar = result.get("grammar", {})
            if grammar.get("available") and grammar.get("corrections"):
                st.markdown("### 📝 Grammar Corrections")
                for corr in grammar["corrections"][:8]:
                    st.markdown(f"""
                    <div class="grammar-fix">
                        <p style="margin:0;"><b>❌</b> <span class="diff-removed">{corr['original']}</span> → <b>✅</b> <span class="diff-added">{corr['suggestion']}</span></p>
                        <p style="color:#9E9E9E;font-size:0.8rem;margin:0.3rem 0 0 0;">💡 {corr['reason']}</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Change explanations
            if result.get("change_details"):
                st.markdown("### 📖 Why These Changes?")
                for cd in result["change_details"]:
                    st.markdown(f'<div class="insight-tip">💡 {cd["reason"]}</div>', unsafe_allow_html=True)

            # Diff View (NEW)
            if result.get("diff"):
                st.markdown("### 🔄 Diff View (Before → After)")
                diff_html = render_diff_html(result["diff"])
                st.markdown(f'<div class="glass-card" style="line-height:1.8;font-size:0.95rem;">{diff_html}</div>', unsafe_allow_html=True)

            # Side-by-side
            st.markdown("### 📝 Full Comparison")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<p style="color:#EF5350;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;font-size:0.85rem;">❌ ORIGINAL</p>', unsafe_allow_html=True)
                st.text_area("Original", value=cleaned[:2000], height=200, disabled=True, key="orig_compare")
            with c2:
                st.markdown('<p style="color:#00E676;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;font-size:0.85rem;">✅ IMPROVED</p>', unsafe_allow_html=True)
                st.text_area("Improved", value=result["improved_text"][:2000], height=200, disabled=True, key="imp_compare")

            # Passive voice
            if result.get("passive_suggestions"):
                st.markdown("### ⚠️ Passive Voice Instances")
                for ps in result["passive_suggestions"][:5]:
                    st.warning(f"**\"{ps['text']}\"** — {ps['reason']}")

        else:
            if not api_key:
                st.warning("⚠️ Enter your OpenAI API key in the sidebar for AI rewriting.")
            else:
                with st.spinner("🤖 AI rewriting..."):
                    result = ai_rewrite(cleaned, api_key, audience=audience)
                if result["success"]:
                    st.markdown(f'### 📝 AI-Improved Version <span class="badge badge-purple">{result["audience"]}</span>', unsafe_allow_html=True)
                    if result.get("diff"):
                        st.markdown("### 🔄 Diff View")
                        st.markdown(f'<div class="glass-card" style="line-height:1.8;">{render_diff_html(result["diff"])}</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.text_area("Original", value=cleaned[:2000], height=200, disabled=True, key="ai_orig")
                    with c2:
                        st.text_area("AI Improved", value=result["improved_text"][:2000], height=200, disabled=True, key="ai_imp")
                else:
                    st.error(f"❌ {result['error']}")


# ═══════════════ TAB 4: PLAGIARISM ══════════════════════════════

with tab4:
    st.markdown('<div class="glass-card"><h3 style="color:#B388FF;margin:0;">🚨 Plagiarism Risk Indicator</h3><p style="color:#9E9E9E;margin:0.5rem 0 0 0;">Internal repetition + n-gram fingerprinting + cross-document TF-IDF comparison.</p></div>', unsafe_allow_html=True)

    ref_text = st.text_area("📄 Reference text (optional)", height=120, placeholder="Paste reference text to compare against...")

    if st.button("🔍 Check Plagiarism Risk", use_container_width=True, key="plag_btn"):
        with st.spinner("🔍 Analyzing..."):
            plag_report = get_plagiarism_report(cleaned, ref_text if ref_text else None)

        internal = plag_report["internal"]
        p1, p2 = st.columns([1, 2])
        with p1:
            st.plotly_chart(create_gauge_chart(100 - internal["risk_score"], "Originality"), use_container_width=True)
        with p2:
            rb = "badge-green" if internal["risk_level"]=="Low" else "badge-yellow" if internal["risk_level"]=="Medium" else "badge-red"
            st.markdown(f'<div class="glass-card"><h4>Risk Assessment</h4><p><span class="badge {rb}">{internal["risk_level"]} Risk</span></p><p>{internal["message"]}</p><p style="color:#666;font-size:0.85rem;">📝 Sentences: {internal["total_sentences"]} | 🔄 Comparisons: {internal["total_comparisons"]}</p></div>', unsafe_allow_html=True)

        # Repeated n-grams (NEW)
        if internal.get("repeated_ngrams"):
            st.markdown("### 🔁 Repeated Phrases (N-gram Analysis)")
            for ng in internal["repeated_ngrams"][:5]:
                st.markdown(f'<div class="insight-tip">📌 "{ng["ngram"]}" — appears {ng["count"]}× </div>', unsafe_allow_html=True)

        if internal["similar_pairs"]:
            st.markdown("### ⚠️ Flagged Similar Sentences")
            for pair in internal["similar_pairs"][:5]:
                with st.expander(f"Similarity {pair['similarity']}% -- Sentences {pair['index_a']} and {pair['index_b']}"):
                    c1, c2 = st.columns(2)
                    with c1: st.markdown(f"**Sentence {pair['index_a']}:** {pair['sentence_a']}")
                    with c2: st.markdown(f"**Sentence {pair['index_b']}:** {pair['sentence_b']}")

        if "cross_document" in plag_report:
            st.markdown("### 📊 Cross-Document Comparison")
            cross = plag_report["cross_document"]
            st.markdown(f'<div class="glass-card"><p style="font-size:1.5rem;font-weight:800;color:{cross["color"]};">{cross["combined_similarity"]}% Combined Similarity</p><p>TF-IDF: {cross["tfidf_similarity"]}% | Fingerprint: {cross["fingerprint_similarity"]}%</p><p>Level: <span class="badge" style="background:{cross["color"]}20;color:{cross["color"]};">{cross["level"]}</span></p></div>', unsafe_allow_html=True)


# ═══════════════ TAB 5: THESIS HELPER ═══════════════════════════

with tab5:
    st.markdown('<div class="glass-card"><h3 style="color:#B388FF;margin:0;">🎓 Thesis Helper Mode</h3><p style="color:#9E9E9E;margin:0.5rem 0 0 0;">Structure analysis, citation format detection, argument coherence, and academic writing tips.</p></div>', unsafe_allow_html=True)

    if st.button("🎓 Analyze Academic Writing", use_container_width=True, key="thesis_btn"):
        with st.spinner("🎓 Analyzing..."):
            thesis_result = thesis_helper(cleaned, api_key if api_key else None)

        # Structure
        st.markdown("### 📋 Structure Analysis")
        sections = thesis_result.get("found_sections", {})
        cols = st.columns(min(6, len(sections)))
        for idx, (section, found) in enumerate(sections.items()):
            with cols[idx % len(cols)]:
                emoji = "✅" if found else "❌"
                color = "#00E676" if found else "#EF5350"
                label = section.replace("_", " ").title()
                st.markdown(f'<div class="metric-card"><p style="font-size:1.5rem;margin:0;">{emoji}</p><p class="metric-label" style="color:{color};">{label}</p></div>', unsafe_allow_html=True)

        # Citations (NEW)
        citations = thesis_result.get("citations", {})
        if citations:
            st.markdown("### 📚 Citation Analysis")
            for fmt, data in citations.items():
                st.markdown(f'<div class="glass-card"><p><b>{fmt}</b> format detected — {data["count"]} citation(s)</p><p style="color:#666;font-size:0.85rem;">Examples: {", ".join(data["examples"][:3])}</p></div>', unsafe_allow_html=True)

        # Coherence (NEW)
        coherence = thesis_result.get("coherence", {})
        if coherence:
            st.markdown("### 🔗 Argument Coherence")
            ch1, ch2, ch3 = st.columns(3)
            with ch1:
                st.markdown(f'<div class="metric-card"><p class="metric-value {score_class(coherence["score"])}">{coherence["score"]}</p><p class="metric-label">Coherence Score</p></div>', unsafe_allow_html=True)
            with ch2:
                st.metric("Claims", "✅ Found" if coherence["has_claims"] else "❌ Missing")
            with ch3:
                st.metric("Evidence", "✅ Found" if coherence["has_evidence"] else "❌ Missing")

        # Suggestions
        st.markdown("### 💡 Suggestions")
        for sug in thesis_result.get("suggestions", []):
            st.markdown(f'<div class="insight-tip">{sug}</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="glass-card"><p>📝 <b>Words:</b> {thesis_result.get("word_count",0)}</p><p>📄 <b>Paragraphs:</b> {thesis_result.get("paragraph_count",0)}</p></div>', unsafe_allow_html=True)

        if thesis_result.get("ai_improved"):
            st.markdown("### 🤖 AI-Improved Academic Version")
            st.text_area("AI Academic", value=thesis_result["ai_improved"][:2000], height=200, disabled=True, key="thesis_ai")


# ═══════════════ TAB 6: AI INTELLIGENCE ═════════════════════════

with tab6:
    st.markdown('<div class="glass-card"><h3 style="color:#B388FF;margin:0;">🤖 AI Intelligence Engine</h3><p style="color:#9E9E9E;margin:0.5rem 0 0 0;">Semantic embeddings, coherence analysis, topic detection, and ML-enhanced quality scoring powered by sentence-transformers.</p></div>', unsafe_allow_html=True)

    if st.button("🧠 Run AI Analysis", use_container_width=True, key="ai_intel_btn", type="primary"):
        if not HAS_EMBEDDINGS or not embeddings_available():
            st.warning("⚠️ sentence-transformers not available. Install with: `pip install sentence-transformers`")
            st.info("💡 The system will run full AI analysis when the library is installed. On Streamlit Cloud, this requires sufficient memory.")
        else:
            with st.spinner("🧠 Running deep AI analysis with sentence embeddings..."):
                sem_report = get_semantic_report(cleaned)

            if sem_report.get("available"):
                # ML Quality Score
                quality = sem_report.get("quality", {})
                if quality.get("available"):
                    st.markdown("### 🏆 ML-Enhanced Quality Score")
                    mq1, mq2, mq3, mq4 = st.columns(4)
                    with mq1:
                        st.plotly_chart(create_gauge_chart(quality["score"], "ML Score"), use_container_width=True)
                    with mq2:
                        st.markdown(f'<div class="metric-card"><p class="metric-value" style="color:#7C4DFF;">{quality["coherence"]}</p><p class="metric-label">Coherence</p></div>', unsafe_allow_html=True)
                    with mq3:
                        st.markdown(f'<div class="metric-card"><p class="metric-value" style="color:#B388FF;">{quality["diversity"]}</p><p class="metric-label">Diversity</p></div>', unsafe_allow_html=True)
                    with mq4:
                        st.markdown(f'<div class="metric-card"><p class="metric-value" style="color:#00E676;">{quality["richness"]}</p><p class="metric-label">Richness</p></div>', unsafe_allow_html=True)

                # Coherence
                coh = sem_report.get("coherence", {})
                if coh.get("available"):
                    st.markdown("### 🔗 Semantic Coherence")
                    st.markdown(f'<div class="glass-card"><p class="metric-value" style="font-size:1.5rem;color:{coh.get("color","#B388FF")};">Coherence: {coh["score"]}%</p><p style="color:#9E9E9E;">{coh["label"]}</p><p style="color:#666;font-size:0.85rem;">Based on {coh.get("total_sentences",0)} sentences</p></div>', unsafe_allow_html=True)

                    # Sentence flow chart
                    sims = coh.get("sentence_similarities", [])
                    if sims:
                        pairs = [s["pair"] for s in sims]
                        vals = [s["similarity"] for s in sims]
                        colors = ["#00E676" if v >= 50 else "#FFA726" if v >= 30 else "#EF5350" for v in vals]
                        import plotly.graph_objects as go
                        fig = go.Figure(go.Bar(x=pairs, y=vals, marker_color=colors))
                        fig.update_layout(height=200, margin=dict(l=40, r=20, t=10, b=40), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(title="Similarity %", gridcolor="rgba(124,77,255,0.08)"), xaxis=dict(tickfont=dict(size=9, color="#666")))
                        st.plotly_chart(fig, use_container_width=True)

                    # Weak transitions
                    weak = coh.get("weak_transitions", [])
                    if weak:
                        st.markdown("#### ⚠️ Weakest Transitions")
                        for w in weak:
                            st.markdown(f'<div class="insight-weakness">🔗 {w["pair"]}: {w["similarity"]}% — <em>"{w["sentences"][0][:60]}..."</em> → <em>"{w["sentences"][1][:60]}..."</em></div>', unsafe_allow_html=True)

                # Topics
                topics = sem_report.get("topics", {})
                if topics.get("available") and topics.get("topics"):
                    st.markdown("### 🗂️ AI-Detected Topics")
                    for t in topics["topics"]:
                        st.markdown(f'<div class="glass-card"><p style="color:#B388FF;font-weight:700;">Topic {t["id"]}: {" • ".join(t["keywords"][:4])}</p><p style="color:#666;font-size:0.85rem;">📝 {t["sentence_count"]} sentences | Preview: <em>{t["preview"][:100]}...</em></p></div>', unsafe_allow_html=True)

            else:
                st.error("❌ Embeddings engine not available.")
    else:
        st.markdown('<div class="glass-card" style="text-align:center;padding:2rem;"><p style="font-size:3rem;">🤖</p><h3 style="color:#B388FF;">AI Intelligence</h3><p style="color:#666;">Click <b>🧠 Run AI Analysis</b> to perform deep semantic analysis using sentence embeddings.</p><p style="color:#666;font-size:0.85rem;">This analyzes: semantic coherence, topic detection, ML-enhanced quality scoring</p></div>', unsafe_allow_html=True)


# ─── Footer ──────────────────────────────────────────────────────

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center;padding:1rem;color:#666;"><p style="margin:0;">🧠 <b>AI Content Intelligence System</b> v{APP_VERSION}</p><p style="margin:0;font-size:0.8rem;">Powered by NLP + AI Embeddings • Built for Writers, Students & Businesses</p></div>', unsafe_allow_html=True)
