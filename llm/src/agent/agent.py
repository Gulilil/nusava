from llama_index.core import Settings

from database_connector.database_connector import DatabaseConnector
from model.model import Model
from prompt_generator.prompt_generator import PromptGenerator
from gateway.gateway import Gateway
from evaluator.evaluator import Evaluator
from utils.function import json_to_string_list, text_to_document

class Agent():
  
  def __init__(self):
    self.database_connector_component = DatabaseConnector()
    self.model_component = Model()
    self.prompt_generator_component = PromptGenerator()
    self.gateway_component = Gateway()
    self.evaluator_component = Evaluator()


  # Agent decide action to do
  def decide_action(self, last_action: str = None, last_action_details: str = None):
    prompt = self.prompt_generator_component.generate_prompt_decide_action(last_action, last_action_details)
    answer = self.model_component.answer(prompt, True)
    return answer
  

  # Process data hotel, "migrate" it from mongodb document to pinecone vector
  def process_data_hotel(self):
    mongo_collection_name = "hotel"
    pinecone_namespace_name = "hotels"

    # Get hotel data from mongo
    hotels = self.database_connector_component.mongo_get_data(mongo_collection_name, {})
    print(f"[FETCHED] Fetched {len(hotels)} hotels")

    hotel_docs = []
    for hotel in hotels[:3]:
      # Delete unnecessary columns
      del hotel['_id']
      id = hotel['title']
      # Get text list from json_data
      text_list = []
      json_to_string_list(hotel, id, text_list)
      # Process to be document list
      documents_list = text_to_document(text_list)
      hotel_docs.extend(documents_list)

    # Insert to pinecone
    vector_store, _ = self.database_connector_component.pinecone_get_vector_store(pinecone_namespace_name)
    self.database_connector_component.pinecone_store_data(hotel_docs, vector_store, self.model_component.embed_model)

    self.database_connector_component.pinecone_get_index_stats()

  # Answer query
  def answer_input(self, user_input: str):
    return
