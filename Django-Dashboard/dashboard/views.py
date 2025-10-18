import os
import re
from collections import Counter

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from django.shortcuts import render
from pymongo import MongoClient

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import csv

# -----------------------------------------------------
# NLTK setup: download to project folder
# -----------------------------------------------------
NLTK_PATH = os.path.join(os.path.dirname(__file__), "nltk_data")
os.makedirs(NLTK_PATH, exist_ok=True)
nltk.data.path.append(NLTK_PATH)

def ensure_nltk_resources():
    # punkt tokenizer
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', download_dir=NLTK_PATH)
        nltk.download('wordnet')
        nltk.download('omw-1.4')
    
    # stopwords
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', download_dir=NLTK_PATH)

ensure_nltk_resources()

# -----------------------------------------------------
# Connect to MongoDB server
# -----------------------------------------------------
client = MongoClient('mongodb://localhost:27017/')
db = client['bigdata_project']

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
    keys_to_extract = ['tweet', 'prediction']
    result_tuples = [tuple(d[key] for key in keys_to_extract) for d in data]

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
    data = list(db.tweets.find())
    len_data = len(data)
    print("len_data : ", len_data)

    if len_data == 0:
        return render(request, 'dashboard/index.html', {'len_data': len_data})

    # Sentiment counts
    sentiment_counts = {label: 0 for label in class_list}
    for entry in data:
        sentiment_counts[entry['prediction']] += 1

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

            csv_path = "/home/acer/Documents/Big Data Project/Real-Time-Twitter-Sentiment-Analysis/Kafka-PySpark/twitter_validation.csv"
            fieldnames = ['Tweet ID', 'Tweet content', 'entity', 'sentiment']

            # === Always write Tweet ID = 1 ===
            tweet_id = 1

            # === Append to CSV ===
            file_exists = os.path.isfile(csv_path)
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()

                writer.writerow({
                    'Tweet ID': tweet_id,
                    'Tweet content': text,
                    'entity': "New Data",
                    'sentiment': prediction
                })

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


