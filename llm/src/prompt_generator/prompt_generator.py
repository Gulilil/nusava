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
    self.prompt_template = RichPromptTemplate(PROMPT_TEMPLATE)

    # Config for tone
    self.tone_str = "Tourism Influencer in Social Media"

  def config_tone(self, tone_str: str) -> None:
    self.tone_str = tone_str

  def generate_prompt_reply_chat(self, new_message: str, previous_messages: list[str] = None) -> str:
    # new_message as query_str
    # TODO
    return 

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

  def generate_prompt_post_caption(self, keywords: list[str], additional_context: str = None) -> str:
    # keywords as context_str
    # additional_context will be appended in context_str
    # predefined query_str

    keywords_str = ", ".join(keywords)
    query_str = ""

    return self.qa_template

    # TODO
    return 
  


  