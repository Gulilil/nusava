from agent.model import Model
from agent.persona import Persona
from agent.memory import Memory
from connector.pinecone import PineconeConnector
from connector.mongo import MongoConnector
from connector.postgres import PostgresConnector
from evaluator.evaluator import Evaluator
from gateway.input import InputGateway
from gateway.output import OutputGateway
from generator.prompt import PromptGenerator
from generator.action import ActionGenerator
from generator.schedule import ScheduleGenerator
from utils.function import json_to_string_list, text_to_document, parse_documents

class Agent():
  """
  General class that encapsulate all the components
  """
  
  def __init__(self):
    self.user_id = None
        # Instantiate Agent Component
    self.model_component = Model()
    self.persona_component = Persona()
    print("[INITIALIZED] Agent component(s) initialized")
    # Instantiate Connector
    self.pinecone_connector_component = PineconeConnector()
    self.mongo_connector_component = MongoConnector()
    self.postgres_connector_component = PostgresConnector()
    print("[INITIALIZED] Connector component(s) initialized")
    # Instantiate Evaluator
    self.evaluator_component = Evaluator()
    print("[INITIALIZED] Evaluator component(s) initialized")
    # Instantiate Gateway
    self.input_gateway_component = InputGateway(self)
    self.output_gateway_component = OutputGateway()
    print("[INITIALIZED] Gateway component(s) initialized")
    # Instantiate Generator
    self.prompt_generator_component = PromptGenerator(self.persona_component)
    print("[INITIALIZED] Generator component(s) initialized")


  ######## SETUP PERSONA/ CONFIG ########

  def set_user(self, user_id:str):
    print(f"[CONSTRUCT] Constructing agent for user_id: {user_id}")
    self.user_id = user_id

    # TODO To be adjusted
    self.set_config()
    self.set_persona()

  def set_persona(self):
    """
    Change the agent persona
    """
    persona_data = self.postgres_connector_component.get_persona_data(self.user_id)
    self.persona_component.load_persona(persona_data)
    self.persona_component.display_persona()

  
  def set_config(self):
    """
    Adjust the performance of the model
    """
    config_data = self.postgres_connector_component.get_config_data(self.user_id)
    self.model_component.config(config_data)
    self.model_component.display_config()


  ######## PUBLIC ########

  def run(self):
    self.input_gateway_component.run()


  def decide_action(self, last_action: str = None, last_action_details: str = None):
    """
    Decision making function of the system
    """
    prompt = self.prompt_generator_component.generate_prompt_decide_action(last_action, last_action_details)
    answer = self.model_component.answer(prompt, True)
    return answer
  

  def process_data_hotel(self):
    """
    Process data hotel, "migrate" it from mongodb document to pinecone vector
    """
    mongo_collection_name = "hotel"
    pinecone_namespace_name = "hotels"

    # Get hotel data from mongo
    hotels = self.mongo_connector_component.get_data(mongo_collection_name, {})
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
        documents_list = text_to_document(text_list)
        hotel_docs.extend(documents_list)

      # Parse hotel data
      hotel_data_parsed = parse_documents(hotel_docs)
      # Insert to pinecone
      _, storage_context = self.pinecone_connector_component.get_vector_store(pinecone_namespace_name)
      self.pinecone_connector_component.store_data(hotel_data_parsed, storage_context, self.model_component.embed_model)      
      print(f'[BATCH PROGRESS] Successfully inserted data idx {idx} to {upper_idx}')
      
      # Increment idx
      idx += length_per_batch

  # TODO
  def process_data_xxxx(self):
    """
    Process data xxxx, "migrate" it from mongodb document to pinecone vector
    """
    return


  ######## ACTION ########

  ######## EXTERNAL TRIGGER ACTION ########

  def action_reply_chat(self, 
                        chat_message: str):
    """
    Operate the action reply chat
    """
    #TODO What to do with user_id
    #TODO How to determine that it is about hotel and construct metadata
    # Load the data from pinecone
    namespace_name = 'hotels'
    vector_store, storage_context = self.pinecone_connector_component.get_vector_store(namespace_name)
    self.model_component.load_data(
      vector_store, 
      storage_context, 
      namespace_name,
      chat_message)

    # Generate prompt
    prompt = self.prompt_generator_component.generate_prompt_reply_chat(
      new_message=chat_message,
      previous_messages=None)
    return self.model_component.answer(prompt)


  def action_reply_comment(self, 
                           comment_message: str, 
                           post_caption: str, 
                           previous_comments: list[str]):
    """
    Operate the action reply comment
    """
    # TODO
    return
  
  ######## INTERNAL TRIGGER ACTION ########

  def action_follow(self):
    """
    Operate the action follow
    """
    # TODO
    return


  def action_like(self):
    """
    Operate the action like
    """
    # TODO
    return


  def action_comment(self):
    """
    Operate the action comment
    """
    # TODO 
    return


  def action_post(self, 
                  img_url: str, 
                  img_description: str, 
                  caption_keywords: list[str]):
    """
    Operate the action post
    """
    # TODO To be improved
    
    # # Generate prompt
    prompt = self.prompt_generator_component.generate_prompt_post_caption(
      img_description=img_description,
      keywords=caption_keywords,
      additional_context=None,
      examples= None
      )
    
    caption_message = self.model_component.answer(prompt, True)

    # TODO Schedule the post
    print(caption_message)