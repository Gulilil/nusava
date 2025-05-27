from database_connector.database_connector import DatabaseConnector
from model.model import Model
from prompt_generator.prompt_generator import PromptGenerator
from gateway.gateway import Gateway
from evaluator.evaluator import Evaluator
from utils.function import json_to_string_list, text_to_document, parse_documents

class Agent():
  
  def __init__(self):
    self.database_connector_component = DatabaseConnector()
    self.evaluator_component = Evaluator()
    self.gateway_component = Gateway()
    self.model_component = Model()
    self.prompt_generator_component = PromptGenerator()


  # TODO Agent decide action to do 
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
    idx = 0
    n_batch = 20
    length_per_batch = (len(hotels)//n_batch)+1
    while (idx < len(hotels)):
      # Set batch indices
      upper_idx = min(idx+length_per_batch, len(hotels))
      curr_batch_hotels = hotels[idx : upper_idx]

      # Iterate data in the current batch list
      for hotel in curr_batch_hotels:
        # Delete unnecessary columns
        del hotel['_id']
        # Use title as id, assuming it is unique for all data
        id = hotel['title']
        # Get text list from json_data
        text_list = []
        json_to_string_list(hotel, id, text_list)
        # Process to be document list
        documents_list = text_to_document(text_list)
        hotel_docs.extend(documents_list)

      # Parse hotel data
      hotel_data_parsed = parse_documents(hotel_docs)
      # Insert to pinecone
      _, storage_context = self.database_connector_component.pinecone_get_vector_store(pinecone_namespace_name)
      self.database_connector_component.pinecone_store_data(hotel_data_parsed, storage_context, self.model_component.embed_model)
      
      # Increment idx
      print(f'[BATCH PROGRESS] Successfully inserted data idx {idx} to {upper_idx}')
      idx += length_per_batch

  # TODO
  def process_data_xxxx(self):
    return


  ##### ACTION #####

  # Answer query
  def action_chat(self, user_query: str):

    #TODO How to determine that it is about hotel and construct metadata
    # Load the data from pinecone
    namespace_name = 'hotels'
    vector_store, storage_context = self.database_connector_component.pinecone_get_vector_store(namespace_name)
    self.model_component.load_data(
      vector_store, 
      storage_context, 
      namespace_name,
      user_query)

    # Generate prompt
    prompt = self.prompt_generator_component.generate_prompt_reply_chat(user_query)
    return self.model_component.answer(prompt)
