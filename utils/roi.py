"""
AI Content Intelligence System — Content ROI Calculator (V4)
Estimate business impact: traffic, time-on-page, conversion lift.
"""


def estimate_traffic_potential(seo_score, word_count):
    """Estimate monthly organic traffic potential."""
    # Base traffic estimate from SEO score
    if seo_score >= 80:
        base_range = (500, 5000)
    elif seo_score >= 60:
        base_range = (100, 1500)
    elif seo_score >= 40:
        base_range = (20, 500)
    else:
        base_range = (5, 100)

    # Word count multiplier (longer content ranks better)
    if word_count >= 2000:
        multiplier = 1.8
    elif word_count >= 1000:
        multiplier = 1.4
    elif word_count >= 500:
        multiplier = 1.0
    else:
        multiplier = 0.6

    low = int(base_range[0] * multiplier)
    high = int(base_range[1] * multiplier)

    return {"low": low, "high": high, "multiplier": round(multiplier, 1)}


def estimate_time_on_page(readability_score, engagement_score, word_count):
    """Estimate average time on page in seconds."""
    # Average reading speed: ~250 wpm
    reading_time_min = word_count / 250

    # Engagement affects how much of the content is read
    if engagement_score >= 70:
        read_pct = 0.85
    elif engagement_score >= 50:
        read_pct = 0.65
    elif engagement_score >= 30:
        read_pct = 0.45
    else:
        read_pct = 0.30

    # Readability affects scanning speed
    if readability_score >= 70:
        speed_factor = 1.0  # Easy to read, normal time
    elif readability_score >= 50:
        speed_factor = 1.15  # Slightly slower
    else:
        speed_factor = 0.85  # Hard content = more bounces, less time

    estimated_seconds = reading_time_min * 60 * read_pct * speed_factor

    return {
        "seconds": int(estimated_seconds),
        "minutes": round(estimated_seconds / 60, 1),
        "read_percentage": round(read_pct * 100),
    }


def estimate_conversion_lift(overall_score, current_baseline=2.0):
    """
    Estimate conversion rate improvement potential.
    baseline is industry average conversion rate (%).
    """
    if overall_score >= 85:
        lift_pct = 35
    elif overall_score >= 70:
        lift_pct = 20
    elif overall_score >= 55:
        lift_pct = 10
    elif overall_score >= 40:
        lift_pct = 0
    else:
        lift_pct = -10

    new_rate = round(current_baseline * (1 + lift_pct / 100), 2)

    return {
        "lift_percentage": lift_pct,
        "baseline_rate": current_baseline,
        "estimated_rate": new_rate,
        "improvement": round(new_rate - current_baseline, 2),
    }


def estimate_content_value(traffic_potential, conversion_rate, avg_order_value=50):
    """Estimate monthly content value in USD."""
    avg_traffic = (traffic_potential["low"] + traffic_potential["high"]) / 2
    monthly_conversions = avg_traffic * (conversion_rate / 100)
    monthly_value = monthly_conversions * avg_order_value

    return {
        "monthly_visitors": int(avg_traffic),
        "monthly_conversions": round(monthly_conversions, 1),
        "monthly_value": round(monthly_value, 2),
        "annual_value": round(monthly_value * 12, 2),
    }


def get_roi_report(scores, word_count):
    """
    Generate full ROI report.
    scores: dict with overall, readability, engagement, clarity, seo
    """
    traffic = estimate_traffic_potential(scores.get("seo", 50), word_count)
    time_on_page = estimate_time_on_page(
        scores.get("readability", 50),
        scores.get("engagement", 50),
        word_count,
    )
    conversion = estimate_conversion_lift(scores.get("overall", 50))
    value = estimate_content_value(traffic, conversion["estimated_rate"])

    # Optimization tips
    tips = []
    if scores.get("seo", 0) < 60:
        tips.append({"icon": "🔍", "tip": "Improve SEO score to increase organic traffic potential",
                     "impact": "High"})
    if scores.get("engagement", 0) < 50:
        tips.append({"icon": "📈", "tip": "Boost engagement to increase time-on-page",
                     "impact": "Medium"})
    if scores.get("readability", 0) < 50:
        tips.append({"icon": "📖", "tip": "Improve readability to reduce bounce rate",
                     "impact": "High"})
    if word_count < 800:
        tips.append({"icon": "📝", "tip": f"Increase content length (currently {word_count} words). "
                     "1000+ words rank better.", "impact": "High"})
    if scores.get("overall", 0) >= 70:
        tips.append({"icon": "🏆", "tip": "Content is well-optimized! Consider A/B testing headlines.",
                     "impact": "Low"})

    return {
        "traffic": traffic,
        "time_on_page": time_on_page,
        "conversion": conversion,
        "value": value,
        "tips": tips,
    }
