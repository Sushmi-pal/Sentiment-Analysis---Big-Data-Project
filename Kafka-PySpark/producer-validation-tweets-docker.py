from time import sleep
import csv 
from kafka import KafkaProducer
import json
import os

# Get Kafka bootstrap servers from environment variable
kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka1:19092')

print(f"Connecting to Kafka at {kafka_bootstrap_servers}")

producer = KafkaProducer(bootstrap_servers=[kafka_bootstrap_servers],
                         value_serializer=lambda x: 
                         json.dumps(x).encode('utf-8'),
                         max_block_ms=10000,
                         request_timeout_ms=30000)

print(f"Connected to Kafka at {kafka_bootstrap_servers}")
print("Starting to send tweets...")

with open('twitter_validation.csv') as file_obj:
    reader_obj = csv.reader(file_obj)
    for idx, data in enumerate(reader_obj): 
        producer.send('numtest', value=data)
        if idx % 10 == 0:
            print(f"Sent {idx} tweets...")
        sleep(3)

print("Finished sending all tweets!")
