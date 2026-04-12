"""
AI Content Intelligence System — Competitor Content Benchmarking (V4)
Scrape competitor URLs → analyze → side-by-side comparison.
"""

import re
import requests
from bs4 import BeautifulSoup


def scrape_url(url, timeout=10):
    """
    Scrape text content from a URL.
    Returns extracted text or error message.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
        }
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove unwanted elements
        for tag in soup(["script", "style", "nav", "footer", "header",
                         "aside", "iframe", "noscript", "form"]):
            tag.decompose()

        # Try to find main content area
        main = (
            soup.find("article")
            or soup.find("main")
            or soup.find("div", class_=re.compile(r"(content|article|post|entry)", re.I))
            or soup.find("body")
        )

        if main:
            text = main.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)

        # Clean up
        lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 20]
        cleaned = "\n".join(lines)

        # Extract title
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Extract meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc["content"] if meta_desc and meta_desc.get("content") else ""

        if len(cleaned) < 100:
            return {"success": False, "error": "Could not extract enough content from this URL."}

        return {
            "success": True,
            "text": cleaned[:10000],  # Cap at 10k chars
            "title": title,
            "description": description,
            "word_count": len(cleaned.split()),
            "url": url,
        }

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. The website took too long to respond."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect to the URL. Check the address."}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"HTTP error: {e.response.status_code}"}
    except Exception as e:
        return {"success": False, "error": f"Scraping failed: {str(e)[:200]}"}


def benchmark_comparison(your_scores, competitor_scores):
    """
    Generate side-by-side comparison between your content and competitor's.
    Both inputs should be dicts with: overall, readability, engagement, clarity, seo
    """
    metrics = ["overall", "readability", "engagement", "clarity", "seo"]
    comparison = []

    for metric in metrics:
        yours = your_scores.get(metric, 0)
        theirs = competitor_scores.get(metric, 0)
        diff = round(yours - theirs, 1)

        if diff > 5:
            verdict = "You Win"
            color = "#00E676"
            emoji = "🏆"
        elif diff < -5:
            verdict = "They Win"
            color = "#EF5350"
            emoji = "📉"
        else:
            verdict = "Tied"
            color = "#FFA726"
            emoji = "🤝"

        comparison.append({
            "metric": metric.title(),
            "yours": yours,
            "theirs": theirs,
            "diff": diff,
            "verdict": verdict,
            "color": color,
            "emoji": emoji,
        })

    # Overall winner
    your_total = sum(your_scores.get(m, 0) for m in metrics)
    their_total = sum(competitor_scores.get(m, 0) for m in metrics)

    if your_total > their_total + 10:
        winner = {"text": "Your content outperforms the competitor!", "emoji": "🏆", "color": "#00E676"}
    elif their_total > your_total + 10:
        winner = {"text": "Competitor content scores higher. Review suggestions.", "emoji": "⚔️", "color": "#EF5350"}
    else:
        winner = {"text": "Very close match! Focus on differentiators.", "emoji": "🤝", "color": "#FFA726"}

    return {
        "comparison": comparison,
        "winner": winner,
        "your_total": round(your_total, 1),
        "their_total": round(their_total, 1),
    }
