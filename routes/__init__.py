from routes.main import main_bp
from routes.auth import auth_bp
from routes.sentiment import sentiment_bp
from routes.history import history_bp
from routes.analytics import analytics_bp

__all__ = ['main_bp', 'auth_bp', 'sentiment_bp', 'history_bp', 'analytics_bp']
