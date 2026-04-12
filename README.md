# 🧠 AI Content Intelligence System

> **AI-powered content analysis, scoring, and rewriting platform — built for writers, students, and businesses.**

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **Content Scoring** | Unified 0–100 quality score (readability, engagement, clarity, SEO) |
| 📖 **Readability Analysis** | Flesch, Gunning Fog, SMOG, Coleman-Liau, and grade-level assessment |
| 🎭 **Tone Detection** | Sentiment polarity, subjectivity, and formality analysis |
| 🔍 **SEO Analysis** | Keyword density, bigrams, headline optimization, vocabulary richness |
| 🧠 **AI Rewrite Engine** | Rule-based + OpenAI-powered content improvement |
| 🎓 **Thesis Helper** | Academic structure analysis, citation checks, hedging detection |
| 🚨 **Plagiarism Risk** | Internal similarity analysis + cross-document TF-IDF comparison |
| 📄 **Document Support** | Upload PDF, DOCX, TXT, MD files |
| 🎯 **Audience Rewriting** | Academic, Business, and Casual tone presets |

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Download TextBlob corpora
python -m textblob.download_corpora

# Run the application
streamlit run app.py
```

## 🏗️ Architecture

```
AI CONTENT INTELLIGENCE SYSTEM/
├── app.py                  # Streamlit UI (premium dark theme)
├── config.py               # Centralized configuration
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Theme configuration
├── utils/
│   ├── extractor.py        # PDF/DOCX/TXT text extraction
│   ├── cleaner.py          # Text normalization & statistics
│   ├── readability.py      # Readability scoring engine
│   ├── tone.py             # Sentiment & formality detection
│   ├── scoring.py          # Unified content scoring (0–100)
│   ├── seo.py              # Keyword density & SEO analysis
│   ├── rewrite.py          # Rule-based + AI rewrite engine
│   ├── plagiarism.py       # Similarity & plagiarism risk
│   └── insights.py         # Smart insight generation
├── data/                   # Input data directory
└── outputs/                # Generated outputs
```

## ⚙️ Configuration

Set your OpenAI API key as an environment variable or enter it in the sidebar:

```bash
set OPENAI_API_KEY=sk-your-key-here
```

## 📋 Tech Stack

- **Python 3.9+**
- **Streamlit** — Premium web UI
- **TextBlob** — Sentiment analysis
- **textstat** — Readability metrics
- **Plotly** — Interactive visualizations
- **PyMuPDF** — PDF text extraction
- **python-docx** — DOCX support
- **scikit-learn** — TF-IDF similarity
- **OpenAI** (optional) — AI-powered rewriting

## 👥 Target Users

- ✍️ **Writers & Bloggers** — Improve content quality
- 🎓 **Students & Researchers** — Academic writing assistant
- 💼 **Businesses & Agencies** — Professional content optimization

---

*Built with ❤️ using AI & NLP*
