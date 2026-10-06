from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import db

class User(db.Model):
    """User account model for authentication and data isolation."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to user's private sentiment analysis records
    results = db.relationship(
        'SentimentResult',
        backref='user',
        cascade='all, delete-orphan',
        lazy='dynamic',
        order_by='desc(SentimentResult.created_at)'
    )

    def set_password(self, password: str) -> None:
        """Hash and store user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify user password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class SentimentResult(db.Model):
    """Sentiment analysis result records tied to individual users."""
    __tablename__ = 'sentiment_results'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False, index=True)  # POSITIVE, NEGATIVE, NEUTRAL
    polarity = db.Column(db.Float, nullable=False)                    # -1.0 to 1.0
    subjectivity = db.Column(db.Float, nullable=False)                # 0.0 to 1.0
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Metadata metrics
    word_count = db.Column(db.Integer, default=0)
    char_count = db.Column(db.Integer, default=0)
    sentence_count = db.Column(db.Integer, default=1)

    @property
    def polarity_display(self) -> str:
        """Format polarity with explicit sign (e.g. +0.82 or -0.45)."""
        return f"{self.polarity:+.2f}"

    @property
    def subjectivity_display(self) -> str:
        """Format subjectivity (e.g. 0.45)."""
        return f"{self.subjectivity:.2f}"

    @property
    def polarity_percent(self) -> float:
        """Map [-1.0, 1.0] onto [0, 100]% for gauge rendering."""
        return round(((self.polarity + 1.0) / 2.0) * 100, 2)

    @property
    def subjectivity_percent(self) -> float:
        """Map [0.0, 1.0] onto [0, 100]% for gauge rendering."""
        return round(self.subjectivity * 100, 2)

    @property
    def preview_text(self) -> str:
        """Short snippet for table display."""
        if len(self.text) > 90:
            return self.text[:90].strip() + '...'
        return self.text

    def to_dict(self) -> dict:
        """Serialize record to dictionary for API and chart responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'text': self.text,
            'preview': self.preview_text,
            'sentiment': self.sentiment,
            'polarity': round(self.polarity, 4),
            'polarity_display': self.polarity_display,
            'polarity_percent': self.polarity_percent,
            'subjectivity': round(self.subjectivity, 4),
            'subjectivity_display': self.subjectivity_display,
            'subjectivity_percent': self.subjectivity_percent,
            'word_count': self.word_count,
            'char_count': self.char_count,
            'sentence_count': self.sentence_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'date_formatted': self.created_at.strftime('%b %d, %Y - %I:%M %p') if self.created_at else None
        }

    def __repr__(self) -> str:
        return f"<SentimentResult {self.id}: {self.sentiment} ({self.polarity:+.2f})>"
