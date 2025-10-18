"""
Lightweight text classification module for Django dashboard.
Uses simple rule-based sentiment analysis without requiring Spark/Java.
For production ML inference, use the PySpark consumer service.
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data (if not already downloaded)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# Sentiment lexicons (simplified for demo purposes)
POSITIVE_WORDS = {
    'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'best',
    'awesome', 'perfect', 'beautiful', 'happy', 'joy', 'pleased', 'delighted', 'impressive',
    'outstanding', 'superb', 'brilliant', 'magnificent', 'terrific', 'marvelous', 'fabulous',
    'incredible', 'exceptional', 'remarkable', 'splendid', 'lovely', 'nice', 'enjoy',
    'liked', 'recommend', 'satisfied', 'positive', 'better', 'improved', 'excited'
}

NEGATIVE_WORDS = {
    'bad', 'terrible', 'horrible', 'awful', 'poor', 'worst', 'hate', 'disappointing',
    'disappointed', 'sad', 'angry', 'frustrated', 'annoying', 'annoyed', 'useless',
    'pathetic', 'disgusting', 'unacceptable', 'broken', 'failed', 'failure', 'problem',
    'issue', 'wrong', 'error', 'bug', 'crash', 'slow', 'waste', 'regret', 'never',
    'not recommend', 'avoid', 'dissatisfied', 'negative', 'worse', 'degraded'
}

NEUTRAL_INDICATORS = {
    'update', 'version', 'release', 'announced', 'report', 'news', 'information',
    'details', 'feature', 'available', 'launched', 'coming', 'planned', 'scheduled',
    'expected', 'according', 'stated', 'said', 'confirmed', 'official'
}

def clean_text(text):
    """Clean and preprocess text for sentiment analysis."""
    if text is not None:
        # Remove links starting with https://, http://, www., or containing .com
        text = re.sub(r'https?://\S+|www\.\S+|\S+\.com\S+|youtu\.be/\S+', '', text)
        
        # Remove words starting with # or @
        text = re.sub(r'(@|#)\w+', '', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove non-alphabetic characters
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    else:
        return ''


def classify_text(text: str) -> str:
    """
    Classify text sentiment using rule-based approach.
    
    This is a lightweight classification for the Django dashboard.
    For production ML inference, tweets are processed by the PySpark consumer service.
    
    Args:
        text: Input text to classify
        
    Returns:
        Sentiment classification: "Positive", "Negative", "Neutral", or "Irrelevant"
    """
    # Preprocess the text
    cleaned_text = clean_text(text)
    
    # Check if text is too short or empty
    if len(cleaned_text) < 3:
        return "Irrelevant"
    
    # Tokenize and remove stopwords
    try:
        tokens = word_tokenize(cleaned_text)
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    except Exception as e:
        print(f"Tokenization error: {e}")
        tokens = cleaned_text.split()
    
    # Check for irrelevant content (very short after preprocessing)
    if len(tokens) < 2:
        return "Irrelevant"
    
    # Calculate sentiment scores
    positive_score = sum(1 for word in tokens if word in POSITIVE_WORDS)
    negative_score = sum(1 for word in tokens if word in NEGATIVE_WORDS)
    neutral_score = sum(1 for word in tokens if word in NEUTRAL_INDICATORS)
    
    # Handle negations (simple approach)
    text_lower = cleaned_text.lower()
    has_negation = any(neg in text_lower for neg in ['not', 'no', 'never', 'dont', "don't", 'wont', "won't", 'cannot', 'cant', "can't"])
    
    if has_negation:
        # Flip positive and negative scores if negation is present
        positive_score, negative_score = negative_score, positive_score
    
    # Classification logic
    total_sentiment = positive_score + negative_score
    
    # If strong neutral indicators, classify as neutral
    if neutral_score >= 2 and total_sentiment <= 1:
        return "Neutral"
    
    # If no sentiment words found, classify as neutral
    if total_sentiment == 0:
        return "Neutral"
    
    # Compare positive vs negative scores
    if positive_score > negative_score:
        return "Positive"
    elif negative_score > positive_score:
        return "Negative"
    else:
        # Tie or equal - classify as neutral
        return "Neutral"


# For debugging - print classification details
def classify_text_detailed(text: str) -> dict:
    """
    Detailed classification with score breakdown.
    Used for debugging and understanding classification decisions.
    """
    cleaned_text = clean_text(text)
    
    try:
        tokens = word_tokenize(cleaned_text)
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    except:
        tokens = cleaned_text.split()
    
    positive_score = sum(1 for word in tokens if word in POSITIVE_WORDS)
    negative_score = sum(1 for word in tokens if word in NEGATIVE_WORDS)
    neutral_score = sum(1 for word in tokens if word in NEUTRAL_INDICATORS)
    
    sentiment = classify_text(text)
    
    return {
        'original_text': text,
        'cleaned_text': cleaned_text,
        'tokens': tokens,
        'positive_score': positive_score,
        'negative_score': negative_score,
        'neutral_score': neutral_score,
        'sentiment': sentiment
    }
