from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from database.database import db
from database.models import User, SentimentResult
from services.sentiment_service import SentimentService

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator ensuring routes are accessed only by authenticated users."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access your sentiment dashboard.", "warning")
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Retrieve User record corresponding to active session."""
    user_id = session.get('user_id')
    if user_id:
        return db.session.get(User, user_id)
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate user with username/email and password."""
    if 'user_id' in session:
        return redirect(url_for('sentiment.dashboard'))

    if request.method == 'POST':
        login_id = request.form.get('login_id', '').strip()
        password = request.form.get('password', '').strip()

        if not login_id or not password:
            flash("Please enter both username/email and password.", "danger")
            return render_template('login.html', login_id=login_id)

        # Allow login by username or email
        user = User.query.filter(
            (User.username == login_id) | (User.email == login_id.lower())
        ).first()

        if not user or not user.check_password(password):
            flash("Invalid credentials. Please verify your login details.", "danger")
            return render_template('login.html', login_id=login_id)

        # Set session state
        session['user_id'] = user.id
        session['username'] = user.username
        session['email'] = user.email

        flash(f"Welcome back, {user.username}!", "success")
        next_url = request.args.get('next') or url_for('sentiment.dashboard')
        return redirect(next_url)

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Create a new user account with data validation and demo seeds."""
    if 'user_id' in session:
        return redirect(url_for('sentiment.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not username or len(username) < 3:
            flash("Username must be at least 3 characters long.", "danger")
            return render_template('register.html', username=username, email=email)

        if not email or '@' not in email:
            flash("Please provide a valid email address.", "danger")
            return render_template('register.html', username=username, email=email)

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template('register.html', username=username, email=email)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html', username=username, email=email)

        # Check existing user
        if User.query.filter_by(username=username).first():
            flash("Username is already taken. Please choose another.", "danger")
            return render_template('register.html', username=username, email=email)

        if User.query.filter_by(email=email).first():
            flash("Email address is already registered.", "danger")
            return render_template('register.html', username=username, email=email)

        # Create user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Seed 3 initial analyses for rich out-of-the-box dashboard experience
        seed_samples = [
            "SentimentIQ delivers outstanding accuracy, an ultra-intuitive workspace, and crisp real-time sentiment telemetry. Truly an exceptional AI platform!",
            "System crashed three times during critical execution and latency spiked uncontrollably. Very disappointed with this unstable build.",
            "The standard protocol specification was released today at 14:00 UTC by the working committee. All documentation is archived in section 4."
        ]
        for sample in seed_samples:
            analysis = SentimentService.analyze(sample)
            record = SentimentResult(
                user_id=new_user.id,
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

        # Auto login
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session['email'] = new_user.email

        flash(f"Account created successfully! Welcome to SentimentIQ, {new_user.username}!", "success")
        return redirect(url_for('sentiment.dashboard'))

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """End active user session."""
    username = session.pop('username', None)
    session.pop('user_id', None)
    session.pop('email', None)
    flash(f"Signed out successfully. See you soon, {username or 'friend'}!", "info")
    return redirect(url_for('auth.login'))
