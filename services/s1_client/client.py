# services/s1_client/client.py
import os
import time
import json
import requests
from faker import Faker
from dotenv import load_dotenv
import logging

# Configuração do Logger
logging.basicConfig(
    filename='s1_log.json',
    level=logging.INFO,
    format='%(message)s'
)

# Carrega variáveis de ambiente
load_dotenv()
API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')
S2_URL = "http://localhost:5000"

faker = Faker()

# Listas para manter o controle dos IDs criados
customers = []
books = []
orders = []

def log_request(method, url, payload, response):
    """Salva a requisição e a resposta em um arquivo de log JSON."""
    log_entry = {
        "timestamp": time.time(),
        "request": {
            "method": method,
            "url": url,
            "payload": payload
        },
        "response": {
            "status_code": response.status_code,
            "body": response.json() if response.content else None
        }
    }
    logging.info(json.dumps(log_entry))

def create_customer():
    """Gera e envia um novo cliente para S2."""
    customer_data = {
        'id': faker.uuid4(),
        'name': faker.name(),
        'email': faker.email(domain='example.com')
    }
    try:
        response = requests.post(f"{S2_URL}/customers", json=customer_data)
        response.raise_for_status() # Lança erro para status HTTP 4xx/5xx
        print(f"[S1] Cliente enviado: {customer_data['id']}")
        customers.append(customer_data)
        log_request('POST', f"{S2_URL}/customers", customer_data, response)
    except requests.exceptions.RequestException as e:
        print(f"[S1] Erro ao enviar cliente: {e}")
        log_request('POST', f"{S2_URL}/customers", customer_data, e.response if hasattr(e, 'response') else None)


def fetch_and_send_book():
    """Busca um livro na API do Google e envia para S2."""
    try:
        query = faker.word()
        google_api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={API_KEY}"
        resp = requests.get(google_api_url).json()
        item = resp.get('items', [{}])[0]
        if not item:
            print("[S1] Nenhum livro encontrado na API do Google.")
            return

        vol = item.get('volumeInfo', {})
        identifiers = vol.get('industryIdentifiers', [])
        isbn = next((i['identifier'] for i in identifiers if 'ISBN' in i.get('type', '')), None)

        book_data = {
            'id': item.get('id', faker.uuid4()), # ID do Google ou um UUID
            'isbn': isbn,
            'title': vol.get('title'),
            'authors': vol.get('authors'),
            'publishedDate': vol.get('publishedDate')
        }
        
        response = requests.post(f"{S2_URL}/books", json=book_data)
        response.raise_for_status()
        print(f"[S1] Livro enviado: {book_data['id']} - {book_data['title']}")
        books.append(book_data)
        log_request('POST', f"{S2_URL}/books", book_data, response)
        
    except requests.exceptions.RequestException as e:
        print(f"[S1] Erro ao buscar ou enviar livro: {e}")
        log_request('POST', f"{S2_URL}/books", book_data if 'book_data' in locals() else {}, e.response if hasattr(e, 'response') else None)

def create_order():
    """Gera e envia um novo pedido para S2."""
    if not customers or not books:
        print("[S1] Aguardando clientes e livros para criar um pedido.")
        return

    cust = faker.random_element(customers)
    book = faker.random_element(books)
    order_data = {
        'id': faker.uuid4(),
        'customer_id': cust['id'],
        'book_id': book['id'],
        'quantity': faker.random_int(1, 5),
        'timestamp': time.time()
    }
    
    try:
        response = requests.post(f"{S2_URL}/orders", json=order_data)
        response.raise_for_status()
        print(f"[S1] Pedido enviado: {order_data['id']}")
        orders.append(order_data)
        log_request('POST', f"{S2_URL}/orders", order_data, response)
    except requests.exceptions.RequestException as e:
        print(f"[S1] Erro ao enviar pedido: {e}")
        log_request('POST', f"{S2_URL}/orders", order_data, e.response if hasattr(e, 'response') else None)

if __name__ == '__main__':
    print("Aguardando o serviço S2 iniciar...")
    time.sleep(5) # Pausa para dar tempo do servidor S2 iniciar
    
    while True:
        print("\n--- Novo ciclo de requisições ---")
        create_customer()
        time.sleep(2)
        fetch_and_send_book()
        time.sleep(2)
        create_order()
        time.sleep(10)