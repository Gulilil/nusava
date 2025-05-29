from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore

from pinecone import Pinecone
import pymongo
import os

from dotenv import load_dotenv
load_dotenv()


class DatabaseConnector():
  """
  Connecting component to all the databases:
  1. MongoDB : DocumentDB from Data Mining
  2. Pinecone : VectorDB for LLM and RAG
  3. PostgreSQL: RDBMS for bot data
  """
  def __init__(self): 
    """
    Instantiate all the database client
    """
    # Instantiate mongo client
    self.mongo_client = pymongo.MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
    self.mongo_database = self.mongo_client[os.getenv("MONGO_DB_NAME")]
    # Instantiate pinecone client
    self.pinecone_client = Pinecone(api_key=(os.getenv("PINECONE_API_KEY")))
    self.pinecone_index = self.pinecone_client.Index(os.getenv("PINECONE_INDEX"))


  def mongo_get_data(self, collection_name: str, filters: dict = {}) -> list:
    """
    Get data from mongo db with filters as parameters
    """
    collection = self.mongo_database[collection_name]
    json_documents = collection.find(filters)
    return list(json_documents)
  

  def pinecone_get_vector_store(self, namespace: str):
    """
    Get vector store and storage context from pinecone for certain namespace
    """
    vector_store = PineconeVectorStore(pinecone_index=self.pinecone_index, namespace=namespace)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return vector_store, storage_context


  def pinecone_store_data(self, nodes, storage_context, embed_model):
    """
    Store processed data to certain storage_context
    """
    VectorStoreIndex(nodes, storage_context=storage_context, embed_model=embed_model)


  def pinecone_get_index_stats(self):
    """
    Display status of the pinecone index
    """
    print(self.pinecone_index.describe_index_stats())