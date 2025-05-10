from pymongo import MongoClient

def init_mongo():
    client = MongoClient("mongodb://mongo:27017/")
    db = client.livraria
    db.livros.create_index("isbn", unique=True)
    print("MongoDB: índice ISBN criado em livros!")

if __name__ == "__main__":
    init_mongo()
