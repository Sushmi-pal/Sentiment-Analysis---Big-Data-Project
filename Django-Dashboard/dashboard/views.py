import os
import re
from collections import Counter

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from django.shortcuts import render
import psycopg2
from psycopg2.extras import RealDictCursor

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# -----------------------------------------------------
# NLTK setup: download to project folder
# -----------------------------------------------------
NLTK_PATH = os.path.join(os.path.dirname(__file__), "nltk_data")
os.makedirs(NLTK_PATH, exist_ok=True)
nltk.data.path.append(NLTK_PATH)

def ensure_nltk_resources():
    """Download required NLTK data"""
    resources = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']
    for resource in resources:
        try:
            if resource in ['punkt', 'punkt_tab']:
                nltk.data.find(f'tokenizers/{resource}')
            elif resource == 'stopwords':
                nltk.data.find('corpora/stopwords')
            else:
                nltk.data.find(f'corpora/{resource}')
        except LookupError:
            try:
                print(f"Downloading NLTK resource: {resource}")
                nltk.download(resource, download_dir=NLTK_PATH, quiet=True)
            except Exception as e:
                print(f"Failed to download {resource}: {e}")
                # Try without download_dir for system-wide install
                try:
                    nltk.download(resource, quiet=True)
                except:
                    pass

ensure_nltk_resources()

# -----------------------------------------------------
# Connect to PostgreSQL server
# -----------------------------------------------------
def get_db_connection():
    """Get PostgreSQL database connection"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'bigdata_project'),
        user=os.getenv('POSTGRES_USER', 'admin'),
        password=os.getenv('POSTGRES_PASSWORD', 'admin')
    )

# -----------------------------------------------------
# Text cleaning and preprocessing
# -----------------------------------------------------
def clean_text(text):
    text = re.sub(r'http[s]?://\S+', '', text)  # Remove URLs
    text = re.sub(r'\b@\w+\b', '', text)        # Remove mentions
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text) # Remove special chars
    return text.lower().strip()

def preprocess_text(text):
    text = clean_text(text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t not in stop_words]
    return tokens

# -----------------------------------------------------
# Classes and plotting
# -----------------------------------------------------
class_list = ['Negative', 'Positive', 'Neutral', 'Irrelevant']

def plot_word_frequencies_per_class(data):
    keys_to_extract = ['tweet', 'sentiment_classname']
    result_tuples = [(d['tweet'], d['sentiment_classname']) for d in data]

    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'BigDataProject', 'static', 'imgs')
    os.makedirs(static_folder, exist_ok=True)  # Ensure folder exists

    all_words_per_class = {class_label: [] for class_label in class_list}
    color_map = {'Negative': 'red', 'Positive': 'blue', 'Neutral': 'green', 'Irrelevant': 'purple'}

    plt.figure(figsize=(12, 8))

    # Preprocess tweets and collect words per class
    for tweet, prediction in result_tuples:
        class_texts = all_words_per_class[prediction]
        class_texts.extend(preprocess_text(tweet))

    # Plot top 5 words per class
    for class_label, class_words in all_words_per_class.items():
        word_freq = Counter(class_words)
        top_words = dict(word_freq.most_common(5))
        df = pd.DataFrame(list(top_words.items()), columns=['Word', 'Frequency'])
        plt.bar(df['Word'] + f' ({class_label})', df['Frequency'], 
                color=color_map[class_label], alpha=0.7, label=class_label)

    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.xticks(rotation=70)
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(static_folder, 'Word_Frequencies_for_all_classes.png')
    plt.savefig(plot_path)
    plt.close()

# -----------------------------------------------------
# Django views
# -----------------------------------------------------
def dashboard(request):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Fetch all tweets from PostgreSQL
    cur.execute("SELECT id, tweet, preprocessed_tweet, predicted_sentiment, sentiment_classname FROM tweets ORDER BY id DESC")
    data = cur.fetchall()
    
    cur.close()
    conn.close()
    
    len_data = len(data)
    print("len_data : ", len_data)

    if len_data == 0:
        return render(request, 'dashboard/index.html', {'len_data': len_data})

    # Sentiment counts
    sentiment_counts = {label: 0 for label in class_list}
    for entry in data:
        sentiment_counts[entry['sentiment_classname']] += 1

    # Sentiment rates (%)
    sentiment_rates = {label: round((count / len_data) * 100, 2) for label, count in sentiment_counts.items()}

    # Generate word frequency plot
    plot_word_frequencies_per_class(data)

    context = {
        'data': data,
        'len_data': len_data,
        'sentiment_counts': sentiment_counts,
        'sentiment_rates': sentiment_rates,
    }
    return render(request, 'dashboard/index.html', context)

def classify(request):
    error = False
    error_text = ""
    prediction = ""
    text = ""

    if request.method == 'POST':
        text = request.POST.get('text', "").strip()
        if len(text) > 0:
            from .consumer_user import classify_text
            prediction = classify_text(text)
        else:
            error = True
            error_text = "The text is empty! Please enter your text."

    context = {
        'error': error,
        'error_text': error_text,
        'prediction': prediction,
        'text': text,
        'text_len': len(text),
    }
    return render(request, 'dashboard/classify.html', context)
