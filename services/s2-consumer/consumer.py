import time
import json
from kafka import KafkaConsumer
from sqlalchemy import create_engine, text
from pymongo import MongoClient
from cassandra.cluster import Cluster

# --- Conexões iniciais (Postgres e MongoDB) ---
pg_engine    = create_engine('postgresql://postgres:postgres@postgres:5432/livraria')
mongo_client = MongoClient('mongodb://mongo:27017/')

# --- Função de retry para Cassandra ---
def make_cassandra_session():
    while True:
        try:
            cluster = Cluster(['cassandra'])
            session = cluster.connect('livraria')
            print("🔌 Cassandra conectada!")
            return cluster, session
        except Exception as e:
            print("⚠️ Cassandra não pronta, retry em 5s…", e)
            time.sleep(5)

cs_cluster, cs_session = make_cassandra_session()

# --- Kafka Consumer ---
consumer = KafkaConsumer(
    'clientes.create', 'livros.create', 'pedidos.create',
    bootstrap_servers='kafka:9092',
    group_id='s2-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("🚀 S2-Consumer iniciado e aguardando mensagens…")

# --- Funções de gravação ---
def gravar_em_postgres(payload):
    with pg_engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO clientes (id,nome,email) VALUES (:id,:nome,:email) "
                "ON CONFLICT (id) DO UPDATE SET nome=:nome,email=:email"
            ),
            payload
        )

def gravar_em_mongodb(payload):
    db = mongo_client.livraria
    db.livros.update_one(
        {"isbn": payload["isbn"]},
        {"$set": payload},
        upsert=True
    )

def gravar_em_cassandra(payload):
    cs_session.execute(
        """
        INSERT INTO pedidos (
            pedido_id,
            cliente_id,
            livros,
            valor_total,
            data_compra,
            status
        ) VALUES (
            uuid(),
            :cliente_id,
            :livros,
            :valor_total,
            toTimestamp(now()),
            :status
        )
        """,
        {
            "cliente_id": payload["cliente_id"],
            "livros": payload["livros"],
            "valor_total": payload["valor_total"],
            "status": payload["status"]
        }
    )

# --- Loop de consumo ---
for msg in consumer:
    topic   = msg.topic
    payload = msg.value["payload"]
    print(f"Recebido em {topic}: {payload}")

    if topic.startswith("clientes"):
        gravar_em_postgres(payload)
    elif topic.startswith("livros"):
        gravar_em_mongodb(payload)
    elif topic.startswith("pedidos"):
        gravar_em_cassandra(payload)
