# 📚 Projeto Livros & Dados – Polyglot Persistence

Este repositório implementa uma **livraria online** seguindo o padrão **Polyglot Persistence** e arquitetura **Pub/Sub** com **Apache Kafka**. O sistema envolve três serviços e armazena diferentes tipos de dados em bancos distintos:

* **Clientes** (informações cadastrais)
* **Livros** (catálogo via API Google Books)
* **Pedidos** (histórico de compras)


## 🧩 Visão Geral e Funcionamento

1. **S1 – Produtor**

   * Gera dados fictícios de **Clientes** (via Faker), **Livros** (API Google Books) e **Pedidos**.

     > **Nota:** o Faker usa domínios reservados (`@example.com`, `@example.org`, `@example.net`) para gerar e-mails falsos, evitando dados reais.
   * Publica mensagens em três tópicos Kafka:

     * `customers`
     * `books`
     * `orders`

2. **Kafka + Zookeeper**

   * Serviço de mensageria Pub/Sub que desacopla produtores e consumidores.

3. **S2 – Consumer & Armazenamento**

   * Consome mensagens dos três tópicos e persiste em bancos apropriados:

    * **Clientes:** `id` (UUID), `name` (nome), `email` (e-mail)
    * **Livros:** `id` (Google Books ID), `isbn` (se disponível), `title` (título), `authors` (autores), `publishedDate` (data de publicação)
    * **Pedidos:** `id` (UUID), `customer_id` (UUID do cliente), `book_id` (ID do livro), `quantity` (quantidade), `timestamp` (carimbo de tempo)

4. **S3 – Logger**

   * Consome os mesmos tópicos e grava cada mensagem **crua** em `messages.log` para auditoria.


## ✏️ Tema e Justificativa de Bancos

### 1. Tema: Livraria Online

O sistema lida com:

* **Clientes:** id, nome, e-mail.
* **Livros:** id, isbn, título, autores, data de publicação.
* **Pedidos:** id, id do cliente, id do livro, quantidade, carimbo de tempo.

A diversidade de estrutura e volume de acesso justifica o uso de **Polyglot Persistence**.

### 2. Escolha dos Bancos

| Banco          | Tipo                   | Uso                                                |
| -------------- | ---------------------- | -------------------------------------------------- |
| **PostgreSQL** | Relacional (RDB)       | Clientes (integridade e restrições)                |
| **MongoDB**    | Document Store (NoSQL) | Livros (estrutura flexível em JSON)                |
| **Redis**      | Key-Value (NoSQL)      | Pedidos (lembrança rápida de histórico de compras) |

> *Nota:* originalmente consideramos Cassandra (wide-column) para pedidos, mas optamos por Redis para agilizar a entrega e evitar dependências de C-extensions.

### 3. Implementação do S2

Optamos por **um único serviço S2** que roteia internamente:

* Recebe todas as mensagens e, conforme o tópico, chama a camada de persistência correspondente.
* **Vantagem:** demonstração simples e código centralizado.
* **Evolução futura:** possível divisão em microserviços específicos para cada dado.


## ⚙️ Pré-requisitos

* **Docker Desktop** (com Docker Compose)
* **Python 3.11+**
* **pip**


## 🔧 Instalação e Configuração

1. **Clone o repositório**

   ```bash
   git clone https://github.com/z0mer/PJ3.BANCO_DE_DADOS.git
   cd PJ3.BANCO_DE_DADOS
   ```

2. **Variáveis de ambiente**

   * O arquivo `.env` já contém a **Google Books API Key**;

3. **Instale dependências Python**

   ```bash
   pip install -r requirements.txt
   ```

4. **Inicie os containers**

   ```bash
   docker-compose up -d
   ```

   Serviços iniciados: Kafka, Zookeeper, PostgreSQL, MongoDB e Redis.

---

## 🚀 Execução

Abra mais **três terminais** e execute em cada um:

```bash
# Terminal 1 – Produtor (S1)
python services/s1_producer/producer.py

# Terminal 2 – Consumer & Armazenamento (S2)
python services/s2_consumer/consumer.py

# Terminal 3 – Logger (S3)
python services/s3_logger/logger.py
```

Você verá:

* **S1:** `[S1] Sent customer/book/order`
* **S2:** `[S2] Stored customer/book/order in Redis`
* **S3:** `[S3] Logged message from ...`

 **Auditoria:** abra `messages.log` para ver todas as mensagens processadas.


## 🛑 Parar e Limpar

Para encerrar e remover containers, redes e volumes:

```bash
docker-compose down --volumes --remove-orphans
```

