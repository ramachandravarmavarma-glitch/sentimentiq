import re
from typing import Dict, Any, List
from textblob import TextBlob

class SentimentService:
    """
    Core Sentiment Intelligence engine utilizing TextBlob NLP.
    
    Threshold Definitions:
    - Polarity:
        > +0.10  -> POSITIVE
        < -0.10  -> NEGATIVE
        [-0.10, +0.10] -> NEUTRAL
        
    - Subjectivity:
        0.00 - 0.20 -> Highly Objective (Factual)
        0.21 - 0.40 -> Moderately Objective
        0.41 - 0.60 -> Balanced (Mix of Facts & Opinion)
        0.61 - 0.80 -> Moderately Subjective
        0.81 - 1.00 -> Highly Subjective (Personal Opinion)
    """

    POLARITY_POS_THRESHOLD = 0.10
    POLARITY_NEG_THRESHOLD = -0.10

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        """
        Analyze input text for sentiment polarity and subjectivity.
        
        Args:
            text (str): Raw input text to evaluate.
            
        Returns:
            dict: Detailed metrics including classification, numerical scores,
                  gauge percentages, and sentence-level breakdown.
        """
        if not text or not isinstance(text, str) or not text.strip():
            raise ValueError("Input text cannot be empty or purely whitespace.")

        clean_text = text.strip()
        blob = TextBlob(clean_text)

        # Compute raw TextBlob metrics
        polarity_raw = float(blob.sentiment.polarity)
        subjectivity_raw = float(blob.sentiment.subjectivity)

        # Enforce clean mathematical rounding
        polarity = round(polarity_raw, 4)
        subjectivity = round(subjectivity_raw, 4)

        # Classification based on documented thresholds
        if polarity > cls.POLARITY_POS_THRESHOLD:
            sentiment = "POSITIVE"
            sentiment_class = "success"
            sentiment_desc = "The tone of this text is positive, expressing satisfaction, optimism, or approval."
        elif polarity < cls.POLARITY_NEG_THRESHOLD:
            sentiment = "NEGATIVE"
            sentiment_class = "danger"
            sentiment_desc = "The tone of this text is negative, expressing dissatisfaction, criticism, or distress."
        else:
            sentiment = "NEUTRAL"
            sentiment_class = "warning"
            sentiment_desc = "The tone of this text is neutral, factual, balanced, or devoid of strong emotional bias."

        # Polarity nuance category
        if polarity >= 0.50:
            polarity_nuance = "Strongly Positive"
        elif polarity > cls.POLARITY_POS_THRESHOLD:
            polarity_nuance = "Moderately Positive"
        elif polarity <= -0.50:
            polarity_nuance = "Strongly Negative"
        elif polarity < cls.POLARITY_NEG_THRESHOLD:
            polarity_nuance = "Moderately Negative"
        else:
            polarity_nuance = "Neutral / Balanced"

        # Subjectivity nuance category
        if subjectivity <= 0.20:
            subjectivity_nuance = "Highly Objective (Factual)"
            subjectivity_desc = "Predominantly objective information, factual reporting, or unopinionated data."
        elif subjectivity <= 0.40:
            subjectivity_nuance = "Moderately Objective"
            subjectivity_desc = "Mostly factual statements with light interpretive phrasing."
        elif subjectivity <= 0.60:
            subjectivity_nuance = "Balanced"
            subjectivity_desc = "Equally blended balance of objective facts and subjective perspectives."
        elif subjectivity <= 0.80:
            subjectivity_nuance = "Moderately Subjective"
            subjectivity_desc = "Noticeable personal opinion, emotional appraisal, or subjective experience."
        else:
            subjectivity_nuance = "Highly Subjective"
            subjectivity_desc = "Intensely personal viewpoint, judgment, emotional reaction, or opinion."

        # Compute visual gauge positions [0 - 100]%
        # Polarity: maps [-1.0, 1.0] to [0%, 100%]
        # -1.0 -> 0%, 0.0 -> 50%, +1.0 -> 100%
        polarity_percent = round(((polarity + 1.0) / 2.0) * 100, 2)
        polarity_percent = max(0.0, min(100.0, polarity_percent))

        # Subjectivity: maps [0.0, 1.0] to [0%, 100%]
        subjectivity_percent = round(subjectivity * 100, 2)
        subjectivity_percent = max(0.0, min(100.0, subjectivity_percent))

        # Text counts and stats
        words = re.findall(r'\b\w+\b', clean_text)
        word_count = len(words)
        char_count = len(clean_text)
        
        # Sentence segmentation
        sentences_raw = [s.strip() for s in re.split(r'[.!?]+', clean_text) if s.strip()]
        sentence_count = max(1, len(sentences_raw))

        # Sentence-by-sentence breakdown (up to first 8 for detailed inspect)
        sentence_breakdown: List[Dict[str, Any]] = []
        for s_text in sentences_raw[:8]:
            s_blob = TextBlob(s_text)
            s_pol = round(float(s_blob.sentiment.polarity), 2)
            s_sub = round(float(s_blob.sentiment.subjectivity), 2)
            if s_pol > cls.POLARITY_POS_THRESHOLD:
                s_sent = "POSITIVE"
            elif s_pol < cls.POLARITY_NEG_THRESHOLD:
                s_sent = "NEGATIVE"
            else:
                s_sent = "NEUTRAL"

            sentence_breakdown.append({
                'sentence': s_text,
                'polarity': s_pol,
                'polarity_display': f"{s_pol:+.2f}",
                'subjectivity': s_sub,
                'sentiment': s_sent
            })

        return {
            'text': clean_text,
            'sentiment': sentiment,
            'sentiment_class': sentiment_class,
            'sentiment_desc': sentiment_desc,
            'polarity': polarity,
            'polarity_display': f"{polarity:+.2f}",
            'polarity_nuance': polarity_nuance,
            'polarity_percent': polarity_percent,
            'subjectivity': subjectivity,
            'subjectivity_display': f"{subjectivity:.2f}",
            'subjectivity_nuance': subjectivity_nuance,
            'subjectivity_desc': subjectivity_desc,
            'subjectivity_percent': subjectivity_percent,
            'word_count': word_count,
            'char_count': char_count,
            'sentence_count': sentence_count,
            'sentences': sentence_breakdown,
            'thresholds': {
                'positive_min': cls.POLARITY_POS_THRESHOLD,
                'negative_max': cls.POLARITY_NEG_THRESHOLD
            }
        }
