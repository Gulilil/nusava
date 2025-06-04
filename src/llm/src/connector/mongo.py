import pymongo
import os

from dotenv import load_dotenv
load_dotenv()


class MongoConnector():
  """
  Connecting component to MongoDB : DocumentDB from Data Mining
  """
  def __init__(self): 
    """
    Instantiate the database client
    """
    self.client = pymongo.MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
    self.database = self.client[os.getenv("MONGO_DB_NAME")]


  def get_data(self, collection_name: str, filters: dict = {}) -> list:
    """
    Get data from mongo db with filters as parameters
    """
    collection = self.database[collection_name]
    json_documents = collection.find(filters)
    return list(json_documents)
  