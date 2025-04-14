from llama_index.core.prompts import PromptTemplate

PROMPT_TEMPLATE = """You are an influencer in social media, expertised in Tourism aspect. We have provided context information below.
---------------------
{context_str}
{example_str}
---------------------
Given this information, answer the query.
Please write the answer in the style of {tone_str}
Query: {query_str}
"""

class PromptGenerator():
  def __init__(self):
    # Initiate template
    self.prompt_template = PromptTemplate(PROMPT_TEMPLATE)

    # Config for tone
    self.tone_str = "Tourism Influencer in Social Media"

  def config_tone(self, tone_str: str) -> None:
    self.tone_str = tone_str

  def generate_prompt_reply_chat(self, new_message: str, previous_messages: list[str] = None) -> str:
    # new_message as query_str

    if (previous_messages is None):
      context_str = ""
    # else
      # TODO
    
    example_str = ""

    return self.prompt_template.format(context_str=context_str, example_str=example_str, tone_str=self.tone_str, query_str=new_message)

  def generate_prompt_reply_comment(self, new_comment: str, previous_comments: list[str] = None) -> str:
    # new_comment as context_str
    # predefined query_str
    # TODO
    return 

  def generate_prompt_comment(self, caption: str, additional_context: str = None) -> str:
    # caption as context_str
    # additional_context will be appended in context_str
    # predefined query_str
    # TODO
    return 

  def generate_prompt_post_caption(self, keywords: list[str], additional_context: str = None, examples: list[str] = None) -> str:
    # keywords as context_str
    # additional_context will be appended in context_str
    # predefined query_str

    keywords_str = ", ".join(keywords)
    query_str = "Make a caption for Instagram post based on the context"

    context_str = f"You are expected to make a caption based on these keywords: {keywords_str}"
    if (additional_context is not None):
      context_str += "\n"
      context_str += f"Here are some additional context of the captions: {additional_context}"
    
    if examples is None:
      example_str = ""
    # else:
      # TODO
      
    return self.prompt_template.format(context_str=context_str, example_str=example_str, tone_str=self.tone_str, query_str=query_str)
  


  