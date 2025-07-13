from llama_index.core.prompts import PromptTemplate
from datetime import datetime, timezone, timedelta
import langid

PROMPT_TEMPLATE = """Definition:
{persona_subprompt}.
---------------------
{context_subprompt}

{additional_subprompt}

{previous_iteration_notes_subprompt}
---------------------
Instruction:
Given this information, answer the query.
Query: \"{query_str}\"
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
    persona_subprompt = f"You are {age} years old with the occupation of {occupation}. You have the characterstics to be {style} "
    persona_subprompt += "This is a crucial part of your identity, so make sure to always follow this persona in your responses. \n"
    # persona_subprompt += f"Here is more details of your persona:\n{self._persona_component.get_persona_str()}\n"

    return persona_subprompt


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
    if (previous_iteration_notes is not None):
      previous_iteration_notes_subprompt = "Previous Iteration Notes:\n"
      if (len(previous_iteration_notes) == 0):
         previous_iteration_notes_subprompt += "I have no provided notes from the previous iteration. This is your first iteration"
      else:
        previous_iteration_notes_subprompt += "Here are some notes from your previous iterations. This notes are important to be considered in your answer. " \
                                              "Your answer are expected to pass the evaluator. But, here I provide some notes on your previous answers and the reason it does not pass the evaluator.\n" \
                                              "You should and are expected to learn from this notes so you do not repeat the same mistake. " \
                                              "The field `your_answer` is the answer that you provided in the previous iteration. \n" \
                                              "You should not repeate the same answer as the ones in `your_answer` fields. At least, you should parafrase and choose different words from your previous answer.\n"     
        for notes in previous_iteration_notes:
          previous_iteration_notes_subprompt += "{\n"
          for key, value in notes.items():
            previous_iteration_notes_subprompt += f"{key}: {value}\n"
          previous_iteration_notes_subprompt += "}\n"
        previous_iteration_notes_subprompt += "If the only \"_passing\" field with False value is \"naturalness_passing\", you *should focus* on paraphrasing your previous answer to sound more natural, fluent, and human-like. \n" 
    else:
      previous_iteration_notes_subprompt = ""
      
    return previous_iteration_notes_subprompt

  ###############################
  ####### GENERATE PROMPT #######
  ###############################

  ######## SUPPORTING PROMPT ########

  def generate_prompt_error(self, user_query: str) -> str:
    """
    Generate a prompt for error message
    """
    context_str = "You are expected to answer the user query, but you cannot answer this query due to some reason. \n" \
                  f"Here is the user query: \"{user_query}\" \n" \
                  "The reason on why you cannot answer this question is because you are not provided with enough data or maybe you require more context to understand user's query. " \
                  "You may explain this reason to user moderately. "\
                  
    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context_str)
    additional_subprompt =  "You are expected to explain to user concisely yet informative." \
                            "Make sure to not answer more than 1 paragraph."
    
    # Identify language
    lang, confidence = langid.classify(user_query)
    print(f"[LANGUAGE IDENTIFICATION] Detected language: \"{lang}\" with confidence: {confidence}")
    additional_subprompt += "You are also a language expert. You should identify the language in the query message. "\
                            f"You are helped with language identification library. Based on its detection, the language is \"{lang}\". "\
                            "However, this is not absolutely true. You may have different answer if you think the answer from identification library is not right. "\
                            "After you identify the language, you should and have to answer it on the same language. \n"

    previous_iteration_notes_subprompt = ""
    query_str = "Explain to user that you cannot answer this query."

    return self._prompt_template.format(persona_subprompt=persona_subprompt,
                                  context_subprompt=context_subprompt,
                                  additional_subprompt=additional_subprompt,
                                  previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                                  query_str=query_str)
  

  def generate_prompt_out_of_domain(self, user_query: str, previous_iteration_notes: list = []) -> str:
    """
    Generate a prompt for out of domain message
    """
    context_str = "You are expected to answer the user query, but you cannot answer this query because you think that the query is outside your domain of expertise. \n" \
                  f"\nHere is the user query: \"{user_query}\" \n" \
                  "You can explain that your expertise domain is tourism. You can also tell the user if they think that the query is in tourism domain, you might require more context to answer it. \n"

    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context_str)
    additional_subprompt =  "You are expected to explain to user concisely yet informative." \
                            "Make sure to not answer more than 1 paragraph."
    previous_iteration_notes_subprompt = self.generate_subprompt_previous_iteration_notes(previous_iteration_notes)
    query_str = "Explain to user that you cannot answer this query because it is not what you are expert on"

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



  ######## ACTION PROMPT ########
  
  ######## CHAT ########

  def generate_prompt_identify_chat_category(self, new_message: str, previous_messages: list[dict] = []) -> str: 
    """
    Generate a prompt for categorize the caht
    """
    context = f"You are required to categorize this new message : \"{new_message}\".\n" \
              "The category is divided into three categories: [general, tourism, other]. \n" \
              "- general: casual conversation, greetings, small talk, and your personal information. \n" \
              "If the message falls into \"general\" category, you have to answer it based on your persona. \n" \
              "- tourism: messages related to travel, destinations, itineraries,  accommodations, local culture, or tourism-related inquiries. \n" \
              "If the message falls into \"tourism\" category, you should and have to use tools from RAG method to answer it. You cannot immediately answer it on your first iteration of thoughts. \n" \
              "- other: anything that does not fall into the above two categories. \n" \
              "If the message falls into \"other\" category, explain that it is outside of your expertise to answer the question. " \
              "Therefore, you need to explain to the user that you cannot provide the answer that message. \n" \

    context += "You are also provided with some previous messages. You should try to understand the whole context of the conversation then decide what type or category is the new message is. \n"
    context += "Here is the previous messages:\n\n"
    for i, message in enumerate(previous_messages):
      context += f"Message {i+1}. {message['role']}: \"{message['content']}\"\n"
    context += "\n"


    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context)

    additional_subprompt =  "Aside from answering the category, you also need to provide the reason why you categorize the message into that certain category. \n" \
                            "Return your answer in this JSON format: \n" \
                            "{\n" \
                            "\"category\": str,\n"\
                            "\"reason\" : str\n" \
                            "}\n"\
                            "Do not add any character or words inside the category fields. Only insert it as general, tourism, or other."\
    
    previous_iteration_notes_subprompt = ""
    return self._prompt_template.format(persona_subprompt=persona_subprompt,
                              context_subprompt=context_subprompt,
                              additional_subprompt=additional_subprompt,
                              previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                              query_str=new_message)


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
      context += "\n"

      context += "Aside for the previous recent messages that you are provided. You will also be provided with some tools. "
      context += "You should and have to use the tools in answering the question using RAG method. The usage of the tools is critical on this aspect. "
      context += "The tools can be used to inquire information related to tourism. Furthermore, you might also be provided with tools to see the summarization of your previous messages. "
      context += "You need and have to utilize all the tools that are provided. In doing action, please do iteration to all the tools you think is related to the query. "
      context += "Do not use only one tools. Whenever you are unsure whether it is Nusa Tenggara Timur or Nusa Tenggara Barat, you should check both tools for Nusa Tenggara Timur and Nusa Tenggara Barat to answer the questions. "
      context += "You should also try to use the tools to check previous memory to get better context. "

    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context)
    # Chat does not need to have examples. It can be vary depending on the topic/ message
    additional_subprompt =  "In answering the context, please add a little of your explaination. " \
                            "Use your persona data to add a little characteristics to your answer. \n" \
                            "The faithfulness and relevancy to the query is critical. " \
                            "However, the style and characteristics of your answer is equally important. \n" \
                            "Please stay true and faithful to your persona. \n"
    additional_subprompt += "You should answer the chat message in 1 to 3 short paragraphs. You may answer up to 5 paragraphs but ONLY if it is critical and necessary. "\
                            "Under normal circumstances, please stick to only using 3 paragraphs. \n" \
                            "Each paragraph can only contain maximum 2 sentences. Avoid using long and complex sentences. "\
                            "You may use slang words and informal tone. However, please use it to suit to your persona. \n" \
                            "Do not explain other things that are not related the message from user. You would like to answer straight to the point. " \
                            "Do not answer in bullet points. On the other hand, try to explain it narratively. " \
                            "Do not forget to give your opinion according to the message as if you are a user in Instagram chatting with other people. \n" 
    
    # Identify language
    lang, confidence = langid.classify(new_message)
    print(f"[LANGUAGE IDENTIFICATION] Detected language: \"{lang}\" with confidence: {confidence}")
    additional_subprompt += "You are also a language expert. You should identify the language in the query message. "\
                            f"You are helped with language identification library. Based on its detection, the language is \"{lang}\". "\
                            "However, this is not absolutely true. You may have different answer if you think the answer from identification library is not right. "\
                            "After you identify the language, you should and have to answer it on the same language. \n"

    previous_iteration_notes_subprompt = self.generate_subprompt_previous_iteration_notes(previous_iteration_notes)
    return self._prompt_template.format(persona_subprompt=persona_subprompt,
                                  context_subprompt=context_subprompt,
                                  additional_subprompt=additional_subprompt,
                                  previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                                  query_str=new_message)

  ######## COMMENT ########

  def generate_prompt_comment(self, caption: str, previous_comments: list = [], previous_iteration_notes: list[dict] = []) -> str:
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
    previous_iteration_notes_subprompt = self.generate_subprompt_previous_iteration_notes(previous_iteration_notes)
    
    # Setup query string
    query_str = "Make a comment for Instagram post based on the context. \n" \
                "Long comment is not preferable and is bot-like. " \
                "Comments longer than 2 sentences are not allowed. However, if possible, 1 sentence comment is preferable. "\
                "Avoid using long and complex sentences. Keep the sentences short and concise. \n" \
                "Try to make the comment as natural as you can. You can use informal tone to suit your persona. " \
                "Users are rarely use emoji in making comments. You may use 1 and 2 if you think it is necessary to suit to your persona. \n" \
                "You should avoid using hashtags unless it is really necessary and related to your persona. \n" \
                "You should and have to make the comment in the same language as the post caption. "

    return self._prompt_template.format(persona_subprompt=persona_subprompt,
                                  context_subprompt=context_subprompt,
                                  additional_subprompt=additional_subprompt,
                                  previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                                  query_str=query_str)

  ######## POST ########

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
                            "Return the answer in string format without any quotation (\") symbol.\n" \
                            "By default, do not use hashtags and emoji unless it is described in \"additional context\". " \
                            "Keep the caption short and meaningful to other people. " \
                            "Use English as the default language in making caption unless it is stated in \"additional context\" regarding the language you have to use."
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
  

  def generate_prompt_choose_schedule_post(self, caption_message: str, reference_posts: list) -> str:
    
    """
    Generate a prompt for choosing schedule for uploading a post
    """
    context_str =  f"You are about to upload a post in Instagram with this given caption, \"{caption_message}\". You are expected to generate the ideal time to upload the post.\n" \
                    "Later you are provided with some data about posts as your references. " \
                    "The post data will consist of: the post caption, the post created time, the comments amount, and its similarity with the given caption"\
                    "Focus on `Post Created Time` because this is the critical aspect you need to examine. " \
                    "If possible, choose post data you think similar or relevan to the post caption, has more comments amount, and its similarity score. " \
                    "\n\n" 
    for i, post in enumerate(reference_posts):
      context_str += f"POST {i+1}:\n"
      context_str += post     
      context_str += "\n\n"  

    # Setup subprompts
    current_time = datetime.now(timezone.utc) + timedelta(hours=7)
    current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
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
                            "Especially for the date, you must not return a date earlier than today's date in the given current_time. \n" \
                            "Do not add any other word, character, or string outside the given format. "\
                            "\n\n" \
                            "Here I provide you some methods if you cannot decide. This is ordered from the most prioritized to least prioritized: \n" \
                            "1. If you think the provided data is not enough, please return the average time of the posts in the provided context \n" \
                            "2. Identify on what time the post would be suitable uploaded. The ideal time would be listed as below: \n" \
                            "   - In the morning is around breakfast time: 06.00 to 08.00 \n" \
                            "   - In the afternoon it would be around lunch time : 12.00 to 13.00 \n" \
                            "   - In the night it would be around the time people resting at their home 18:00 to 21:00\n" \
                            "3. Choose one of these default values: [07.00, 12.30, 18.00] with the date of today or tomorrow. \n" \
                            "Avoid not returning anything at any cost. "
    previous_iteration_notes_subprompt = ""
    
    # Setup query string
    query_str = "Choose the best schedule to upload the post"

    return self._prompt_template.format(persona_subprompt=persona_subprompt,
                                      context_subprompt=context_subprompt,
                                      additional_subprompt=additional_subprompt,
                                      previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                                      query_str=query_str)
  

