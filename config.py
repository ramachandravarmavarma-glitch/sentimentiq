import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base application configuration for SENTIMENTIQ."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sentimentiq-super-secret-key-qskill-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(BASE_DIR, 'database', 'sentimentiq.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # TextBlob Classification Thresholds
    # Polarity range: [-1.0, 1.0]
    # - Polarity > 0.10: POSITIVE
    # - Polarity < -0.10: NEGATIVE
    # - -0.10 <= Polarity <= 0.10: NEUTRAL
    POLARITY_POSITIVE_THRESHOLD = 0.10
    POLARITY_NEGATIVE_THRESHOLD = -0.10
    
    # Application branding
    APP_NAME = "SENTIMENTIQ"
    APP_TAGLINE = "AI-Powered Text Sentiment Intelligence"
    APP_VERSION = "2.1.0"
    INTERNSHIP_CREDIT = "Project 2 | QSkill Python Development Internship"
    
    # Pagination
    ITEMS_PER_PAGE = 10

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
