import os
import sqlite3
from flask import Blueprint, render_template, redirect, url_for, session, request, flash, current_app
from database.database import db
from database.models import User, SentimentResult
from routes.auth import login_required, get_current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Root endpoint: route authenticated users to dashboard, visitors to landing page."""
    if 'user_id' in session:
        return redirect(url_for('sentiment.dashboard'))
    return render_template('landing.html')

@main_bp.route('/landing')
def landing():
    """Public promotional landing page."""
    return render_template('landing.html')

@main_bp.route('/documentation')
def documentation():
    """
    Comprehensive technical and user documentation detailing:
    - What is Sentiment Analysis
    - TextBlob Architecture
    - Polarity and Subjectivity mathematics
    - Classification thresholds
    - Project Architecture, Database schema, and Run guide
    """
    return render_template('documentation.html')

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User account settings, theme preferences, and database diagnostic telemetry."""
    user = get_current_user()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            email = request.form.get('email', '').strip().lower()
            if email and '@' in email:
                existing = User.query.filter(User.email == email, User.id != user.id).first()
                if existing:
                    flash("Email address is already in use by another account.", "danger")
                else:
                    user.email = email
                    db.session.commit()
                    session['email'] = email
                    flash("Profile information updated successfully.", "success")
            else:
                flash("Please provide a valid email address.", "danger")
                
        elif action == 'save_preferences':
            theme = request.form.get('theme', 'dark-charcoal')
            session['theme'] = theme
            flash("UI preferences saved successfully.", "success")
            
        return redirect(url_for('main.settings'))

    # Fetch database diagnostics
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    db_size_kb = 0
    if os.path.exists(db_path):
        db_size_kb = round(os.path.getsize(db_path) / 1024, 2)

    total_system_records = SentimentResult.query.count()
    user_record_count = SentimentResult.query.filter_by(user_id=user.id).count()

    db_status = {
        'engine': 'SQLite 3 (via SQLAlchemy)',
        'path': db_path,
        'size_kb': db_size_kb,
        'sqlite_version': sqlite3.sqlite_version,
        'connected': True,
        'total_system_records': total_system_records,
        'user_records': user_record_count
    }

    return render_template('settings.html', user=user, db_status=db_status)
