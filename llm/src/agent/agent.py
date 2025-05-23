
from database_connector.database_connector import DatabaseConnector
from model.model import Model
from prompt_generator.prompt_generator import PromptGenerator
from gateway.gateway import Gateway
from evaluator.evaluator import Evaluator
from utils.utils import json_to_string_list

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
    # Get hotel data from mongo
    hotels = self.database_connector_component.mongo_get_data("hotel", {})
    print(f"[FETCHED] Fetched {len(hotels)} hotels")

    for hotel in hotels[:1]:
      # Delete unnecessary columns
      del hotel['_id']
      if 'reviews' in hotel: 
        del hotel['reviews']

      id = hotel['title']
      result_arr = []
      json_to_string_list(hotel, id, result_arr)