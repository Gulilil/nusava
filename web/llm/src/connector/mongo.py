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
    self.mongo_client = pymongo.MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
    self.mongo_database = self.mongo_client[os.getenv("MONGO_DB_NAME")]
    self.mongo_persona_database = self.mongo_client[os.getenv("MONGO_DB_PERSONA_NAME")]


  def get_data(self, collection_name: str, filters: dict = {}) -> list:
    """
    Get data from mongo db with filters as parameters
    """
    collection = self.mongo_database[collection_name]
    json_documents = collection.find(filters)
    return list(json_documents)
  

  def get_persona_data_by_name(self, name: str) -> dict:
    """
    Get persona data based on name
    """
    collection = self.mongo_persona_database["persona"]
    json_documents = collection.find({"name" : name})
    # Check that there should only be one persona
    assert len(json_documents) > 0, "[FAILED] No persona data is found!"
    assert len(json_documents) == 1, "[FAILED] Multiple persona is found!"
    return list(json_documents)[0]
