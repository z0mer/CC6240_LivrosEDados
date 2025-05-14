import os
import json
from kafka import KafkaConsumer
from dotenv import load_dotenv
import psycopg2
from pymongo import MongoClient
import redis           # import do Redis

load_dotenv()

# Conexões
pg = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    dbname=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)
cursor = pg.cursor()

mongo = MongoClient(os.getenv('MONGO_URI'))
mdb = mongo['books_db']

# Conexão Redis para orders
r = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    decode_responses=True
)

consumer = KafkaConsumer(
    'customers', 'books', 'orders',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for msg in consumer:
    topic = msg.topic
    data = msg.value

    if topic == 'customers':
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id text PRIMARY KEY,
                name text,
                email text
            );
        """)
        cursor.execute(
            "INSERT INTO customers (id,name,email) VALUES (%s,%s,%s) "
            "ON CONFLICT (id) DO NOTHING;",
            (data['id'], data['name'], data['email'])
        )
        pg.commit()
        print(f"[S2] Stored customer {data['id']}")

    elif topic == 'books':
        mdb['books'].insert_one(data)
        print(f"[S2] Stored book {data['id']}")

    elif topic == 'orders':
        # Armazena cada order no Redis como hash: key = order:<id>
        key = f"order:{data['id']}"
        r.hset(key, mapping={
            'customer_id': data['customer_id'],
            'book_id':     data['book_id'],
            'quantity':    data['quantity'],
            'timestamp':   data['timestamp']
        })
        print(f"[S2] Stored order {data['id']} in Redis")
