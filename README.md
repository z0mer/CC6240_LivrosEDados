# 📚 Projeto Livros & Dados – Polyglot Persistence

Este projeto implementa uma **livraria online** usando o padrão **Polyglot Persistence** e arquitetura **Pub/Sub** com Apache Kafka. Três serviços (S1, S2 e S3) trocam mensagens via Kafka e armazenam dados em diferentes bancos, de acordo com o uso de cada informação.



## 🧩 Como Funciona

1. **S1 – Produtor**
    - Gera dados fictícios de **Clientes** (via Faker), **Livros** (via API Google Books) e **Pedidos**.
        
        > **Nota:** os e-mails e demais dados gerados pelo Faker são fictícios e usam domínios reservados (`@example.com`, `@example.org` e `@example.net`) para evitar uso de informações reais.
        > 
    - Publica mensagens nos tópicos Kafka:
        - `customers` (clientes)
        - `books` (livros)
        - `orders` (pedidos)
2. **Kafka (Mensageria)**
    - Apache Kafka + Zookeeper garantem o fluxo assíncrono de mensagens.
3. **S2 – Consumer & Armazenamento**
    - Lê os três tópicos do Kafka e persiste:
        - **Clientes** em **PostgreSQL** (modelo relacional).
        - **Livros** em **MongoDB** (document store).
        - **Pedidos** em **Redis** (key-value).
4. **S3 – Logger**
    - Também consome os mesmos tópicos e grava cada mensagem bruta em `messages.log` para auditoria.



## ⚙️ Pré-requisitos

Antes de começar, verifique se possui instalado em sua máquina:

- **Docker Desktop** (inclui Docker Compose)
- **Python 3.11+**
- **pip** (gerenciador de pacotes Python)



## 🔧 Instalação e Configuração

1. **Clone o repositório**:
    
    ```bash
    git clone https://github.com/seu-usuario/polyglot-persistence.git
    cd polyglot-persistence
    ```
    
2. **Variáveis de ambiente**:
    - O arquivo `.env` já contém a **Google Books API Key** configurada para avaliação; **não é necessário alterá-la**.
3. **Instale dependências Python**:
    
    ```bash
    pip install -r requirements.txt
    
    ```
    
4. **Inicie a infraestrutura**:
    
    ```bash
    docker-compose up -d
    
    ```
    
    Isso sobe: Kafka, Zookeeper, PostgreSQL, MongoDB e Redis.
    



## 🗂️ Estrutura do Projeto

```
polyglot-persistence/
├── .env.example       # Exemplo de variáveis de ambiente
├── docker-compose.yml # Infraestrutura Docker
├── requirements.txt   # Dependências Python
├── README.md          # Este arquivo
└── services/
    ├── s1_producer/
    │   └── producer.py
    ├── s2_consumer/
    │   └── consumer.py
    └── s3_logger/
        └── logger.py

```



## 🚀 Como Executar

Abra **três terminais** e, em cada um, execute:

```bash
# Terminal 1 – S1: Produtor
python services/s1_producer/producer.py

# Terminal 2 – S2: Consumer & Armazenamento
python services/s2_consumer/consumer.py

# Terminal 3 – S3: Logger
python services/s3_logger/logger.py

```

Você verá no terminal:

- **S1**: `[S1] Sent customer/book/order`
- **S2**: `[S2] Stored customer/book/order in Redis`
- **S3**: `[S3] Logged message from ...`

**Auditoria**: abra `messages.log` para ver todas as mensagens processadas.



## 🛑 Parar e Limpar

Para encerrar e remover containers, redes e volumes:

```bash
docker-compose down --volumes --remove-orphans
```

---