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
    self.pinecone_connector_component = PineconeConnector()
    self.mongo_connector_component = MongoConnector()
    self.postgres_connector_component = PostgresConnector()
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


  #######################
  ######## OTHER ########
  #######################

  def run(self) -> None:
    """
    Run the agent, this is the main entry point for the agent to start working
    """
    print("[AGENT RUN] Agent is running...")
    self.input_gateway_component.run()


  async def decide_action(self) -> None:
    """
    Decide action based on the current conditions and statistics
    This is the main entry point for the agent to decide what to do next.
    """
    statistics = self.postgres_connector_component.get_statistics_data(self.user_id)
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
        await self.action_comment()
      else:
        return
      
      # Give time delay
      sleep_time = random.randint(5, 15)
      print(f"[ACTION TIME SLEEP] Delay for {sleep_time} seconds")
      time.sleep(sleep_time)
      

  async def summarize_and_store_memory(self, sender_id: str, memory_data: list[dict]) -> bool:
    """
    Summarize memory and store it to vector database
    """
    # Make the summary
    try:
      prompt = self.prompt_generator_component.generate_prompt_summarize_memory(memory_data)
      summary, _ = await self.model_component.answer(prompt)
      
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
    

  async def _load_tools_rag(self, pinecone_namespace_name : str, metadata_name: str, metadata_description: str):
    """
    Load tools to be inserted to array of tools and later be used by ReAct
    """
    vector_store, storage_context = self.pinecone_connector_component.get_vector_store(pinecone_namespace_name)
    await self.model_component.load_data(
      vector_store, 
      storage_context, 
      metadata_name,
      metadata_description)
    print(f"[LOADING TOOLS] Inserting tools for RAG: {pinecone_namespace_name}")


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
      await self._load_tools_rag("hotels", "rag_tools_for_hotels_data", "Used to answer hotels-related query based on retrieved documents")
      # Then asso-rules
      await self._load_tools_rag("association_rules", "rag_tools_for_association_rules_data", "Used to recommend system for hotel based on its antecedent-consequent relation based on retrieved documents")
      # Then tourist attractions
      await self._load_tools_rag("tourist_attractions", "rag_tools_for_tourist_attractions_data", "Used to answer tourist-attractions-related query based on retrieved documents")
            
      # Load the long-term memory from pinecone
      chat_memory_namespace_name = f"chat_bot[{self.user_id}]_sender[{sender_id}]"
      if (self.pinecone_connector_component.is_namespace_exist(chat_memory_namespace_name)):
        await self._load_tools_rag(chat_memory_namespace_name, f"rag_tools_for_memory_chat_with_{sender_id}", f"Used to help answering question from {sender_id} based on previous occurences")

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
        print(f"[ACTION REPLY CHAT] Attempt {attempt+1} of {max_attempts}. \nQuery: {chat_message} \nAnswer: {answer}")
        if (answer is not None):

          # Display contexts (for printing only)
          for i, context  in enumerate(contexts):
            print(f"[ACTION REPLY CHAT CONTEXT #{i+1}]: \n"\
                  f"{context}")
          
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
      answer = clean_quotation_string(answer)

      # Store in bot's reply memory
      await self.memory_component.store(sender_id, {"role": "bot", "content" : answer})

      return answer
    
    except Exception as e:
      print(f"[ERROR ACTION REPLY CHAT] Error occured while processing action reply chat: {e}")

      # LLM should explain to user
      error_prompt = self.prompt_generator_component.generate_prompt_error(user_query=chat_message)
      answer, _ = await self.model_component.answer(error_prompt)
      answer = clean_quotation_string(answer)

      # Store in bot's reply memory
      await self.memory_component.store(sender_id, {"role": "bot", "content" : answer})

      return answer

  #########################################
  ######## INTERNAL TRIGGER ACTION ########
  #########################################


  def action_follow(self) -> None:
    """
    Operate the action follow
    """
    try:
      mongo_collection_name = "communities"
      communities = self.mongo_connector_component.get_data(mongo_collection_name, {})
      
      found = False
      chosen_influencer = None
      visited_communities_id = []
      # Pick certain influencer
      while (not found):
        # Randomly pick community
        community = random.choice(communities)
        community_id = community['community_id']
        while (community_id in visited_communities_id):
          # If the community has been visited
          community = random.choice(communities)
          community_id = community['community_id']

        # Get influencer
        influencers = community['influencers']
        # Traverse the influencer
        for influencer in influencers:
          if (not "marked_follow" in influencer):
            found = True
            chosen_influencer = influencer
            break
        
        # For context if all the influencer is already been marked
        if (not found):
          # Append community_id to visited_communities_list
          if (community_id not in visited_communities_id):
            visited_communities_id.append(community_id)
          if (len(visited_communities_id) == len(communities)):
            print(f"[NO AVAILABLE DATA] All data has been marked")

      # Get Influencer
      influencer_id = chosen_influencer['id']
      influencer_username = chosen_influencer['username']

      # Request
      is_success = self.output_gateway_component.request_follow(influencer_username)
      if (is_success):
        # Mark influencer
        chosen_influencer['mark_follow'] = True
        self.mongo_connector_component.update_one_data(mongo_collection_name, {"community_id": community_id}, {"influencers": influencers})
        print(f"[ACTION FOLLOW] Follow influencer {influencer_username} with influencer_id {influencer_id} in community {community_id}")
      
    except Exception as e:
      print(f"[ERROR ACTION FOLLOW] Error occured in executing `follow`: {e}")


  def action_like(self) -> None:
    """
    Operate the action like
    """
    try:
      mongo_collection_name = "communities"
      communities = self.mongo_connector_component.get_data(mongo_collection_name, {})

      found = False
      chosen_post = None
      visited_communities_id = []
      # Pick certain post
      while (not found):
        # Randomly pick community
        community = random.choice(communities)
        community_id = community['community_id']
        if (len(community['posts']) == 0 and community_id not in visited_communities_id):
          visited_communities_id.append(community_id)
        # Iterate until find the correct one
        while (community_id in visited_communities_id):
          # If the community has been visited
          community = random.choice(communities)
          community_id = community['community_id']
          if (len(community['posts']) == 0 and community_id not in visited_communities_id):
            visited_communities_id.append(community_id)

        # Get post
        posts = community['posts']
        sorted_posts = sorted(posts, key=lambda p: len(p['comments']), reverse=True)
        # Traverse the posts
        for post in sorted_posts:
          if (not "marked_like" in post):
            found = True
            chosen_post = post
            break
        
        # For context if all the influencer is already been marked
        if (not found):
          # Append community_id to visited_communities_list
          if (community_id not in visited_communities_id):
            visited_communities_id.append(community_id)
          if (len(visited_communities_id) == len(communities)):
            print(f"[NO AVAILABLE DATA] All data has been marked")

      # Get Influencer
      post_id = chosen_post['id']

      # Request
      is_success = self.output_gateway_component.request_like(post_id)
      if (is_success):
        # Mark post
        chosen_post['mark_like'] = True
        self.mongo_connector_component.update_one_data(mongo_collection_name, {"community_id": community_id}, {"posts": posts})
        print(f"[ACTION LIKE] Like post with post_id {post_id} in community {community_id}")

    except Exception as e:
      print(f"[ERROR ACTION LIKE] Error occured in executing `like`: {e}")



  async def action_comment(self) -> None:
    """
    Operate the action comment
    """
    try:
      mongo_collection_name = "communities"
      communities = self.mongo_connector_component.get_data(mongo_collection_name, {})

      found = False
      chosen_post = None
      visited_communities_id = []
      # Pick certain post
      while (not found):
        # Randomly pick community
        community = random.choice(communities)
        community_id = community['community_id']
        if (len(community['posts']) == 0 and community_id not in visited_communities_id):
          visited_communities_id.append(community_id)
        # Iterate until find the correct one
        while (community_id in visited_communities_id):
          # If the community has been visited
          community = random.choice(communities)
          community_id = community['community_id']
          if (len(community['posts']) == 0 and community_id not in visited_communities_id):
            visited_communities_id.append(community_id)

        # Get post
        posts = community['posts']
        sorted_posts = sorted(posts, key=lambda p: len(p['comments']), reverse=True)
        # Traverse the posts
        for post in sorted_posts:
          if (not "marked_comment" in post):
            found = True
            chosen_post = post
            break
        
        # For context if all the influencer is already been marked
        if (not found):
          # Append community_id to visited_communities_list
          if (community_id not in visited_communities_id):
            visited_communities_id.append(community_id)
          if (len(visited_communities_id) == len(communities)):
            print(f"[NO AVAILABLE DATA] All data has been marked")

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
      comment_message, _ = await self.model_component.answer(prompt)
      comment_message = clean_quotation_string(comment_message)

      # Request
      is_success = self.output_gateway_component.request_comment(post_id, comment_message)
      if (is_success):
        # Mark post
        chosen_post['mark_comment'] = True
        self.mongo_connector_component.update_one_data(mongo_collection_name, {"community_id": community_id}, {"posts": posts})
        print(f"[ACTION COMMENT] Comment post with post_id {post_id} in community {community_id}")
        
    except Exception as e:
      print(f"[ERROR ACTION COMMENT] Error occured in executing `comment`: {e}")


  async def action_schedule_post(self, img_url: str, caption_message: str) -> None:
    """
    Operate the action schedule post
    """
    try:
      # Load posts in database pinecone
      await self._load_tools_rag("communities", "rag_tools_for_post_data", "Used to provide examples of posts from Influencers")
      
      # Initiate attempts
      max_attempts = 3 
      attempt = 0
      while (attempt <= max_attempts):
        # Generate prompt
        prompt = self.prompt_generator_component.generate_prompt_choose_schedule_post(caption_message)
      
        # Ask the LLM
        answer, _ = await self.model_component.answer(prompt)
        print(f"[ACTION SCHEDULE POST] Attempt {attempt+1} of {max_attempts}. \nCaption: {caption_message} \nAnswer: {answer}")


        # If the answer is not None, stop iteration
        if (answer is not None):
          break

        # Increment attempt
        attempt += 1
        if (attempt == max_attempts):
          raise Exception(f"Model cannot choose the schedule time")
      
      # Process answer
      json_answer = json.loads(answer)
      schedule_time = json_answer['schedule_time']
      reason = json_answer['reason']
      print(schedule_time, reason)
  
    except Exception as e:
      print(f"[ERROR ACTION SCHEDULE POST] Error occured in executing `schedule post`: {e}")


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
        caption_message, _ = await self.model_component.answer(prompt)
        print(f"[ACTION POST CAPTION] Attempt {attempt+1} of {max_attempts}. \nCaption: {caption_message}")          
        
        if (caption_message is not None):
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
      answer, _ = await self.model_component.answer(error_prompt)
      answer = clean_quotation_string(answer)
      return answer


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
      _, storage_context = self.pinecone_connector_component.get_vector_store(pinecone_namespace_name)
      self.pinecone_connector_component.store_data(hotel_data_parsed, storage_context, self.model_component.embed_model)      
      print(f'[BATCH PROGRESS] Successfully inserted data idx {idx} to {upper_idx}')
      
      # Increment idx
      idx += length_per_batch


  def process_data_post(self) -> None:
    """
    Process data communities, "migrate" it from mongodb document to pinecone vector
    """
    mongo_collection_name = "communities"
    pinecone_namespace_name = "communities"

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
      _, storage_context = self.pinecone_connector_component.get_vector_store(pinecone_namespace_name)
      self.pinecone_connector_component.store_data(batch_post_parsed, storage_context, self.model_component.embed_model)      
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
                          "The data is about association rule of hotels." \
                          "Therefore, this data can be used to link as a recommendation system for hotels.\n" \
                          "The data consist of antecedents and consequents. If user talk about hotels in antecedents, you can recommend the hotels in consequents.\n"                   
      asso_rule_string += antecedents_string
      asso_rule_string += consequents_string

      # Append to list
      asso_rule_string_list.append(asso_rule_string)
    
    # Preprocess
    asso_rule_docs_list = text_to_document(asso_rule_string)
    asso_rule_parsed = parse_documents(asso_rule_docs_list)
    
    # Insert data to pinecone
    _, storage_context = self.pinecone_connector_component.get_vector_store(pinecone_namespace_name)
    self.pinecone_connector_component.store_data(asso_rule_parsed, storage_context, self.model_component.embed_model)      
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
      _, storage_context = self.pinecone_connector_component.get_vector_store(pinecone_namespace_name)
      self.pinecone_connector_component.store_data(attraction_data_parsed, storage_context, self.model_component.embed_model)      
      print(f'[BATCH PROGRESS] Successfully inserted data idx {idx} to {upper_idx}')
      
      # Increment idx
      idx += length_per_batch
      



      
