import json
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

consumer = KafkaConsumer(
    'customers','books','orders',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

with open('messages.log', 'a') as log_file:
    for msg in consumer:
        entry = {
            'topic': msg.topic,
            'message': msg.value,
            'timestamp': msg.timestamp
        }
        log_file.write(json.dumps(entry) + '\n')
        print(f"[S3] Logged message from {msg.topic}")