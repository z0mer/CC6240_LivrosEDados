from sqlalchemy import create_engine, text

def init_postgres():
    engine = create_engine('postgresql://postgres:postgres@postgres:5432/livraria')
    with engine.begin() as conn:
        conn.execute(text("""
          CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL
          );
        """))
    print("Postgres: tabela clientes pronta!")

if __name__ == "__main__":
    init_postgres()
