from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from database.database import db
from database.models import SentimentResult
from services.sentiment_service import SentimentService
from routes.auth import login_required, get_current_user

sentiment_bp = Blueprint('sentiment', __name__)

@sentiment_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Main Analytics Overview Dashboard.
    Pulls REAL user metrics directly from SQLite database:
    - Total analyses
    - Positive count
    - Negative count
    - Neutral count
    - Recent analyses
    """
    user_id = session['user_id']
    user = get_current_user()

    total_count = SentimentResult.query.filter_by(user_id=user_id).count()
    positive_count = SentimentResult.query.filter_by(user_id=user_id, sentiment='POSITIVE').count()
    negative_count = SentimentResult.query.filter_by(user_id=user_id, sentiment='NEGATIVE').count()
    neutral_count = SentimentResult.query.filter_by(user_id=user_id, sentiment='NEUTRAL').count()

    # Calculate percentages
    positive_pct = round((positive_count / total_count * 100), 1) if total_count > 0 else 0
    negative_pct = round((negative_count / total_count * 100), 1) if total_count > 0 else 0
    neutral_pct = round((neutral_count / total_count * 100), 1) if total_count > 0 else 0

    # Fetch recent analyses
    recent_analyses = SentimentResult.query.filter_by(user_id=user_id)\
        .order_by(SentimentResult.created_at.desc())\
        .limit(5)\
        .all()

    stats = {
        'total': total_count,
        'positive': positive_count,
        'negative': negative_count,
        'neutral': neutral_count,
        'positive_pct': positive_pct,
        'negative_pct': negative_pct,
        'neutral_pct': neutral_pct
    }

    return render_template(
        'dashboard.html',
        stats=stats,
        recent_analyses=recent_analyses,
        user=user
    )

@sentiment_bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    """Workspace page for typing, pasting, and analyzing text with instant feedback."""
    user_id = session['user_id']
    
    # Handle standard POST form submission if JS disabled
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        if not text:
            flash("Please provide text to analyze.", "warning")
            return redirect(url_for('sentiment.analyze'))

        try:
            analysis = SentimentService.analyze(text)
            new_record = SentimentResult(
                user_id=user_id,
                text=analysis['text'],
                sentiment=analysis['sentiment'],
                polarity=analysis['polarity'],
                subjectivity=analysis['subjectivity'],
                word_count=analysis['word_count'],
                char_count=analysis['char_count'],
                sentence_count=analysis['sentence_count']
            )
            db.session.add(new_record)
            db.session.commit()
            flash("Sentiment analysis completed.", "success")
            return render_template('analyze.html', result=analysis, record_id=new_record.id, input_text=text)
        except Exception as e:
            flash(f"Unable to analyze the text: {str(e)}", "danger")
            return render_template('analyze.html', input_text=text)

    return render_template('analyze.html')

@sentiment_bp.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    """
    Asynchronous AJAX API endpoint.
    Processes text with TextBlob, saves entry to SQLite database,
    and returns comprehensive response for instant dynamic rendering.
    """
    user_id = session['user_id']
    data = request.get_json(silent=True) or request.form

    text = data.get('text', '').strip() if data else ''
    if not text:
        return jsonify({
            'success': False,
            'error': 'Text cannot be empty. Please enter or paste some text.'
        }), 400

    try:
        # Run TextBlob sentiment calculation
        analysis = SentimentService.analyze(text)

        # Persist to database
        record = SentimentResult(
            user_id=user_id,
            text=analysis['text'],
            sentiment=analysis['sentiment'],
            polarity=analysis['polarity'],
            subjectivity=analysis['subjectivity'],
            word_count=analysis['word_count'],
            char_count=analysis['char_count'],
            sentence_count=analysis['sentence_count']
        )
        db.session.add(record)
        db.session.commit()

        # Add record metadata to payload
        analysis['id'] = record.id
        analysis['created_at'] = record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        analysis['date_formatted'] = record.created_at.strftime('%b %d, %Y - %I:%M %p')
        analysis['success'] = True
        analysis['message'] = 'Sentiment analysis completed.'

        return jsonify(analysis), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Unable to analyze the text: {str(e)}'
        }), 500
