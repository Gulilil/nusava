from llama_index.core.prompts import RichPromptTemplate

PROMPT_TEMPLATE = """You are an influencer in social media, expertised in Tourism aspect. We have provided context information below.
---------------------
{{ context_str }}

{{ example_str}}
---------------------
Given this information, answer the query.
Please write the answer in the style of {{ tone_str }}
Query: {{ query_str }}
"""

class PromptGenerator():
  def __init__(self):
    # Initiate template
    self.qa_template = RichPromptTemplate(PROMPT_TEMPLATE)

    # Config for tone
    self.tone_str = "Tourism Influencer in Social Media"

  def config_tone(self, tone_str: str):
    self.tone_str = tone_str

  def generate_prompt_reply_chat(context_str: str):
    # Expeceted format:
    # TODO
    return 

  def generate_prompt_reply_comment(context_str: str):
    # TODO
    return 

  def generate_prompt_comment(context_str: str):
    # TODO
    return 

  def generate_prompt_like(context_str: str):
    # TODO
    return 

  def generate_prompt_follow(context_str: str):
    # TODO
    return 

  def generate_prompt_post(context_str: str):
    # TODO
    return 


  