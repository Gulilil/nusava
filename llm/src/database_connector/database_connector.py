from llama_index.core import Document

from pinecone import Pinecone
import pymongo
import os
import jsonpickle
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()


class DatabaseConnector():
  # Initialization
  def __init__(self): 
    # Instantiate mongo client
    self.mongo_client = pymongo.MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
    self.mongo_database = self.mongo_client[os.getenv("MONGO_DB_NAME")]
    # Instantiate pinecone client
    self.pinecone_client = Pinecone(api_key=(os.getenv("PINECONE_API_KEY")))
    self.pinecone_index = self.pinecone_client.Index(os.getenv("PINECONE_INDEX"))


  # Get parsed based on filename
  def mongo_get_data(self, collection_name: str, filters: dict = {}) -> list:
    collection = self.mongo_database[collection_name]
    json_documents = collection.find(filters)
    return list(json_documents)


  # Parse json
  def mongo_parse(self, collection_name: str, title: str) -> str:
    documents = self.mongo_get_data(collection_name, {"title": title})

    assert len(documents) > 0, "[ERROR] No data found"
    assert len(documents) == 1, "[ERROR] Multiple title, not unique"

    document = documents[0]
    # Delete id since it is not necessary
    del document['_id']
    # Delete reviews
    del document['reviews']
    return document

  # Upsert vector index
  def pinecone_upsert(self, vector_data: dict) -> None:
    self.pinecone_index.upsert_records(vector_data)