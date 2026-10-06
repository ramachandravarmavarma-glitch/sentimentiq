import pytest
import sys
import os

# Add parent directory to path so tests can run from anywhere
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.sentiment_service import SentimentService

class TestSentimentService:
    """Unit tests for the TextBlob-powered SentimentService engine."""

    def test_positive_sentiment_detection(self):
        text = "I absolutely love this amazing product! It works wonderfully and brings pure joy."
        result = SentimentService.analyze(text)

        assert result['sentiment'] == 'POSITIVE'
        assert result['polarity'] > 0.10
        assert result['polarity_percent'] > 55.0
        assert result['word_count'] > 0
        assert 'sentences' in result
        assert len(result['sentences']) >= 1

    def test_negative_sentiment_detection(self):
        text = "This is a terrible, horrible, and dreadful failure. I hate this awful experience."
        result = SentimentService.analyze(text)

        assert result['sentiment'] == 'NEGATIVE'
        assert result['polarity'] < -0.10
        assert result['polarity_percent'] < 45.0
        assert result['word_count'] > 0

    def test_neutral_sentiment_detection(self):
        text = "The table is located in the middle of room 402."
        result = SentimentService.analyze(text)

        assert result['sentiment'] == 'NEUTRAL'
        assert -0.10 <= result['polarity'] <= 0.10

    def test_empty_string_rejection(self):
        with pytest.raises(ValueError):
            SentimentService.analyze("")

        with pytest.raises(ValueError):
            SentimentService.analyze("    \n\t  ")

    def test_subjectivity_computation(self):
        # Objective statement
        objective_text = "Water boils at 100 degrees Celsius under standard atmospheric pressure."
        obj_result = SentimentService.analyze(objective_text)
        assert 0.0 <= obj_result['subjectivity'] <= 0.30

        # Highly subjective statement
        subjective_text = "In my personal opinion, this is the most gorgeous, breathtaking aesthetic ever created."
        subj_result = SentimentService.analyze(subjective_text)
        assert subj_result['subjectivity'] > 0.50

    def test_gauge_percentage_bounds(self):
        pos = SentimentService.analyze("Super awesome fantastic outstanding brilliant marvelous!")
        assert 0.0 <= pos['polarity_percent'] <= 100.0
        assert 0.0 <= pos['subjectivity_percent'] <= 100.0

        neg = SentimentService.analyze("Worst disgusting disaster catastrophic tragic failure!")
        assert 0.0 <= neg['polarity_percent'] <= 100.0
        assert 0.0 <= neg['subjectivity_percent'] <= 100.0
