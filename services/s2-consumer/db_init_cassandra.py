from cassandra.cluster import Cluster

def init_cassandra():
    cluster = Cluster(['cassandra'])
    session = cluster.connect()
    session.execute("""
      CREATE KEYSPACE IF NOT EXISTS livraria
      WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
    """)
    session.set_keyspace('livraria')
    session.execute("""
      CREATE TABLE IF NOT EXISTS pedidos (
        pedido_id uuid PRIMARY KEY,
        cliente_id int,
        livros list<text>,
        valor_total decimal,
        data_compra timestamp,
        status text
      );
    """)
    cluster.shutdown()
    print("Cassandra: keyspace e tabela pedidos prontas!")

if __name__ == "__main__":
    init_cassandra()
