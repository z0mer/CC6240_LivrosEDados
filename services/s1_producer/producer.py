import os
import time
import json
import requests
from kafka import KafkaProducer
from faker import Faker
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

faker = Faker()
customers = []
books = []

def create_customer():
    cust = {
        'id': faker.uuid4(),
        'name': faker.name(),
        'email': faker.email()
    }
    customers.append(cust)
    producer.send('customers', cust)
    print(f"[S1] Sent customer: {cust}")


def fetch_book():
    query = faker.word()
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={API_KEY}"
    resp = requests.get(url).json()
    item = resp.get('items', [None])[0]
    if not item:
        return
    vol = item['volumeInfo']
    book = {
        'id': item['id'],
        'title': vol.get('title'),
        'authors': vol.get('authors'),
        'publishedDate': vol.get('publishedDate')
    }
    books.append(book)
    producer.send('books', book)
    print(f"[S1] Sent book: {book}")


def create_order():
    if not customers or not books:
        return
    cust = faker.random_element(customers)
    bk = faker.random_element(books)
    order = {
        'id': faker.uuid4(),
        'customer_id': cust['id'],
        'book_id': bk['id'],
        'quantity': faker.random_int(1, 5),
        'timestamp': time.time()
    }
    producer.send('orders', order)
    print(f"[S1] Sent order: {order}")


if __name__ == '__main__':
    while True:
        create_customer()
        time.sleep(1)
        fetch_book()
        time.sleep(1)
        create_order()
        time.sleep(5)