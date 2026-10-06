import io
from datetime import datetime, timezone
import pandas as pd
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session, Response
from database.database import db
from database.models import SentimentResult
from routes.auth import login_required

history_bp = Blueprint('history', __name__)

@history_bp.route('/history')
@login_required
def history():
    """
    Searchable, filterable analysis history table.
    Supports text keyword search, sentiment filter, sorting, and pagination.
    """
    user_id = session['user_id']

    # URL query params
    search_query = request.args.get('q', '').strip()
    sentiment_filter = request.args.get('sentiment', 'ALL').strip().upper()
    sort_by = request.args.get('sort', 'newest').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Build query
    query = SentimentResult.query.filter_by(user_id=user_id)

    # Keyword search
    if search_query:
        query = query.filter(SentimentResult.text.ilike(f"%{search_query}%"))

    # Sentiment filter
    if sentiment_filter in ['POSITIVE', 'NEGATIVE', 'NEUTRAL']:
        query = query.filter_by(sentiment=sentiment_filter)

    # Sorting
    if sort_by == 'oldest':
        query = query.order_by(SentimentResult.created_at.asc())
    elif sort_by == 'highest_polarity':
        query = query.order_by(SentimentResult.polarity.desc())
    elif sort_by == 'lowest_polarity':
        query = query.order_by(SentimentResult.polarity.asc())
    elif sort_by == 'highest_subjectivity':
        query = query.order_by(SentimentResult.subjectivity.desc())
    else:  # 'newest' default
        query = query.order_by(SentimentResult.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    results = pagination.items

    # Sentiment summary counts for badge tabs
    total_all = SentimentResult.query.filter_by(user_id=user_id).count()
    pos_count = SentimentResult.query.filter_by(user_id=user_id, sentiment='POSITIVE').count()
    neg_count = SentimentResult.query.filter_by(user_id=user_id, sentiment='NEGATIVE').count()
    neu_count = SentimentResult.query.filter_by(user_id=user_id, sentiment='NEUTRAL').count()

    counts = {
        'ALL': total_all,
        'POSITIVE': pos_count,
        'NEGATIVE': neg_count,
        'NEUTRAL': neu_count
    }

    return render_template(
        'history.html',
        results=results,
        pagination=pagination,
        search_query=search_query,
        sentiment_filter=sentiment_filter,
        sort_by=sort_by,
        counts=counts
    )

@history_bp.route('/api/history/<int:record_id>', methods=['GET'])
@login_required
def get_record(record_id):
    """Retrieve full detail for a single analysis record (for modal inspection)."""
    user_id = session['user_id']
    record = SentimentResult.query.filter_by(id=record_id, user_id=user_id).first()

    if not record:
        return jsonify({'success': False, 'error': 'Record not found'}), 404

    return jsonify({
        'success': True,
        'record': record.to_dict()
    })

@history_bp.route('/api/history/<int:record_id>/delete', methods=['POST', 'DELETE'])
@login_required
def delete_record(record_id):
    """Delete an individual analysis record belonging to the authenticated user."""
    user_id = session['user_id']
    record = SentimentResult.query.filter_by(id=record_id, user_id=user_id).first()

    if not record:
        return jsonify({'success': False, 'error': 'Record not found or access denied.'}), 404

    db.session.delete(record)
    db.session.commit()

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Analysis record deleted successfully.'})

    flash("Analysis record deleted successfully.", "success")
    return redirect(url_for('history.history'))

@history_bp.route('/history/clear', methods=['POST'])
@login_required
def clear_all():
    """Clear all analysis history for the current user."""
    user_id = session['user_id']
    deleted_count = SentimentResult.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    flash(f"Cleared {deleted_count} analysis record(s) from your history.", "info")
    return redirect(url_for('history.history'))

@history_bp.route('/history/export', methods=['GET'])
@login_required
def export_csv():
    """
    Generate and stream an actual CSV file containing the user's complete analysis history.
    Uses Pandas to structure and format tabular data.
    """
    user_id = session['user_id']
    records = SentimentResult.query.filter_by(user_id=user_id)\
        .order_by(SentimentResult.created_at.desc())\
        .all()

    if not records:
        flash("No analysis history available to export.", "warning")
        return redirect(url_for('history.history'))

    # Build DataFrame with Pandas
    data = []
    for r in records:
        data.append({
            'Analysis ID': r.id,
            'Timestamp (UTC)': r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else '',
            'Sentiment': r.sentiment,
            'Polarity': round(r.polarity, 4),
            'Polarity Display': r.polarity_display,
            'Subjectivity': round(r.subjectivity, 4),
            'Subjectivity Display': r.subjectivity_display,
            'Word Count': r.word_count,
            'Character Count': r.char_count,
            'Sentence Count': r.sentence_count,
            'Analyzed Text': r.text
        })

    df = pd.DataFrame(data)

    # Convert to CSV string buffer
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8')
    csv_bytes = output.getvalue().encode('utf-8')

    timestamp_str = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    filename = f"sentimentiq_analysis_history_{timestamp_str}.csv"

    return Response(
        csv_bytes,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )
