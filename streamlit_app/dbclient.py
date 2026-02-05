from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoVectorClient:
    def __init__(self, username, password, cluster_name, cluster_id, db_name, collection_name, vector_index_name):
        mongo_uri = f"mongodb+srv://{username}:{password}@{cluster_name}.{cluster_id}.mongodb.net/?appName={cluster_name}"
        try:
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
        except ConnectionFailure as e:
            raise RuntimeError(f"Connection failed: {e}")

        self.db = self.client[db_name]
        self.col = self.db[collection_name]
        self.vector_index_name = vector_index_name

    def insert_document(self, doc):
        return self.col.insert_one(doc).inserted_id