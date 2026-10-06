import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database.database import db
from database.models import User, SentimentResult

@pytest.fixture
def app():
    """Create application in testing mode with in-memory database."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    """Helper client that registers and signs in a test user."""
    client.post('/register', data={
        'username': 'tester_user',
        'email': 'tester@example.com',
        'password': 'securepassword123',
        'confirm_password': 'securepassword123'
    }, follow_redirects=True)
    return client

class TestRoutes:
    """Integration test suite for Flask routes and data isolation."""

    def test_landing_page(self, client):
        response = client.get('/landing')
        assert response.status_code == 200
        assert b"Understand What Your Text" in response.data

    def test_documentation_page(self, client):
        response = client.get('/documentation')
        assert response.status_code == 200
        assert b"TextBlob" in response.data

    def test_user_registration_and_login(self, client):
        # Register new account
        res = client.post('/register', data={
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        assert res.status_code == 200
        assert b"Sentiment Overview" in res.data or b"Dashboard" in res.data

        # Logout
        res_logout = client.get('/logout', follow_redirects=True)
        assert res_logout.status_code == 200
        assert b"Signed out" in res_logout.data

        # Login again
        res_login = client.post('/login', data={
            'login_id': 'john_doe',
            'password': 'password123'
        }, follow_redirects=True)
        assert res_login.status_code == 200
        assert b"Welcome back" in res_login.data

    def test_analyzer_api_endpoint(self, auth_client):
        # Send text to analyze
        response = auth_client.post('/api/analyze', json={
            'text': 'The performance of this newly released feature is fantastic and remarkably fast.'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['sentiment'] == 'POSITIVE'
        assert data['polarity'] > 0.10
        assert 'id' in data

    def test_history_and_csv_export(self, auth_client):
        # View history page
        hist_res = auth_client.get('/history')
        assert hist_res.status_code == 200
        assert b"Analysis History" in hist_res.data

        # Export CSV (Real Pandas export)
        csv_res = auth_client.get('/history/export')
        assert csv_res.status_code == 200
        assert 'text/csv' in csv_res.headers.get('Content-Type', '')
        assert b"Analysis ID,Timestamp (UTC),Sentiment,Polarity" in csv_res.data

    def test_analytics_api(self, auth_client):
        # Fetch JSON analytics
        analytics_res = auth_client.get('/api/analytics-data')
        assert analytics_res.status_code == 200
        data = analytics_res.get_json()
        assert 'total' in data
        assert 'positive' in data
        assert 'negative' in data
        assert 'neutral' in data
        assert 'polarity_buckets' in data
        assert 'subjectivity_buckets' in data
        assert 'timeline' in data

    def test_data_isolation_between_users(self, app):
        client = app.test_client()

        # User 1 registers and analyzes a positive text
        client.post('/register', data={
            'username': 'user_one',
            'email': 'user1@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        client.post('/api/analyze', json={'text': 'Unique secret message from User One'})
        client.get('/logout')

        # User 2 registers
        client.post('/register', data={
            'username': 'user_two',
            'email': 'user2@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)

        # User 2 views history - should NOT see User 1's secret text
        user2_hist = client.get('/history')
        assert b"Unique secret message from User One" not in user2_hist.data
