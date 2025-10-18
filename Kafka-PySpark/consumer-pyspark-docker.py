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

# --- Kafka configuration ---
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka1:19092")

print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}")
print(f"Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")

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
print("PostgreSQL table created/verified successfully")

# --- NLP preprocessing ---
print("Downloading NLTK data...")
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# --- Spark setup ---
print("Initializing Spark...")
spark = SparkSession.builder \
    .appName("classify tweets") \
    .getOrCreate()

# --- Load ML model ---
print("Loading ML model...")
model_path = "ML PySpark Model/logistic_regression_model.pkl"
if not os.path.exists(model_path):
    model_path = "logistic_regression_model.pkl"
    
pipeline = PipelineModel.load(model_path)
print("Model loaded successfully")

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
print("Starting Kafka consumer...")
consumer = KafkaConsumer(
    'numtest',
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)

print("Consumer started. Waiting for messages...")

# --- Main Loop ---
message_count = 0
for message in consumer:
    try:
        tweet = message.value[-1]
        preprocessed_tweet = clean_text(tweet)
        data = [(preprocessed_tweet,)]
        data = spark.createDataFrame(data, ["Text"])
        processed = pipeline.transform(data)
        prediction = processed.collect()[0][6]
        classname = class_index_mapping[int(prediction)]

        print(f"\n[Message {message_count}]")
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
        
        message_count += 1
        print("/" * 50)
        
    except Exception as e:
        print(f"Error processing message: {e}")
        continue

# Close DB connections (won't usually be reached in infinite loop)
cur.close()
conn.close()
