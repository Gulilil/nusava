import random
import json
import time

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
from utils.function import hotel_data_to_string_list, attraction_data_to_string_list, text_to_document, parse_documents, clean_quotation_string


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
    self.mongo_connector_component = MongoConnector() 
    self.postgres_connector_component = PostgresConnector()
    self.pinecone_connector_component = PineconeConnector(self.model_component)
    print("[AGENT INITIALIZED] Connector component(s) initialized")
    # Instantiate Evaluator
    self.evaluator_component = Evaluator(self.model_component.llm_model)
    print("[AGENT INITIALIZED] Evaluator component(s) initialized")
    # Instantiate Gateway
    self.input_gateway_component = InputGateway(self)
    self.output_gateway_component = OutputGateway(self)
    print("[AGENT INITIALIZED] Gateway component(s) initialized")
    # Instantiate Generator
    self.prompt_generator_component = PromptGenerator(self.persona_component)
    self.action_generator_component = ActionGenerator()
    self.schedule_generator_component = ScheduleGenerator()
    print("[AGENT INITIALIZED] Generator component(s) initialized")


  #######################
  ######## SETUP ########
  #######################

  async def set_user(self, user_id:str) -> None:
    """
    Set user_id, as well as model config and persona.
    This function should be called first thing
    """

    # Check if there is any memory
    # Insert first the memory before changing user_id
    if (self.user_id and self.memory_component.count() > 0):
      memories = self.memory_component.retrieve_all()
      for sender_id, memory_data in memories.items():
        print(f"[STORING REMAINING MEMORY] Storing remaining memory from previous user with user_id: {user_id} with {sender_id}")
        await self.summarize_and_store_memory(sender_id, memory_data)
      
    print(f"[AGENT CONSTRUCTED] Constructing agent for user_id: {user_id}")
    self.user_id = user_id

    # Reset model tools
    self.model_component.refresh_tools("", is_all=True)

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


  #######################
  ######## OTHER ########
  #######################

  def run(self) -> None:
    """
    Run the agent, this is the main entry point for the agent to start working
    """
    print("[AGENT RUN] Agent is running...")
    self.input_gateway_component.run()
      

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
    

  async def _load_tools_rag(self, pinecone_namespace_name : str, metadata_name: str, metadata_description: str, tool_user_id: str):
    """
    Load tools to be inserted to array of tools and later be used by ReAct
    """
    vector_store, storage_context = self.pinecone_connector_component.get_vector_store(pinecone_namespace_name)
    await self.model_component.load_data(vector_store, 
                                          storage_context, 
                                          metadata_name,
                                          metadata_description,
                                          tool_user_id)
    print(f"[LOADING TOOLS] Inserting tools for RAG: {pinecone_namespace_name}")

  
  def _construct_retrieval_system (self, pinecone_namespace_name : str, top_k: int =10):
    """
    Return query engine as retrieval system
    """
    vector_store, storage_context = self.pinecone_connector_component.get_vector_store(pinecone_namespace_name)
    return self.model_component.construct_retrieval_system(vector_store, storage_context, top_k)

  

  #########################################
  ######## EXTERNAL TRIGGER ACTION ########
  #########################################

  async def action_reply_chat(self, chat_message: str, sender_id: str) -> str:
    """
    Operate the action reply chat
    """

    # Store in user query reply memory
    await self.memory_component.store(sender_id, {"role": "user", "content" : chat_message})

    try:
      # Load the data from pinecone
      # First hotel data
      await self._load_tools_rag("hotels", "rag_tools_for_hotels_data", "Used to answer hotels-related query based on retrieved documents", sender_id)
      # Then asso-rules
      await self._load_tools_rag("association_rules", "rag_tools_for_association_rules_data", "Used to recommend system for hotel based on its antecedent-consequent relation based on retrieved documents", sender_id)
      # Then tourist attractions
      await self._load_tools_rag("tourist_attractions", "rag_tools_for_tourist_attractions_data", "Used to answer tourist-attractions-related query based on retrieved documents", sender_id)
            
      # Load the long-term memory from pinecone
      chat_memory_namespace_name = f"chat_bot[{self.user_id}]_sender[{sender_id}]"
      if (self.pinecone_connector_component.is_namespace_exist(chat_memory_namespace_name)):
        await self._load_tools_rag(chat_memory_namespace_name, f"rag_tools_for_memory_chat_with_{sender_id}", f"Used to help answering question from {sender_id} based on previous occurences", sender_id)

      # Do iteration of action reply chat
      # While the thresholds are not satisfied, do the iteration
      max_attempts = 3 
      attempt = 0
      evaluation_passing = False
      previous_iteration_notes = []
      while (not evaluation_passing):
        # Generate prompt
        prompt = self.prompt_generator_component.generate_prompt_reply_chat(
          new_message=chat_message,
          previous_messages=self.memory_component.retrieve(sender_id),
          previous_iteration_notes=previous_iteration_notes)  
        # Answer the query
        # Skip if the answer is None
        answer, contexts = await self.model_component.answer(prompt, tool_user_id=sender_id)
        print(f"[ACTION REPLY CHAT] Attempt {attempt+1} of {max_attempts}. \nQuery: {chat_message} \nAnswer: {answer}")

        if (answer is None):
          previous_iteration_notes.append({
            "iteration": attempt,
            "your_answer" : None,
            "evaluator": "model",
            "evaluation_score": None,
            "reason_of_rejection": "Model cannot answer this query."
          })
        # Answer is not None
        else:
          # Display contexts
          for i, context  in enumerate(contexts):
            context = context.replace("\n", " ")
            if (len(context) <= 80):  context_to_display = context
            else:   context_to_display = f"{context[:40]}...{context[-40:]}"
            print(f"[ACTION REPLY CHAT CONTEXT #{i+1}]: {context_to_display}")
          
          # Evaluate the answer
          evaluation_result = await self.evaluator_component.evaluate_response(chat_message, answer, contexts, ["correctness", "faithfulness", "relevancy"])
          evaluation_passing = evaluation_result['evaluation_passing']
          print(f"[EVALUATION RESULT] {evaluation_result}")

          # Add notes if it does not pass
          if (not evaluation_passing):
            previous_iteration_notes.append(evaluation_result)

        # Increment attempt
        attempt += 1
        if (not evaluation_passing):
          if (attempt >= max_attempts):
            raise Exception(f"Model cannot answer this query after {max_attempts} attempts. The evaluations thresholds are not satisfied.")
    
    except Exception as e:
      print(f"[ERROR ACTION REPLY CHAT] Error occured while processing action reply chat: {e}")
      # LLM should explain to user about the error
      error_prompt = self.prompt_generator_component.generate_prompt_error(user_query=chat_message)
      answer, _ = await self.model_component.answer(error_prompt, is_direct=True)
    
    finally:
      # Clean answer
      answer = clean_quotation_string(answer)
      # Store in bot's reply memory
      await self.memory_component.store(sender_id, {"role": "bot", "content" : answer})
      # Refresh tools after use
      self.model_component.refresh_tools(sender_id)
      # Return answer
      return answer


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
      evaluation_passing = False
      previous_iteration_notes = []
      while (not evaluation_passing):
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
        print(f"[ACTION POST CAPTION] Attempt {attempt+1} of {max_attempts}. \nCaption: {caption_message}")          
        
        if (caption_message is None):
          previous_iteration_notes.append({
            "iteration": attempt,
            "your_answer" : None,
            "evaluator": "model",
            "reason_of_rejection": "Model cannot generate caption."
          })

        # Condition caption_message is not None
        else:
          # Prepare contexts for evaluation
          keywords_str = ", ".join(caption_keywords)
          contexts = [f"Here is the image description: {img_description}", f"Here are the keywords: {keywords_str}"]  
          
          # Evaluate the answer
          evaluation_result = await self.evaluator_component.evaluate_response("Create a caption for an Instagram post", caption_message, contexts, ["relevancy"])  
          evaluation_passing = evaluation_result['evaluation_passing']
          print(f"[EVALUATION RESULT] {evaluation_result}")
          
          # Add note if does not pass
          if (not evaluation_passing):
            previous_iteration_notes.append(evaluation_result)

        # Increment attempt
        attempt += 1
        if (not evaluation_passing):
          if (attempt >= max_attempts):
            raise Exception(f"Model cannot answer this query after {max_attempts} attempts. The evaluations thresholds are not satisfied.")
        
    except Exception as e:
      print(f"[ERROR ACTION POST] Error occured while processing action post caption: {e}")
      user_query = f"Make a post caption with image description: {img_description}, keywords: {caption_keywords}, additional context: {additional_context}"
      error_prompt = self.prompt_generator_component.generate_prompt_error(user_query=user_query)
      answer, _ = await self.model_component.answer(error_prompt, is_direct=True)
    
    finally:
      # Return answer regardless the condition
      answer = clean_quotation_string(caption_message)
      return answer


  async def action_schedule_post(self, img_url: str, caption_message: str) -> None:
    """
    Operate the action schedule post
    """
    try:
      # Load posts in database pinecone
      await self._load_tools_rag("posts", "rag_tools_for_post_data", "Used to provide examples of posts from Influencers", "self")
      
      # Initiate attempts
      max_attempts = 3 
      attempt = 0
      while (attempt <= max_attempts):
        # Generate prompt
        prompt = self.prompt_generator_component.generate_prompt_choose_schedule_post(caption_message)
      
        # Ask the LLM
        answer, contexts = await self.model_component.answer(prompt, tool_user_id="self")
        print(f"[ACTION SCHEDULE POST] Attempt {attempt+1} of {max_attempts}. \nCaption: {caption_message} \nAnswer: {answer}")


        # If the answer is not None, stop iteration
        if (answer is not None):
          for i, context  in enumerate(contexts):
            context = context.replace("\n", " ")
            if (len(context) <= 80):  context_to_display = context
            else:   context_to_display = f"{context[:40]}...{context[-40:]}"
            print(f"[ACTION SCHEDULE POST CONTEXT #{i+1}]: {context_to_display}")
          break

        # Increment attempt
        attempt += 1
        if (attempt == max_attempts):
          raise Exception(f"Model cannot choose the schedule time")
      
      # Process answer
      json_answer = json.loads(answer)
      schedule_time = json_answer['schedule_time']
      reason = json_answer['reason']

      # TODO Scheduler
      # Write here

      # TODO To be removed
      # Do immediate post
      self.output_gateway_component.request_post(img_url, caption_message)

      # Refresh tools
      self.model_component.refresh_tools("self")
      return schedule_time, reason
  
    except Exception as e:
      print(f"[ERROR ACTION SCHEDULE POST] Error occured in executing `schedule post`: {e}")
      return None, None


  #########################################
  ######## INTERNAL TRIGGER ACTION ########
  #########################################

  async def decide_action(self) -> None:
    """
    Decide action based on the current conditions and statistics
    This is the main entry point for the agent to decide what to do next.
    """
    statistics = self.postgres_connector_component.get_statistics_data(self.user_id)
    observations = self.action_generator_component.observe_statistics(statistics)
    print(f"[ACTION OBSERVATION] Acquired observations: {observations}")

    # Get the community
    communities = await self.choose_community()

    # Max 5 times of action decision
    for itr in range(5):
      action, state = self.action_generator_component.decide_action(observations, itr)
      print(f"[ACTION DECISION] {itr+1}.  action \"{action}\" in state \"{state}\"")

      if (action == "like"):
        await self.action_like(communities)
      elif (action == "follow"):
        await self.action_follow(communities)
      elif (action == "comment"):
        await self.action_comment(communities)
      else:
        return
      
      # Give time delay
      sleep_time = random.randint(6, 18)
      print(f"[ACTION TIME SLEEP] Delay for {sleep_time} seconds")
      time.sleep(sleep_time)

  
  async def choose_community(self, 
                             top_k: int = 20, 
                             threshold: float = 0.5) -> list[dict]:
    """
    LLM decide which community it wants to got into for actions like, follow, and comment
    """
    try:
      # Load the data
      query_engine = self._construct_retrieval_system("communities", top_k)

      # Prepare to generate prompt
      persona_str = self.persona_component.get_persona_str()
      # prompt = self.prompt_generator_component.generate_prompt_choose_community(persona_str)
      prompt = f"Choose the most suitable community out of this persona: \n {persona_str}"
      
      # Retrieve data
      community_id_list = []
      nodes = query_engine.retriever.retrieve(prompt)
      for i, node in enumerate(nodes):
          similarity_score = round(node.score, 4)
          print(f"[CHOOSE COMMUNITY {i+1}] Score: {similarity_score}")
          community_str = node.text
          community_id = int(community_str.split("\n")[0].split(":")[1].strip())
          community_label = community_str.split("\n")[1].split(":")[1].strip()
          print(f"[CHOOSE COMMUNITY {i+1}] ID | Label: {community_id} | {community_label}")
          if(similarity_score > threshold):
            community_id_list.append(community_id)

      # Get from mongodb
      get_filter_using_id = {"community_id": {"$in": community_id_list}}
      community_data = self.mongo_connector_component.get_data("communities", get_filter_using_id)
      print(f"[CHOOSE COMMUNITY] Fetched {len(community_data)} similiar communities")
      return community_data

    except Exception as e:
      print(f"[ERROR CHOOSE COMMUNITY] Error occured in executing `choose community`: {e}")


  async def action_follow(self, communities: list[dict]) -> None:
    """
    Operate the action follow
    """
    try:
      mongo_collection_name = "communities"
      
      found = False
      chosen_influencer = None
      # Pick certain influencer
      for community in communities:
        community_id = community['community_id']
        # Get influencer
        influencers = community['influencers']
        # Traverse the influencer
        for influencer in influencers:
          if (not "mark_follow" in influencer):
            found = True
            chosen_influencer = influencer
            break
          # Case mark_follow list already in post
          elif (self.user_id not in influencer['mark_follow'] and str(self.user_id) not in influencer['mark_follow']):
            found = True
            chosen_influencer = influencer
            break
        # Get out of loop if it is found
        if (found):
          break
      # Handle if not found
      if (not found):
        raise Exception("All fetched similar data has been marked")

      # Get Influencer
      influencer_id = chosen_influencer['id']
      influencer_username = chosen_influencer['username']

      # Request
      is_success = self.output_gateway_component.request_follow(influencer_username)
      if (is_success):
        # Mark influencer
        if ('mark_follow' in chosen_influencer and isinstance(chosen_influencer['mark_follow'], list)):
          chosen_influencer['mark_follow'].append(self.user_id)
          print(f"[ACTION FOLLOW] Mark array has been created for {self.user_id}")
        else:
          chosen_influencer['mark_follow'] = [self.user_id]
          print(f"[ACTION FOLLOW] {self.user_id} is inserted to mark array")
        self.mongo_connector_component.update_one_data(mongo_collection_name, {"community_id": community_id}, {"influencers": influencers})
        print(f"[ACTION FOLLOW] Follow influencer {influencer_username} with influencer_id {influencer_id} in community {community_id}")
      
    except Exception as e:
      print(f"[ERROR ACTION FOLLOW] Error occured in executing `follow`: {e}")


  async def action_like(self, communities: list[dict]) -> None:
    """
    Operate the action like
    """
    try:
      mongo_collection_name = "communities"
      
      found = False
      chosen_post = None
      # Pick certain post
      for community in communities:
        community_id = community['community_id']
        # Get post
        posts = community['posts']
        # Traverse the post
        for post in posts:
          if (not "mark_like" in post):
            found = True
            chosen_post = post
            break
          # Case mark_like list already in post
          elif (self.user_id not in post['mark_like'] and str(self.user_id) not in post['mark_like']):
            found = True
            chosen_post = post
            break
        # Get out of loop if it is found
        if (found):
          break
      # Handle if not found
      if (not found):
        raise Exception("All fetched similar data has been marked")

      # Get Influencer
      post_id = chosen_post['id']

      # Request
      is_success = self.output_gateway_component.request_like(post_id)
      if (is_success):
        # Mark post
        if ('mark_like' in chosen_post and isinstance(chosen_post['mark_like'], list)):
          chosen_post['mark_like'].append(self.user_id)
          print(f"[ACTION LIKE] Mark array has been created for {self.user_id}")
        else:
          chosen_post['mark_like'] = [self.user_id]
          print(f"[ACTION LIKE] {self.user_id} is inserted to mark array")
        self.mongo_connector_component.update_one_data(mongo_collection_name, {"community_id": community_id}, {"posts": posts})
        print(f"[ACTION LIKE] Like post with post_id {post_id} in community {community_id}")

    except Exception as e:
      print(f"[ERROR ACTION LIKE] Error occured in executing `like`: {e}")


  async def action_comment(self, communities: list[dict]) -> None:
    """
    Operate the action comment
    """
    try:
      mongo_collection_name = "communities"
      
      found = False
      chosen_post = None
      # Pick certain post
      for community in communities:
        community_id = community['community_id']
        # Get post
        posts = community['posts']
        # Traverse the post
        for post in posts:
          if (not "mark_comment" in post):
            found = True
            chosen_post = post
            break
          # Case marked_comment list already in post
          elif (self.user_id not in post['mark_comment'] and str(self.user_id) not in post['mark_comment']):
            print("yang ini")
            found = True
            chosen_post = post
            break
        # Get out of loop if it is found
        if (found):
          break
      # Handle if not found
      if (not found):
        raise Exception("All fetched similar data has been marked")

      # Get Influencer
      post_id = chosen_post['id']
      post_caption = chosen_post["caption"]
      comments = chosen_post['comments']
      max_length = 20
      selected_comments = comments[:min(max_length, len(comments))]
      selected_comments_str = [comment['content'] for comment in selected_comments]

      # Generate prompt
      prompt = self.prompt_generator_component.generate_prompt_comment(post_caption, selected_comments_str)
      
      # Make comment
      comment_message, _ = await self.model_component.answer(prompt, is_direct=True)
      comment_message = clean_quotation_string(comment_message)
      print(f"[RESULTED ACTION COMMENT] Comment message: {comment_message}")

      # Request
      is_success = self.output_gateway_component.request_comment(post_id, comment_message)
      if (is_success):
        # Mark post
        if ('mark_comment' in chosen_post and isinstance(chosen_post['mark_comment'], list)):
          chosen_post['mark_comment'].append(self.user_id)
          print(f"[ACTION COMMENT] Mark array has been created for {self.user_id}")
        else:
          chosen_post['mark_comment'] = [self.user_id]
          print(f"[ACTION LIKE] {self.user_id} is inserted to mark array")
        self.mongo_connector_component.update_one_data(mongo_collection_name, {"community_id": community_id}, {"posts": posts})
        print(f"[ACTION COMMENT] Comment post with post_id {post_id} in community {community_id}")
        
    except Exception as e:
      print(f"[ERROR ACTION COMMENT] Error occured in executing `comment`: {e}")


 


  ##############################
  ######## PROCESS DATA ########
  ##############################

  """
  Should only be run manually
  It is run to convert the data from Document type in Mongo to Vector in Pinecone
  """

  def process_data_hotel(self) -> None:
    """
    Process data hotel, "migrate" it from mongodb document to pinecone vector
    """
    mongo_collection_name = "hotel"
    pinecone_namespace_name = "hotels"

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
      self.pinecone_connector_component.store_data(hotel_data_parsed, pinecone_namespace_name)        
      print(f'[BATCH PROGRESS] Successfully inserted data idx {idx} to {upper_idx}')
      
      # Increment idx
      idx += length_per_batch


  def process_data_post(self) -> None:
    """
    Process data communities, "migrate" it from mongodb document to pinecone vector
    """
    mongo_collection_name = "communities"
    pinecone_namespace_name = "posts"

    # Get data from mongo
    communities = self.mongo_connector_component.get_data(mongo_collection_name, {})
    print(f"[FETCHED] Fetched {len(communities)} communities")

    # Insert data as batch
    idx = 0
    n_batch = 20
    length_per_batch = (len(communities)//n_batch)+1
    while (idx < len(communities)):
      # Set batch indices
      batch_post_data = []
      upper_idx = min(idx+length_per_batch, len(communities))
      curr_batch_communities = communities[idx : upper_idx]

      # Iterate data in the current batch list
      for community in curr_batch_communities:
        community_id = community['community_id']
        posts = community['posts']
        # Iterate posts in community
        for post in posts:
          post_data = f"""Community ID: {community_id}\n""" \
                      f"""Post Caption: \"{post['caption']}\"\n""" \
                      f"""Post Created Time: {post['posted_at']}\n"""\
                      f"""Comment Ammount: {len(post['comments'])}\n"""
          batch_post_data.append(post_data)

      # Preprocess
      batch_post_docs = text_to_document(batch_post_data)
      batch_post_parsed = parse_documents(batch_post_docs)
      
      # Insert data to pinecone
      self.pinecone_connector_component.store_data(batch_post_parsed, pinecone_namespace_name)        
      print(f'[BATCH PROGRESS] Successfully inserted data idx {idx} to {upper_idx}')

      # Increment idx
      idx += length_per_batch


  def process_data_association_rule(self) -> None:
    """
    Process data association rule, "migrate" it from mongodb document to pinecone vector
    """
    mongo_collection_name = "association-rule"
    pinecone_namespace_name = "association_rules"

    # Get data from mongo
    asso_rules = self.mongo_connector_component.get_data(mongo_collection_name, {})
    print(f"[FETCHED] Fetched {len(asso_rules)} asso_rules")

    asso_rule_string_list = []
    # Iterate association rules
    for asso_rule in asso_rules:
      antecedents = asso_rule['antecedent']
      consequents = asso_rule['consequent']

      antecedents_string = "Antecedents:\n"
      for i, antecedent in enumerate(antecedents):
        antecedents_string += f"{i+1}. {antecedent['place']}\n"

      consequents_string = "Consequents:\n"
      for i, consequent in enumerate(consequents):
        consequents_string += f"{i+1}. {consequent['place']}\n"

      asso_rule_string =  "Here is an insight of recommendation from data mining process.\n" \
                          "The data is about association rule of hotels. " \
                          "Therefore, this data can be used to link as a recommendation system for hotels.\n" \
                          "The data consist of antecedents and consequents. If user ask or talk about hotels in antecedents, you can recommend the hotels in consequents.\n"                   
      asso_rule_string += antecedents_string
      asso_rule_string += consequents_string

      # Append to list
      asso_rule_string_list.append(asso_rule_string)
    
    # Preprocess
    asso_rule_docs_list = text_to_document(asso_rule_string_list)
    asso_rule_parsed = parse_documents(asso_rule_docs_list)
    
    # Insert data to pinecone
    self.pinecone_connector_component.store_data(asso_rule_parsed, pinecone_namespace_name)        
    print(f'[BATCH PROGRESS] Successfully inserted data')


  def process_data_tourist_attraction(self) -> None:
    """
    Process data tourism places, "migrate" it from mongodb document to pinecone vector
    """
    mongo_collection_name = "objek-wisata"
    pinecone_namespace_name = "tourist_attractions"

    # Get attraction data from mongo
    attractions = self.mongo_connector_component.get_data(mongo_collection_name, {})
    print(f"[FETCHED] Fetched {len(attractions)} attractions")

    idx = 0
    n_batch = 20
    length_per_batch = (len(attractions)//n_batch)+1
    while (idx < len(attractions)):
      # Set batch indices
      attraction_docs = []
      upper_idx = min(idx+length_per_batch, len(attractions))
      curr_batch_attractions = attractions[idx : upper_idx]

      # Iterate data in the current batch list
      for attraction in curr_batch_attractions:
        attraction_string_data = attraction_data_to_string_list(attraction)
        documents_list = text_to_document(attraction_string_data)
        attraction_docs.extend(documents_list)
      
      # Parse attraction data
      attraction_data_parsed = parse_documents(attraction_docs)
      # Insert to pinecone
      self.pinecone_connector_component.store_data(attraction_data_parsed, pinecone_namespace_name)         
      print(f'[BATCH PROGRESS] Successfully inserted data idx {idx} to {upper_idx}')
      
      # Increment idx
      idx += length_per_batch
    

  async def process_labelling_communities(self, limit=None) -> None:
    """"
      Give label to all communities based on influencers' bios, posts' tags, captions, and comments
    """
    try:
      mongo_collection_name = "communities"
      communities = self.mongo_connector_component.get_data(mongo_collection_name, {})
      
      if limit:
        communities = communities[:limit]
        print(f"Processing only first {limit} communities")
      
      
      for community in communities: 
        community_id = community.get("community_id", "unknown")
        influencers = community.get("influencers", [])
        posts = community.get("posts", [])
        
        # Skip if no data to analyze
        if not influencers and not posts:
          print(f"Community {community_id} has no influencers or posts, skipping...")
          continue
        
        # Generate label using LLM
        label, description = await self._generate_community_label(influencers, posts)
        print(label, description)
        
        # Store to Mongo DB
        if label and description:
          # Update community with generated label
          self.mongo_connector_component.update_one_data(
            mongo_collection_name,
            {"community_id": community_id},
            {"label": label, "description": description}
          )
          print(f"Labeled community {community_id}: {label} with description :{description}")
        else:
          print(f"Failed to generate label for community {community_id}")

        
        # Also store to pinecone
        pinecone_namespace_name = "communities"
        community_str = f"community_id: {community_id}\n" \
                        f"label: {label}\n" \
                        f"description: {description}\n"
        community_docs = text_to_document([community_str])
        community_parsed = parse_documents(community_docs)
        self.pinecone_connector_component.store_data(community_parsed, pinecone_namespace_name)    
      
    except Exception as e: 
      print(f"Error in labelling_communities: {str(e)}")
      import traceback
      traceback.print_exc()


  async def _generate_community_label(self, influencers: list, posts: list) -> tuple[str]:
    """
    Generate a community label based on influencers' biographies, posts' tags, captions, and comments
    """
    try:
      # Prepare context from influencers
      influencer_context = ""
      if influencers:
        influencer_context = "Influencers in this community:\n"
        for i, influencer in enumerate(influencers[:5]):  # Limit to 5 influencers to avoid too long context
          username = influencer.get("username", "unknown")
          biography = influencer.get("biography", "")
          if biography:
            influencer_context += f"- {username}: {biography}\n"
          else:
            influencer_context += f"- {username}: (no biography)\n"
      
      # Prepare context from posts
      post_context = ""
      if posts:
        post_context = "Posts in this community:\n"
        for i, post in enumerate(posts[:10]):  # Limit to 10 posts to avoid too long context
          caption = post.get("caption", "")[:200]  # Limit caption length
          tags = post.get("tags", [])
          comments = post.get("comments", [])
          
          post_context += f"Post {i+1}:\n"
          if caption:
            post_context += f"  Caption: {caption}...\n"
          if tags:
            post_context += f"  Tags: {', '.join(tags[:10])}\n"  # Limit to 10 tags
          if comments:
            comment_preview = ', '.join([comment.get("text", "")[:50] for comment in comments[:3]])  # First 3 comments
            post_context += f"  Sample Comments: {comment_preview}...\n"
          post_context += "\n"
      
      # Generate prompt for community labeling
      prompt = self.prompt_generator_component.generate_community_labeling_prompt(influencer_context, post_context)
      
      # Get response from LLM
      response, _ = await self.model_component.answer(prompt, is_direct=True)
      response_json = json.loads(response)
      label = response_json['label']
      description = response_json['description']
      
      return (label.strip(), description.strip())
      
    except Exception as e:
      print(f"Error generating community label: {str(e)}")
      return "", ""

