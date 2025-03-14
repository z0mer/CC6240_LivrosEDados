# Projeto Livros & Dados 📚

## 1. Explicação do Tema

O tema escolhido para este projeto é uma **livraria** online. O sistema irá lidar com três tipos principais de dados:

- **Clientes:** informações cadastrais dos leitores, como nome, e-mail, endereço e preferências literárias.  
- **Livros:** dados sobre os livros disponíveis no catálogo, como título, autor, ISBN, preço, gênero, além de informações adicionais (ex.: sinopse, avaliações).  
- **Pedidos:** histórico de compras realizadas pelos clientes, incluindo a lista de livros adquiridos, datas, valores totais e status de entrega.

A escolha de uma livraria como tema permite explorar a diversidade de dados. Enquanto as informações de clientes e pedidos precisam de consistência relacional, os dados dos livros podem variar em estrutura, dependendo do tipo de livro (físico, e-book, coleções especiais, etc.). Essa variedade justifica o uso de diferentes bancos de dados para cada necessidade, alinhando-se ao conceito de **Polyglot Persistence**.

## 2. Justificativa para cada Banco e Definição de Como S2 Será Implementado

### 2.1 Bancos de Dados Escolhidos

1. **Banco Relacional (RDB) – PostgreSQL**  
   - **Por que usar?**  
     - É fundamental garantir a integridade e a consistência das informações dos clientes (nome, e-mail, CPF, etc.).  
     - Um modelo relacional facilita a criação de relacionamentos e a aplicação de restrições (ex.: unicidade de e-mail).  
   - **Quais dados serão armazenados?**  
     - Dados cadastrais dos clientes: nome, e-mail, endereço, preferências.  
     - Possível uso de chaves estrangeiras, caso necessário relacionar clientes a outras entidades (por exemplo, histórico de pedidos).

2. **Banco NoSQL (Document Store) – MongoDB**  
   - **Por que usar?**  
     - Livros podem ter estruturas de dados diferentes (livros físicos vs. e-books), atributos opcionais (edições, formatos, idiomas, etc.).  
     - O formato de documentos (JSON) oferece flexibilidade para armazenar diversas informações sem a necessidade de alterar esquemas complexos.  
   - **Quais dados serão armazenados?**  
     - Informações dos livros: título, autor, ISBN, gênero, sinopse, avaliações, preço, estoque, formato (físico ou digital), entre outros atributos específicos.

3. **Banco NoSQL (Wide Column) – Cassandra**  
   - **Por que usar?**  
     - Escalabilidade horizontal e alta disponibilidade para lidar com um grande volume de pedidos, especialmente se a livraria crescer e receber muitos acessos simultâneos.  
     - Modelagem orientada a consultas, eficiente para recuperar rapidamente históricos de pedidos ou buscar dados de vendas.  
   - **Quais dados serão armazenados?**  
     - Pedidos: identificação do cliente, lista de livros adquiridos, valor total, data de compra, status de entrega.  
     - Informações que podem ser consultadas com grande frequência, como histórico de compras do cliente ou análise de vendas.

### 2.2 Definição do Serviço S2

O **S2** será o serviço responsável por receber as mensagens que chegam do sistema de mensageria (enviadas pelo S1) e realizar as operações de armazenamento/consulta nos bancos de dados. Existem duas abordagens possíveis:

1. **Serviço Único (Monolítico)**  
   - Lê todas as mensagens (sobre clientes, livros e pedidos) e faz o roteamento interno, direcionando cada operação para o banco apropriado (PostgreSQL, MongoDB ou Cassandra).  
   - **Vantagens:**  
     - Menor complexidade na gestão de serviços (somente um serviço para consumir as mensagens).  
   - **Desvantagens:**  
     - Pode tornar-se muito grande e de difícil manutenção à medida que a aplicação cresce.

2. **Serviços Separados (Microserviços)**  
   - Um serviço para cada tipo de dado:  
     - **S2-Clientes:** conecta-se ao PostgreSQL.  
     - **S2-Livros:** conecta-se ao MongoDB.  
     - **S2-Pedidos:** conecta-se ao Cassandra.  
   - **Vantagens:**  
     - Separação de responsabilidades e escalabilidade independente de cada serviço.  
   - **Desvantagens:**  
     - Maior número de serviços para gerenciar e orquestrar.

Para este projeto, **optaremos inicialmente por um único serviço S2**, pois isso simplifica a demonstração do conceito de Polyglot Persistence. O serviço único fará a leitura de cada mensagem (por exemplo, “cliente.create”, “livro.create”, “pedido.create”) e gravará os dados no respectivo banco. Caso seja necessário escalar ou segmentar a aplicação, podemos evoluir para microserviços em uma etapa posterior.


