from agent.memory import Memory
from agent.model import Model
from agent.persona import Persona
from connector.pinecone import PineconeConnector
from connector.mongo import MongoConnector
from connector.postgres import PostgresConnector
from evaluator.evaluator import Evaluator
from gateway.input import InputGateway
from gateway.output import OutputGateway
from generator.prompt import PromptGenerator
from generator.action import ActionGenerator
from generator.schedule import ScheduleGenerator
from utils.function import hotel_data_to_string_list, text_to_document, parse_documents, clean_quotation_string


class Agent():
  """
  General class that encapsulate all the components
  """
  
  def __init__(self):
    self.user_id = None
    # Instantiate Agent Component
    self.persona_component = Persona()
    self.memory_component = Memory(self)
    self.model_component = Model(self.persona_component)
    print("[AGENT INITIALIZED] Agent component(s) initialized")
    # Instantiate Connector
    self.pinecone_connector_component = PineconeConnector()
    self.mongo_connector_component = MongoConnector()
    self.postgres_connector_component = PostgresConnector()
    print("[AGENT INITIALIZED] Connector component(s) initialized")
    # Instantiate Evaluator
    self.evaluator_component = Evaluator(self.model_component.llm_model)
    print("[AGENT INITIALIZED] Evaluator component(s) initialized")
    # Instantiate Gateway
    self.input_gateway_component = InputGateway(self)
    self.output_gateway_component = OutputGateway()
    print("[AGENT INITIALIZED] Gateway component(s) initialized")
    # Instantiate Generator
    self.prompt_generator_component = PromptGenerator(self.persona_component)
    self.action_generator_component = ActionGenerator()
    self.schedule_generator_component = ScheduleGenerator()
    print("[AGENT INITIALIZED] Generator component(s) initialized")



  ######## SETUP PERSONA/ CONFIG ########

  def set_user(self, user_id:str) -> None:
    """
    Set user_id, as well as model config and persona.
    This function should be called first thing
    """
    print(f"[AGENT CONSTRUCTED] Constructing agent for user_id: {user_id}")
    self.user_id = user_id

    # Reset model tools
    self.model_component.refresh_tools()

    # Setup components
    self.set_config()
    self.set_persona()

  def set_persona(self) -> None:
    """
    Change the agent persona
    """
    persona_data = self.postgres_connector_component.get_persona_data(self.user_id)
    self.persona_component.load_persona(persona_data)

  
  def set_config(self) -> None:
    """
    Adjust the performance of the model
    """
    config_data = self.postgres_connector_component.get_config_data(self.user_id)
    self.model_component.config(config_data)


  ######## PUBLIC ########

  def run(self) -> None:
    """
    Run the agent, this is the main entry point for the agent to start working
    """
    print("[AGENT RUN] Agent is running...")
    self.input_gateway_component.run()


  def decide_action(self) -> None:
    """
    Decide action based on the current conditions and statistics
    This is the main entry point for the agent to decide what to do next.
    """
    statistics = self.output_gateway_component.request_statistics(self.user_id)
    observations = self.action_generator_component.observe_statistics(statistics)
    print(f"[ACTION OBSERVATION] Acquired observations: {observations}")

    # Max 5 times of action decision
    for itr in range(5):
      action, state = self.action_generator_component.decide_action(observations, itr)
      print(f"[ACTION DECISION] {itr+1}.  action \"{action}\" in state \"{state}\"")

      if (action == "like"):
        self.action_like()
      elif (action == "follow"):
        self.action_follow()
      elif (action == "comment"):
        self.action_comment()
      else:
        return
      

  async def summarize_and_store_memory(self, sender_id: str, memory_data: list[dict]) -> bool:
    """
    Summarize memory and store it to vector database
    """
    # Make the summary
    try:
      prompt = self.prompt_generator_component.generate_prompt_summarize_memory(memory_data)
      summary, _ = await self.model_component.answer(prompt, is_direct=True)
      
      # Prepare to insert
      pinecone_namespace_name = f"chat_bot[{self.user_id}]_sender[{sender_id}]"
      summary_document = text_to_document([summary])
      summary_parsed = parse_documents(summary_document)
      _, storage_context = self.pinecone_connector_component.get_vector_store(pinecone_namespace_name)

      # Insert to pinecone
      self.pinecone_connector_component.store_data(summary_parsed, storage_context, self.model_component.embed_model) 
      return True

    except Exception as e:
      print(f"[ERROR SUMMARIZE AND STORE MEMORY] {e}")
      return False



  ######## ACTION ########

  ######## EXTERNAL TRIGGER ACTION ########

  async def action_reply_chat(self, chat_message: str, sender_id: str) -> str:
    """
    Operate the action reply chat
    """

    # Store in user query reply memory
    await self.memory_component.store(sender_id, {"role": "user", "content" : chat_message})

    try:
      # Load the data from pinecone
      # First hotel data
      pinecone_namespace_name = 'hotels_new'
      vector_store, storage_context = self.pinecone_connector_component.get_vector_store(pinecone_namespace_name)
      await self.model_component.load_data(
        vector_store, 
        storage_context, 
        pinecone_namespace_name,
        chat_message)
      
      # Load the long-term memory from pinecone
      pinecone_namespace_name = f"chat_bot[{self.user_id}]_sender[{sender_id}]"
      if (self.pinecone_connector_component.is_namespace_exist(pinecone_namespace_name)):
        vector_store, storage_context = self.pinecone_connector_component.get_vector_store(pinecone_namespace_name)
        await self.model_component.load_data(
          vector_store, 
          storage_context, 
          pinecone_namespace_name,
          chat_message)
        print(f"[LOADING MEMORY] Inserting long-term memory as tools for RAG")


      # Do iteration of action reply chat
      # While the thresholds are not satisfied, do the iteration
      max_attempts = 3 
      attempt = 0
      correctness_pass, faithfulness_pass, relevancy_pass = False, False, False
      previous_iteration_notes = []
      while (not correctness_pass or not faithfulness_pass or not relevancy_pass):
        # Generate prompt
        prompt = self.prompt_generator_component.generate_prompt_reply_chat(
          new_message=chat_message,
          previous_messages=self.memory_component.retrieve(sender_id),
          previous_iteration_notes=previous_iteration_notes)
      
        # Answer the query
        # Skip if the answer is None
        answer, contexts = await self.model_component.answer(prompt)
        if (answer is not None):
          print(f"[ACTION REPLY CHAT] Attempt {attempt+1} of {max_attempts}. \nQuery: {chat_message} \nAnswer: {answer}")

          # Display contexts (for printing only)
          for i, context  in enumerate(contexts):
            context_topic = context.split('\n', 1)[0]
            print(f"[ACTION REPLY CHAT CONTEXT #{i+1}] : {context_topic}")
          
          # Evaluate the answer
          correctness_evaluation = await self.evaluator_component.evaluate_correctness(chat_message, answer, contexts)
          correctness_pass = correctness_evaluation["passing"]
          faithfulness_evaluation = await self.evaluator_component.evaluate_faithfulness(chat_message, answer, contexts)
          faithfulness_pass = faithfulness_evaluation["passing"]
          relevancy_evaluation = await self.evaluator_component.evaluate_relevancy(chat_message, answer, contexts)  
          relevancy_pass = relevancy_evaluation["passing"]
          print(f"[EVALUATION RESULT] \nCorrectness: {correctness_evaluation} \nFaithfulness: {faithfulness_evaluation} \nRelevancy: {relevancy_evaluation}")

        # Increment attempt
        attempt += 1
        if (attempt >= max_attempts):
          raise Exception(f"Model cannot answer this query after {max_attempts} attempts. The evaluations thresholds are not satisfied.")
        
        # Add notes for failing evaluation
        if (answer is None):
          previous_iteration_notes.append({
            "iteration": attempt,
            "your_answer" : None,
            "evaluator": "model",
            "evaluation_score": None,
            "reason_of_rejection": "Model cannot answer this query."
          })
        else:
          if (not correctness_pass):
            previous_iteration_notes.append({
              "iteration": attempt,
              "your_answer" : answer,
              "evaluator": "correctness",
              "reason_of_rejection": correctness_evaluation['reason']
            })
          if (not faithfulness_pass):
            previous_iteration_notes.append({
              "iteration": attempt,
              "your_answer" : answer,
              "evaluator": "faithfulness",
              "reason_of_rejection": faithfulness_evaluation['reason']
            })
          if (not relevancy_pass):
            previous_iteration_notes.append({
              "iteration": attempt,
              "your_answer" : answer,
              "evaluator": "relevancy",
              "reason_of_rejection": relevancy_evaluation['reason']
            })
      # Return the answer
      answer = clean_quotation_string(answer)

      # Store in bot's reply memory
      await self.memory_component.store(sender_id, {"role": "bot", "content" : answer})

      return answer
    
    except Exception as e:
      print(f"[ERROR ACTION REPLY CHAT] Error occured while processing action reply chat: {e}")

      # LLM should explain to user
      error_prompt = self.prompt_generator_component.generate_prompt_error(user_query=chat_message)
      answer, _ = await self.model_component.answer(error_prompt, is_direct=True)
      answer = clean_quotation_string(answer)

      # Store in bot's reply memory
      await self.memory_component.store(sender_id, {"role": "bot", "content" : answer})

      return answer


  ######## INTERNAL TRIGGER ACTION ########

  def action_follow(self) -> None:
    """
    Operate the action follow
    """
    # TODO
    return


  def action_like(self) -> None:
    """
    Operate the action like
    """
    # TODO
    return


  def action_comment(self) -> None:
    """
    Operate the action comment
    """
    # TODO 
    return
  

  def action_schedule_post(self, img_url: str, caption_message: str) -> None:
    """
    Operate the action schedule post
    """
    # TODO
    return


  async def action_generate_caption(self, 
                  img_description: str, 
                  caption_keywords: list[str],
                  additional_context: str = None) -> str:
    """
    Operate the action generate caption
    """
    try:
      # Do iteration of action generate caption
      # While the thresholds are not satisfied, do the iteration
      max_attempts = 3 
      attempt = 0
      relevancy_pass = False
      previous_iteration_notes = []
      while (not relevancy_pass):
        # Generate prompt
        prompt = self.prompt_generator_component.generate_prompt_post_caption(
          img_description=img_description,
          keywords=caption_keywords,
          additional_context=additional_context,
          previous_iteration_notes=previous_iteration_notes
          )

        # Generate caption message
        # Skip is the caption message is None
        caption_message, _ = await self.model_component.answer(prompt, is_direct=True)
        if (caption_message is not None):
          print(f"[ACTION POST CAPTION] Attempt {attempt+1} of {max_attempts}. \nCaption: {caption_message}")

          # Prepare contexts for evaluation
          keywords_str = ", ".join(caption_keywords)
          contexts = [f"Here is the image description: {img_description}", f"Here are the keywords: {keywords_str}"]  
          
          # Evaluate the answer
          relevancy_evaluation = await self.evaluator_component.evaluate_relevancy("Create a caption for an Instagram post", caption_message, contexts)  
          relevancy_pass = relevancy_evaluation['passing']
          print(f"[EVALUATION RESULT] \nRelevancy: {relevancy_evaluation}")
        else:
          print(f"[FAILED ACTION POST CAPTION] Attempt {attempt+1} of {max_attempts}. Model cannot generate caption.")

        # Increment attempt
        attempt += 1
        if (attempt >= max_attempts):
          raise Exception(f"Model cannot answer this query after {max_attempts} attempts. The evaluation threshold is not satisfied.")
        
        # Add notes for failing evaluation
        if (caption_message is None):
          previous_iteration_notes.append({
            "iteration": attempt,
            "your_answer" : None,
            "evaluator": "model",
            "reason_of_rejection": "Model cannot generate caption."
          })
        elif (caption_message and not relevancy_pass):
          previous_iteration_notes.append({
            "iteration": attempt,
            "your_answer" : caption_message,
            "evaluator": "relevancy",
            "reason_of_rejection": relevancy_evaluation['reason']
          })
      # Return the generated caption
      answer = clean_quotation_string(caption_message)
      return answer

    except Exception as e:
      print(f"[ERROR ACTION POST] Error occured while processing action post caption: {e}")
      user_query = f"Make a post caption with image description: {img_description}, keywords: {caption_keywords}, additional context: {additional_context}"
      error_prompt = self.prompt_generator_component.generate_prompt_error(user_query=user_query)
      answer, _ = await self.model_component.answer(error_prompt, is_direct=True)
      answer = clean_quotation_string(answer)
      return answer


  ######## PROCESS DATA ########
  """
  Should only be run manually
  It is run to convert the data from Document type in Mongo to Vector in Pinecone
  """

  def process_data_hotel(self) -> None:
    """
    Process data hotel, "migrate" it from mongodb document to pinecone vector
    """
    mongo_collection_name = "hotel"
    pinecone_namespace_name = "hotels_new"

    # Get hotel data from mongo
    hotels = self.mongo_connector_component.get_data(mongo_collection_name, {})
    print(f"[FETCHED] Fetched {len(hotels)} hotels")


    idx = 0
    n_batch = 20
    length_per_batch = (len(hotels)//n_batch)+1
    while (idx < len(hotels)):
      # Set batch indices
      hotel_docs = []
      upper_idx = min(idx+length_per_batch, len(hotels))
      curr_batch_hotels = hotels[idx : upper_idx]

      # Iterate data in the current batch list
      for hotel in curr_batch_hotels:
        hotel_string_data = hotel_data_to_string_list(hotel)
        documents_list = text_to_document(hotel_string_data)
        hotel_docs.extend(documents_list)

      # Parse hotel data
      hotel_data_parsed = parse_documents(hotel_docs)
      # Insert to pinecone
      _, storage_context = self.pinecone_connector_component.get_vector_store(pinecone_namespace_name)
      self.pinecone_connector_component.store_data(hotel_data_parsed, storage_context, self.model_component.embed_model)      
      print(f'[BATCH PROGRESS] Successfully inserted data idx {idx} to {upper_idx}')
      
      # Increment idx
      idx += length_per_batch

  # TODO Wait for later data mining process
  def process_data_xxxx(self) -> None:
    """
    Process data xxxx, "migrate" it from mongodb document to pinecone vector
    """
    return

