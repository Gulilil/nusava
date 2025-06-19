from llama_index.core.prompts import PromptTemplate
from datetime import datetime

PROMPT_TEMPLATE = """Definition:
{persona_subprompt}.
---------------------
{context_subprompt}
{additional_subprompt}
{previous_iteration_notes_subprompt}
---------------------
Instruction:
Given this information, answer the query.
Query: {query_str}
"""

class PromptGenerator():

  def __init__(self, 
               persona_component: object):
    """
    Instantiate the template
    """
    self._prompt_template = PromptTemplate(PROMPT_TEMPLATE)
    self._persona_component = persona_component

  # GENERATE SUBPROMPT
  ##############################
  
  def generate_subprompt_persona(self) -> str:
    age, style, occupation = self._persona_component.get_typing_style()
    persona_subprompt = f"You are {age} years old with the occupation of {occupation}. You have the characterstics to be {style}"
    persona_subprompt += " This is a crucial part of your identity, so make sure to always follow this persona in your responses."
    return persona_subprompt


  def generate_subprompt_example(self, examples: list[dict]) -> str:
    """
    Prepare the example part of the prompt

    Format of examples:
    [
      {"question": "...", "answer": "..."}, 
      ..., 
      {"question": "...", "answer": "..."}
    ]
    """
    example_subprompt = "Examples:\n"
    if (examples is None or len(examples) == 0):
      example_subprompt += "I have no provided examples for this query."
    else:
      example_subprompt += "Here is some provided examples to guide you answer the question."
      for i, example in enumerate(examples):
        example_subprompt += "\n"
        example_subprompt += f"Query {i+1}. {example['question']}"
        example_subprompt += "\n"
        example_subprompt += f"Answer {i+1}. {example['answer']}"
    return example_subprompt
  

  def generate_subprompt_context(self, context: str) -> str:
    """
    Prepare the context part of the prompt
    """
    context_subprompt = "Context:\n"
    if (context is not None):
      context_subprompt += "Here I provide context regarding this query.\n"
      context_subprompt += context
    else:
      context_subprompt += "I have no provided context for this query."
    return context_subprompt


  def generate_subprompt_previous_iteration_notes(self, previous_iteration_notes: list[dict]) -> str:
    """
    Prepare the previous iteration notes part of the prompt
    """
    previous_iteration_notes_subprompt = "Previous Iteration Notes:\n"
    if (previous_iteration_notes is not None and len(previous_iteration_notes) > 0):
      previous_iteration_notes_subprompt += "Here are some notes from your previous iterations. This notes are important to be considered in your answer.\n"
      previous_iteration_notes_subprompt += "Your answer are expected to pass the evaluator. But, here I provide some notes on your previous answers and the reason it does not pass the evaluator.\n"
      for notes in previous_iteration_notes:
        previous_iteration_notes_subprompt += "{\n"
        for key, value in notes.items():
          previous_iteration_notes_subprompt += f"{key}: {value}\n"
        previous_iteration_notes_subprompt += "}\n"
    else:
      previous_iteration_notes_subprompt += "I have no provided notes from the previous iteration. This is your first iteration"
    
    return previous_iteration_notes_subprompt

  ###############################
  ####### GENERATE PROMPT #######
  ###############################

  ######## SUPPORTING PROMPT ########

  def generate_prompt_error(self, user_query: str) -> str:
    """
    Generate a prompt for error message
    """
    context_str = "You are expected to answer the user query, but you cannot answer this query due to some error."
    context_str += f"\nHere is the user query: \"{user_query}\""

    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context_str)
    additional_subprompt =  "You are expected to explain to user concisely yet informative." \
                            "Make sure to not answer more than 1 paragraph."
    previous_iteration_notes_subprompt = ""
    query_str = "Explain to user that you cannot answer this query."

    return self._prompt_template.format(persona_subprompt=persona_subprompt,
                                  context_subprompt=context_subprompt,
                                  additional_subprompt=additional_subprompt,
                                  previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                                  query_str=query_str)
  

  def generate_prompt_summarize_memory(self, memory_data: list[dict]) -> str:
    """
    Generate a prompt for summarizing memory
    """
    context_str = "You are expected to summarize this memory. This is the memory of the chat between you and specific user."
    context_str += "In these messages, you have the role `bot` while the user have the role `user`.\n"
    context_str += "Here is the memory data:\n\n"
    for i, memory in enumerate(memory_data): 
      timestamp_str = memory['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
      context_str += f"Memory {i+1}. {memory['role']} [{timestamp_str}]: \"{memory['content']}\"\n"

    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context_str)
    additional_subprompt =  "You do not have to be so concise when summarizing." \
                            "However, you have to make sure that you are not missing any critical points of the chat." \
                            "This memory will later be used for RAG system. Therefore, you need to summarize this in form of a document."
    previous_iteration_notes_subprompt = ""
    query_str = "Summarize this memory data."

    return self._prompt_template.format(persona_subprompt=persona_subprompt,
                                  context_subprompt=context_subprompt,
                                  additional_subprompt=additional_subprompt,
                                  previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                                  query_str=query_str)


  def generate_community_labeling_prompt(self, influencer_context: str, post_context: str) -> str:
    """
    Generate a prompt for community labeling
    """
    context_str = "You are analyzing a social media community to generate an appropriate label/category for it.\n"
    context_str += "Based on the influencers' biographies and posts' content (captions, tags, comments), you need to determine what this community is about.\n\n"
    
    if influencer_context:
      context_str += influencer_context + "\n"
    
    if post_context:
      context_str += post_context + "\n"
    
    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context_str)
    additional_subprompt = ("Generate a short, descriptive label (1-3 words) that best represents what this community is about. " \
                           "Focus on the main theme, topic, or niche of the community. " \
                           "Examples of good labels: 'Travel', 'Food & Cooking', 'Fashion', 'Fitness', 'Technology', 'Art & Design', etc. \n" \
                           "Aside from the label, also summarize the community and describe. Store the your summary in a description that describes the community."
                           "1-2 sentences are enough for the description as long as you think it is the most suitable way to describe the community.\n"
                           "Return your answer in this JSON format: \n" \
                           "{\n"
                           "\"label\": str,\n"\
                           "\"description\" : str\n"
                           "}\n"
                           "Do not add any other string, word, or character outside the format that has been stated.")
    previous_iteration_notes_subprompt = ""
    query_str = "What is the most appropriate label and dsecription for this community based on the provided information?"

    return self._prompt_template.format(
      persona_subprompt=persona_subprompt,
      context_subprompt=context_subprompt,
      additional_subprompt=additional_subprompt,
      previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
      query_str=query_str
    )


  # ######## CHOOSE COMMUNITY ########

  # def generate_prompt_choose_community(self, persona_str: str) -> str:
  #   """
  #   Generate a prompt for choosing community for internal trigger action
  #   """
  #   context_str =  f"You are about to do an action such as like, follow, or comment in Instagram. You are expected to choose which community you want to get into. \n" \
  #                   "Later you are provided with tools using RAG to get some data about community. " \
  #                   "You might want to use the context from this tools as your references. " \
  #                   "This community data has been processed by Data Mining module so you can assume that the data is valid." \
  #                   "The community data will consist of: the community id, the community label, and the community description. "\
  #                   "Focus on community `Label` and `Description` because this is the critical aspect you need to examine. \n" \
  #                   "You also have a certain persona that is set by the stakeholders. Here is the details of your persona: " \
  #                   "\n" \
  #                   f"{persona_str}" \
  #                   "\n" \

  #   # Setup subprompts
  #   persona_subprompt = self.generate_subprompt_persona()
  #   context_subprompt = self.generate_subprompt_context(context_str)
  #   additional_subprompt =  "You have to choose which community is the most suitable with your persona. " \
  #                           "Your end goal is to decide the community that you want to be into so it will increase the awareness of Instagram users about you." \
  #                           "Return only the id of the community. Do not add any words, strings, or characters aside from community id. \n" 
  #   previous_iteration_notes_subprompt = self.generate_subprompt_previous_iteration_notes([])
    
  #   # Setup query string
  #   query_str = "Choose the most suitable community for your persona"

  #   return self._prompt_template.format(persona_subprompt=persona_subprompt,
  #                                     context_subprompt=context_subprompt,
  #                                     additional_subprompt=additional_subprompt,
  #                                     previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
  #                                     query_str=query_str)


  ######## ACTION PROMPT ########

  def generate_prompt_reply_chat(self, new_message: str, previous_messages: list[dict] = [], previous_iteration_notes: list[dict] = []) -> str:
    """
    Generate a prompt for replying chat
    See the Class Memory for the template of the previous messages
    """
    context = "You have to be informative and clear in giving information to users. You also have to assure the correctness of the facts that you provide.\n"

    # Process previous messages
    if (len(previous_messages) > 0):
      context += "Here will be provided some of the most recent messages.\n"
      context += "You need to keep in mind that there might be other messages before this. However, they were omitted for brevity.\n"
      context += "In these messages, you have the role `bot` while the user have the role `user`.\n"
      context += "Here is the messages:\n\n"
      for i, message in enumerate(previous_messages):
        context += f"Message {i+1}. {message['role']}: \"{message['content']}\"\n"

    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context)
    # Chat does not need to have examples. It can be vary depending on the topic/ message
    additional_subprompt =  "In answering the context, please add a little of your explaination. " \
                            "Use your persona data to add a little characteristics to your answer. \n" \
                            "The correctness and relevancy to the query is important. " \
                            "However, the style and characteristics of your answer is equally important. \n" \
                            "Please stay true and faithful to your persona."
    previous_iteration_notes_subprompt = self.generate_subprompt_previous_iteration_notes(previous_iteration_notes)
    return self._prompt_template.format(persona_subprompt=persona_subprompt,
                                  context_subprompt=context_subprompt,
                                  additional_subprompt=additional_subprompt,
                                  previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                                  query_str=new_message)


  def generate_prompt_comment(self, caption: str, previous_comments: list = []) -> str:
    """
    Generate a prompt for making a comment on Instagram post
    """

    context_str = f"You are expected to make a comment on a post in Instagram with this caption: \"{caption}\"\n"
    if (previous_comments is not None):
      context_str += f"Here are some comments in the post:\n"
      for i, previous_comment in enumerate(previous_comments):
        context_str += f"Comment {i+1}: {previous_comment}\n"

    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context_str)
    additional_subprompt = ""
    previous_iteration_notes_subprompt = self.generate_subprompt_previous_iteration_notes([])
    
    # Setup query string
    query_str = "Make a comment for Instagram post based on the context. Do not use any hashtags in making the comment."

    return self._prompt_template.format(persona_subprompt=persona_subprompt,
                                  context_subprompt=context_subprompt,
                                  additional_subprompt=additional_subprompt,
                                  previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                                  query_str=query_str)


  def generate_prompt_post_caption(self, img_description: str,  keywords: list[str], additional_context: str = None,  previous_iteration_notes: list[dict] = None) -> str:
    """
    Generate a prompt for generating caption for Instagram post
    """
    keywords_str = ", ".join(keywords)
    context_str = f"You are expected to make a caption with images of this description: \"{img_description}\" and based on these keywords: \"{keywords_str}\" at the same time."
    if (additional_context is not None):
      context_str += "\n"
      context_str += f"Here are some additional context of the captions: {additional_context}"


    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context_str)
    additional_subprompt =  "Only answer the text caption without any explanation text. " \
                            "Return the answer in string format without any quotation (\") symbol."
    if (additional_context is not None):
      additional_subprompt += f" Here are some additional context: {additional_context}"
    previous_iteration_notes_subprompt = self.generate_subprompt_previous_iteration_notes(previous_iteration_notes)
    
    # Setup query string
    query_str = "Make a caption for Instagram post based on the context"

    return self._prompt_template.format(persona_subprompt=persona_subprompt,
                                      context_subprompt=context_subprompt,
                                      additional_subprompt=additional_subprompt,
                                      previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                                      query_str=query_str)
  

  def generate_prompt_choose_schedule_post(self, caption_message: str) -> str:
    
    """
    Generate a prompt for choosing schedule for uploading a post
    """
    context_str =  f"You are about to upload a post in Instagram with this caption, \"{caption_message}\". You are expected to generate the ideal time to upload the post.\n" \
                    "Later you are provided with tools using RAG to get some data about posts. " \
                    "You might want to use the context from this tools as your references. " \
                    "The post data will consist of: the post caption, the post created time, and the comments amount. "\
                    "Focus on `Post Created Time` because this is the critical aspect you need to examine. " \
                    "If possible, choose post data you think similar or relevan to the post caption or has more comments amount. " \
                    "\n\n" \
                    "You don't need to be so strict with searching similar post caption." \
                    "Lower your threshold. You can choos a post as a reference even if it is just a slightly similar." \

    # Setup subprompts
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context_str)
    additional_subprompt =  "Please write your chosen schedule in this time format: (%Y-%m-%d %H:%M:%S). " \
                            "Please also provide your reason on choosing the schedule time. " \
                            "Return your answer in this JSON format: \n" \
                            "{\n" \
                            "\"schedule_time\": str,\n"\
                            "\"reason\" : str\n" \
                            "}\n"\
                            f"Make sure to not return the schedule time earlier than current time. Current time is {current_time}. " \
                            "\n\n" \
                            "Here I provide you some methods if you cannot decide. This is ordered from the most prioritized to least prioritized: \n" \
                            "1. If you think the provided data is not enough, please return the average time of the posts in the provided context \n" \
                            "2. Identify on what time the post would be suitable uploaded. The ideal time would be listed as below: \n" \
                            "   - In the morning is around breakfast time: 06.00 to 08.00 \n" \
                            "   - In the afternoon it would be around lunch time : 12.00 to 13.00 \n" \
                            "   - In the night it would be around the time people resting at their home 18:00 to 21:00\n" \
                            "3. Choose one of these default values: [07.00, 12.30, 18.00] with the date of today or tomorrow. \n" \
                            "Avoid not returning anything at any cost. "
    previous_iteration_notes_subprompt = self.generate_subprompt_previous_iteration_notes([])
    
    # Setup query string
    query_str = "Choose the best schedule to upload the post"

    return self._prompt_template.format(persona_subprompt=persona_subprompt,
                                      context_subprompt=context_subprompt,
                                      additional_subprompt=additional_subprompt,
                                      previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                                      query_str=query_str)
  

