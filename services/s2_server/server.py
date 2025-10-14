# services/s2_server/server.py
import os
import json
import sys
from flask import Flask, request, jsonify
from dotenv import load_dotenv, find_dotenv # Importe o find_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
import redis

# Carrega variáveis de ambiente do arquivo .env encontrado na raiz do projeto
load_dotenv(find_dotenv()) # Use find_dotenv() para localizar o arquivo .env

# --- Validação das variáveis de ambiente ---
REQUIRED_ENV_VARS = [
    "POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD",
    "MONGO_URI",
    "REDIS_HOST", "REDIS_PORT"
]

missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    print(f"Erro: As seguintes variáveis de ambiente não foram definidas: {', '.join(missing_vars)}")
    print("Por favor, verifique se o arquivo .env está correto e na raiz do projeto.")
    sys.exit(1)

# Inicializa o Flask
app = Flask(__name__)

# --- Conexões com os Bancos de Dados ---
try:
    # 1. PostgreSQL para Clientes (RDB)
    pg_conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    with pg_conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY, name TEXT, email TEXT
            );
        """)
    pg_conn.commit()
    pg_conn.close() # Feche a conexão inicial, a função get_pg_connection vai reabrir

    def get_pg_connection():
        return psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'), port=os.getenv('POSTGRES_PORT'),
            dbname=os.getenv('POSTGRES_DB'), user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )

    # 2. MongoDB para Livros (DB1 - Document Store)
    mongo_client = MongoClient(os.getenv('MONGO_URI'))
    mongo_client.server_info()
    mongo_db = mongo_client['books_db']
    books_collection = mongo_db['books']

    # 3. Redis para Pedidos (DB2 - Key-Value)
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')),
        decode_responses=True
    )
    redis_client.ping()

except Exception as e:
    print(f"\nERRO CRÍTICO AO CONECTAR COM OS BANCOS DE DADOS: {e}")
    print("Verifique se os contêineres do Docker estão rodando ('docker-compose up -d').\n")
    sys.exit(1)


# --- Endpoints da API ---
@app.route('/')
def index():
    return "Serviço S2 está no ar!"

# Endpoints de Clientes, Livros e Pedidos... (o restante do código permanece o mesmo)
# --- Clientes (PostgreSQL) ---
@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.json
    conn = get_pg_connection()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO customers (id, name, email) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING;",
            (data['id'], data['name'], data['email'])
        )
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": f"Cliente {data['id']} armazenado."}), 201

@app.route('/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    conn = get_pg_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM customers WHERE id = %s;", (customer_id,))
        customer = cur.fetchone()
    conn.close()
    if customer:
        return jsonify(customer)
    return jsonify({"status": "error", "message": "Cliente não encontrado."}), 404

# --- Livros (MongoDB) ---
@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    books_collection.update_one(
        {'id': data['id']},
        {'$set': data},
        upsert=True
    )
    return jsonify({"status": "success", "message": f"Livro {data['id']} armazenado."}), 201

@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    book = books_collection.find_one({'id': book_id}, {'_id': 0})
    if book:
        return jsonify(book)
    return jsonify({"status": "error", "message": "Livro não encontrado."}), 404

# --- Pedidos (Redis) ---
@app.route('/orders', methods=['POST'])
def add_order():
    data = request.json
    key = f"order:{data['id']}"
    redis_client.hset(key, mapping={
        'customer_id': data['customer_id'],
        'book_id': data['book_id'],
        'quantity': str(data['quantity']),
        'timestamp': str(data['timestamp'])
    })
    return jsonify({"status": "success", "message": f"Pedido {data['id']} armazenado."}), 201

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    key = f"order:{order_id}"
    order = redis_client.hgetall(key)
    if order:
        return jsonify(order)
    return jsonify({"status": "error", "message": "Pedido não encontrado."}), 404


if __name__ == '__main__':
    print("Servidor S2 iniciado com sucesso. Aguardando requisições...")
    app.run(host='0.0.0.0', port=5000, debug=True)