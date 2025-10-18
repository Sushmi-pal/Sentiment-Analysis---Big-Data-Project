from pyspark.ml import PipelineModel
import re
import nltk
from kafka import KafkaConsumer
from json import loads
import psycopg2
import os
from pyspark.sql import SparkSession

# --- PostgreSQL connection setup ---
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "bigdata_project")
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cur = conn.cursor()

# Create table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS tweets (
    id SERIAL PRIMARY KEY,
    tweet TEXT,
    preprocessed_tweet TEXT,
    predicted_sentiment FLOAT,
    sentiment_classname TEXT
)
""")
conn.commit()

# --- NLP preprocessing ---
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# --- Spark setup ---
spark = SparkSession.builder \
    .appName("classify tweets") \
    .getOrCreate()

# --- Load ML model ---
pipeline = PipelineModel.load("logistic_regression_model.pkl")

# --- Text cleaning function ---
def clean_text(text):
    if text:
        text = re.sub(r'https?://\S+|www\.\S+|\.com\S+|youtu\.be/\S+', '', text)
        text = re.sub(r'(@|#)\w+', '', text)
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    return ''

class_index_mapping = {0: "Negative", 1: "Positive", 2: "Neutral", 3: "Irrelevant"}

# --- Kafka Consumer ---
consumer = KafkaConsumer(
    'numtest',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)

# --- Main Loop ---
for message in consumer:
    tweet = message.value[-1]
    preprocessed_tweet = clean_text(tweet)
    data = [(preprocessed_tweet,)]
    data = spark.createDataFrame(data, ["Text"])
    processed = pipeline.transform(data)
    prediction = processed.collect()[0][6]
    classname = class_index_mapping[int(prediction)]

    print("-> Tweet:", tweet)
    print("-> Preprocessed:", preprocessed_tweet)
    print("-> Predicted Sentiment:", prediction)
    print("-> Sentiment Class:", classname)

    # Insert into PostgreSQL
    cur.execute(
        """
        INSERT INTO tweets (tweet, preprocessed_tweet, predicted_sentiment, sentiment_classname)
        VALUES (%s, %s, %s, %s)
        """,
        (tweet, preprocessed_tweet, float(prediction), classname)
    )
    conn.commit()

    print("/" * 50)

# Close DB connections (won’t usually be reached in infinite loop)
cur.close()
conn.close()
