import os
from datetime import datetime
from flask import Flask, render_template, session
from config import config_by_name
from database.database import init_db, db
from database.models import User

def create_app(config_name=None):
    """
    Application Factory for SENTIMENTIQ Flask Web Application.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Ensure database folder exists
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        db_file = db_uri.replace('sqlite:///', '')
        db_dir = os.path.dirname(os.path.abspath(db_file))
        os.makedirs(db_dir, exist_ok=True)

    # Initialize SQLAlchemy database & tables
    init_db(app)

    # Register Blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.sentiment import sentiment_bp
    from routes.history import history_bp
    from routes.analytics import analytics_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(sentiment_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(analytics_bp)

    # Global Context Processors
    @app.context_processor
    def inject_global_template_vars():
        current_user = None
        user_id = session.get('user_id')
        if user_id:
            current_user = db.session.get(User, user_id)
        
        return {
            'current_user': current_user,
            'app_name': app.config.get('APP_NAME', 'SENTIMENTIQ'),
            'app_tagline': app.config.get('APP_TAGLINE', 'AI-Powered Text Sentiment Intelligence'),
            'app_version': app.config.get('APP_VERSION', '2.1.0'),
            'internship_credit': app.config.get('INTERNSHIP_CREDIT', 'Project 2 | QSkill Python Development Internship'),
            'current_theme': session.get('theme', 'dark-charcoal'),
            'now_year': datetime.now().year
        }

    # Custom Error Pages
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', not_found=True), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', server_error=True), 500

    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='127.0.0.1', port=5000, debug=True)
