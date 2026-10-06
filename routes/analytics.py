from collections import defaultdict
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from flask import Blueprint, render_template, jsonify, session
from database.database import db
from database.models import SentimentResult
from routes.auth import login_required

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def analytics():
    """
    Renders analytics dashboard with calculated database statistics.
    All data is derived from actual records stored in the SQLite database.
    """
    user_id = session['user_id']
    stats = _compute_user_metrics(user_id)
    return render_template('analytics.html', stats=stats)

@analytics_bp.route('/api/analytics-data')
@login_required
def analytics_data():
    """
    API endpoint returning structured metrics for Chart.js:
    - Sentiment distribution (Doughnut)
    - Polarity score bucket distribution (Bar)
    - Subjectivity score bucket distribution (Bar / Radar)
    - Analysis activity timeline (Line / Area)
    """
    user_id = session['user_id']
    metrics = _compute_user_metrics(user_id)
    return jsonify(metrics)

def _compute_user_metrics(user_id: int) -> dict:
    """Helper calculating strictly real mathematical statistics for a user's records."""
    records = SentimentResult.query.filter_by(user_id=user_id).all()
    total = len(records)

    if total == 0:
        return {
            'total': 0,
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'positive_pct': 0.0,
            'negative_pct': 0.0,
            'neutral_pct': 0.0,
            'avg_polarity': 0.0,
            'avg_polarity_display': '+0.00',
            'avg_subjectivity': 0.0,
            'avg_subjectivity_display': '0.00',
            'polarity_buckets': {
                'Strong Negative (-1.0 to -0.6)': 0,
                'Moderate Negative (-0.6 to -0.1)': 0,
                'Neutral (-0.1 to +0.1)': 0,
                'Moderate Positive (+0.1 to +0.6)': 0,
                'Strong Positive (+0.6 to +1.0)': 0
            },
            'subjectivity_buckets': {
                'Objective (0.0 - 0.2)': 0,
                'Mod. Objective (0.2 - 0.4)': 0,
                'Balanced (0.4 - 0.6)': 0,
                'Mod. Subjective (0.6 - 0.8)': 0,
                'Highly Subjective (0.8 - 1.0)': 0
            },
            'timeline': {'labels': [], 'counts': [], 'positive': [], 'negative': [], 'neutral': []}
        }

    pos_count = sum(1 for r in records if r.sentiment == 'POSITIVE')
    neg_count = sum(1 for r in records if r.sentiment == 'NEGATIVE')
    neu_count = sum(1 for r in records if r.sentiment == 'NEUTRAL')

    avg_polarity = sum(r.polarity for r in records) / total
    avg_subjectivity = sum(r.subjectivity for r in records) / total

    # Polarity distribution buckets
    pol_buckets = {
        'Strong Negative (-1.0 to -0.6)': 0,
        'Moderate Negative (-0.6 to -0.1)': 0,
        'Neutral (-0.1 to +0.1)': 0,
        'Moderate Positive (+0.1 to +0.6)': 0,
        'Strong Positive (+0.6 to +1.0)': 0
    }
    for r in records:
        p = r.polarity
        if p <= -0.60:
            pol_buckets['Strong Negative (-1.0 to -0.6)'] += 1
        elif p < -0.10:
            pol_buckets['Moderate Negative (-0.6 to -0.1)'] += 1
        elif p <= 0.10:
            pol_buckets['Neutral (-0.1 to +0.1)'] += 1
        elif p <= 0.60:
            pol_buckets['Moderate Positive (+0.1 to +0.6)'] += 1
        else:
            pol_buckets['Strong Positive (+0.6 to +1.0)'] += 1

    # Subjectivity distribution buckets
    subj_buckets = {
        'Objective (0.0 - 0.2)': 0,
        'Mod. Objective (0.2 - 0.4)': 0,
        'Balanced (0.4 - 0.6)': 0,
        'Mod. Subjective (0.6 - 0.8)': 0,
        'Highly Subjective (0.8 - 1.0)': 0
    }
    for r in records:
        s = r.subjectivity
        if s <= 0.20:
            subj_buckets['Objective (0.0 - 0.2)'] += 1
        elif s <= 0.40:
            subj_buckets['Mod. Objective (0.2 - 0.4)'] += 1
        elif s <= 0.60:
            subj_buckets['Balanced (0.4 - 0.6)'] += 1
        elif s <= 0.80:
            subj_buckets['Mod. Subjective (0.6 - 0.8)'] += 1
        else:
            subj_buckets['Highly Subjective (0.8 - 1.0)'] += 1

    # Activity timeline (grouped by date)
    date_counts = defaultdict(lambda: {'total': 0, 'pos': 0, 'neg': 0, 'neu': 0})
    for r in records:
        date_key = r.created_at.strftime('%Y-%m-%d') if r.created_at else 'Unknown'
        date_counts[date_key]['total'] += 1
        if r.sentiment == 'POSITIVE':
            date_counts[date_key]['pos'] += 1
        elif r.sentiment == 'NEGATIVE':
            date_counts[date_key]['neg'] += 1
        else:
            date_counts[date_key]['neu'] += 1

    sorted_dates = sorted(date_counts.keys())
    # Format labels for display (e.g. "Sep 28")
    formatted_labels = []
    total_series = []
    pos_series = []
    neg_series = []
    neu_series = []

    for d in sorted_dates:
        try:
            dt = datetime.strptime(d, '%Y-%m-%d')
            formatted_labels.append(dt.strftime('%b %d'))
        except ValueError:
            formatted_labels.append(d)
        total_series.append(date_counts[d]['total'])
        pos_series.append(date_counts[d]['pos'])
        neg_series.append(date_counts[d]['neg'])
        neu_series.append(date_counts[d]['neu'])

    return {
        'total': total,
        'positive': pos_count,
        'negative': neg_count,
        'neutral': neu_count,
        'positive_pct': round((pos_count / total) * 100, 1),
        'negative_pct': round((neg_count / total) * 100, 1),
        'neutral_pct': round((neu_count / total) * 100, 1),
        'avg_polarity': round(avg_polarity, 4),
        'avg_polarity_display': f"{avg_polarity:+.2f}",
        'avg_subjectivity': round(avg_subjectivity, 4),
        'avg_subjectivity_display': f"{avg_subjectivity:.2f}",
        'polarity_buckets': pol_buckets,
        'subjectivity_buckets': subj_buckets,
        'timeline': {
            'labels': formatted_labels,
            'counts': total_series,
            'positive': pos_series,
            'negative': neg_series,
            'neutral': neu_series
        }
    }
