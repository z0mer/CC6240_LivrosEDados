import time
import json
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

def make_producer():
    while True:
        try:
            p = KafkaProducer(
                bootstrap_servers='kafka:9092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            # testar conexão simples
            p.bootstrap_connected()
            return p
        except NoBrokersAvailable:
            print("Kafka não disponível. Tentando de novo em 5s...")
            time.sleep(5)

def send_test_message(producer):
    msg = {
        "entity": "cliente",
        "action": "create",
        "payload": {
            "id": 1,
            "nome": "Ana Silva",
            "email": "ana.silva@example.com"
        }
    }
    producer.send('clientes.create', msg)
    producer.flush()
    print("Mensagem enviada:", msg)

if __name__ == "__main__":
    producer = make_producer()
    send_test_message(producer)
