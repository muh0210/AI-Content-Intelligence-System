"""
AI Content Intelligence System — Semantic Embeddings Engine (V3 — NEW)
Sentence embeddings for: semantic similarity, coherence scoring, 
topic detection, and content intelligence.
Uses sentence-transformers (all-MiniLM-L6-v2) — free, runs locally.
"""

import re
import numpy as np

# ═══════════════════════════════════════════════════════════════════
# Model Loading (Lazy + Cached)
# ═══════════════════════════════════════════════════════════════════

_model = None
_model_available = None


def _get_model():
    """Lazy-load the sentence transformer model."""
    global _model, _model_available
    if _model_available is not None:
        return _model if _model_available else None
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        _model_available = True
        return _model
    except ImportError:
        _model_available = False
        return None
    except Exception:
        _model_available = False
        return None


def is_available():
    """Check if embeddings engine is available."""
    return _get_model() is not None


def encode_text(text):
    """Encode text into embedding vector."""
    model = _get_model()
    if model is None:
        return None
    return model.encode(text, show_progress_bar=False)


def encode_sentences(sentences):
    """Encode list of sentences into embedding matrix."""
    model = _get_model()
    if model is None:
        return None
    return model.encode(sentences, show_progress_bar=False)


# ═══════════════════════════════════════════════════════════════════
# Semantic Similarity
# ═══════════════════════════════════════════════════════════════════

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def semantic_similarity(text_a, text_b):
    """
    Compute semantic similarity between two texts.
    Returns 0–100 score.
    """
    emb_a = encode_text(text_a)
    emb_b = encode_text(text_b)
    if emb_a is None or emb_b is None:
        return {"score": 0, "available": False}

    sim = cosine_similarity(emb_a, emb_b)
    return {
        "score": round(sim * 100, 1),
        "raw": round(sim, 4),
        "available": True,
    }


# ═══════════════════════════════════════════════════════════════════
# Content Coherence Scoring
# ═══════════════════════════════════════════════════════════════════

def coherence_score(text):
    """
    Score how well the content flows logically.
    Measures semantic similarity between adjacent sentences.
    High coherence = smooth topic transitions.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if len(sentences) < 3:
        return {
            "score": 75,
            "label": "Insufficient text for coherence analysis",
            "sentence_similarities": [],
            "available": True,
        }

    embeddings = encode_sentences(sentences)
    if embeddings is None:
        return {"score": 0, "available": False}

    # Compute adjacent sentence similarities
    similarities = []
    for i in range(len(embeddings) - 1):
        sim = cosine_similarity(embeddings[i], embeddings[i + 1])
        similarities.append({
            "pair": f"S{i+1}→S{i+2}",
            "similarity": round(sim * 100, 1),
            "sentences": (sentences[i][:80], sentences[i+1][:80]),
        })

    avg_sim = np.mean([s["similarity"] for s in similarities])

    # Score interpretation
    if avg_sim >= 60:
        label = "Excellent — Content flows smoothly with strong topic continuity"
        color = "#00E676"
    elif avg_sim >= 40:
        label = "Good — Generally coherent with minor topic shifts"
        color = "#66BB6A"
    elif avg_sim >= 25:
        label = "Fair — Some disconnected ideas or abrupt transitions"
        color = "#FFA726"
    else:
        label = "Weak — Content jumps between unrelated topics"
        color = "#EF5350"

    # Find weakest transitions
    weak_spots = sorted(similarities, key=lambda x: x["similarity"])[:3]

    return {
        "score": round(avg_sim, 1),
        "label": label,
        "color": color,
        "sentence_similarities": similarities,
        "weak_transitions": weak_spots,
        "total_sentences": len(sentences),
        "available": True,
    }


# ═══════════════════════════════════════════════════════════════════
# Topic Detection
# ═══════════════════════════════════════════════════════════════════

def detect_topics(text, n_topics=3):
    """
    Detect main topics by clustering sentence embeddings.
    Uses simple centroid-based clustering.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    if len(sentences) < 3:
        return {"topics": [], "available": True}

    embeddings = encode_sentences(sentences)
    if embeddings is None:
        return {"topics": [], "available": False}

    # Simple k-means-like clustering
    n_topics = min(n_topics, len(sentences) // 2, 5)
    if n_topics < 1:
        n_topics = 1

    try:
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=n_topics, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)

        topics = []
        for i in range(n_topics):
            cluster_sents = [sentences[j] for j in range(len(sentences)) if labels[j] == i]
            if cluster_sents:
                # Get key words from the cluster
                all_words = " ".join(cluster_sents).lower().split()
                from collections import Counter
                stop = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at",
                        "to", "for", "of", "with", "and", "or", "but", "that", "this",
                        "it", "by", "from", "as", "be", "has", "have", "had", "not",
                        "they", "their", "them", "its", "can", "will", "would", "could",
                        "should", "may", "might"}
                filtered = [w for w in all_words if len(w) > 3 and w not in stop]
                top_words = [w for w, _ in Counter(filtered).most_common(5)]

                topics.append({
                    "id": i + 1,
                    "keywords": top_words,
                    "sentence_count": len(cluster_sents),
                    "preview": cluster_sents[0][:120],
                })

        return {"topics": topics, "available": True}

    except ImportError:
        return {"topics": [], "available": False}


# ═══════════════════════════════════════════════════════════════════
# Semantic Quality Score (ML-Enhanced)
# ═══════════════════════════════════════════════════════════════════

def semantic_quality_score(text):
    """
    Compute an ML-enhanced quality score using embeddings.
    Combines coherence, diversity, and semantic richness.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if len(sentences) < 2:
        return {"score": 50, "available": True, "components": {}}

    embeddings = encode_sentences(sentences)
    if embeddings is None:
        return {"score": 0, "available": False, "components": {}}

    # Component 1: Coherence (adjacent similarity)
    adj_sims = []
    for i in range(len(embeddings) - 1):
        adj_sims.append(cosine_similarity(embeddings[i], embeddings[i + 1]))
    coherence = np.mean(adj_sims) * 100 if adj_sims else 50

    # Component 2: Diversity (average pairwise distance)
    all_sims = []
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            all_sims.append(cosine_similarity(embeddings[i], embeddings[j]))
    avg_sim = np.mean(all_sims) if all_sims else 0.5
    diversity = (1 - avg_sim) * 100  # Lower similarity = higher diversity

    # Component 3: Richness (spread of embedding space)
    centroid = np.mean(embeddings, axis=0)
    distances = [np.linalg.norm(e - centroid) for e in embeddings]
    richness = min(100, np.std(distances) * 500)

    # Weighted ML-enhanced score
    ml_score = (coherence * 0.4) + (diversity * 0.3) + (richness * 0.3)
    ml_score = max(0, min(100, ml_score))

    return {
        "score": round(ml_score, 1),
        "coherence": round(coherence, 1),
        "diversity": round(diversity, 1),
        "richness": round(richness, 1),
        "available": True,
        "components": {
            "coherence": round(coherence, 1),
            "diversity": round(diversity, 1),
            "richness": round(richness, 1),
        },
    }


# ═══════════════════════════════════════════════════════════════════
# Full Semantic Report
# ═══════════════════════════════════════════════════════════════════

def get_semantic_report(text):
    """Generate comprehensive semantic analysis report."""
    if not is_available():
        return {
            "available": False,
            "error": "sentence-transformers not installed. Run: pip install sentence-transformers",
        }

    return {
        "available": True,
        "coherence": coherence_score(text),
        "topics": detect_topics(text),
        "quality": semantic_quality_score(text),
    }
