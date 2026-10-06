from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize database with the application context."""
    db.init_app(app)
    with app.app_context():
        # Import models so SQLAlchemy detects tables
        from database import models
        db.create_all()
