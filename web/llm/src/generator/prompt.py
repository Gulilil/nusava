from llama_index.core.prompts import PromptTemplate
from utils.constant import ACTIONS_LIST
import json

PROMPT_TEMPLATE = """Definition:
You are an influencer in Instagram, expertised in Tourism aspect.
---------------------
{context_subprompt}
{example_subprompt}
{answer_format_subprompt}
---------------------
Instruction:
Given this information, answer the query.
Please write the answer in the style of {tone_str}
Query: {query_str}
"""

class PromptGenerator():

  def __init__(self):
    """
    Instantiate the template
    """
    self.prompt_template = PromptTemplate(PROMPT_TEMPLATE)

    # Config for tone
    self.tone_str = "a Tourism Influencer in Social Media"

  def config_tone(self, tone_str: str) -> None:
    """
    A change for tone
    """
    self.tone_str = tone_str
  
  
  # GENERATE SUBPROMPT
  ##############################
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
  

  def generate_subprompt_answer_format(self, answer_format: str, answer_format_type: str):
    """
    Prepare the answer format part of the prompt
    """
    answer_format_subprompt = "Answer Format:\n"
    if (answer_format is not None and answer_format_type is not None):
      answer_format_subprompt += f"You are expected to return the answer in the type of {answer_format_type} with this format:\n"
      answer_format_subprompt += answer_format
      answer_format_subprompt += "\nPlease do not add any other text beside the answer in the desired format."
    else:
      answer_format_subprompt += "There is no specific format for this query. You may answer however you like."
    return answer_format_subprompt


  # GENERATE PROMPT
  ##############################
  def generate_prompt_decide_action(self, last_action: str = None, last_action_details: str = None, examples: list[dict] = None) -> str:
    # Handle context
    action_list_str = json.dumps(ACTIONS_LIST, indent=2)
    context = f"Here is the list of the actions you can choose along with the descriptions:\n{action_list_str}\n"
    if (last_action is None and last_action_details is None):
      context += f"Your last action is {last_action} with the details: {last_action_details}\n"
      context += "Choose \"none\" when you think you should not do any action. You do not have to take the same action as your last action."

    # Handle answer format
    answer_format = """{
  "action" : "",
  "reason" : ""
}"""
    answer_format_type = "json"

    # Handle subprompt
    context_subprompt = self.generate_subprompt_context(context)
    example_subprompt = self.generate_subprompt_example(examples)
    answer_format_subprompt = self.generate_subprompt_answer_format(answer_format, answer_format_type)

    return self.prompt_template.format(context_subprompt=context_subprompt,
                                      example_subprompt=example_subprompt, 
                                      answer_format_subprompt=answer_format_subprompt,
                                      tone_str=self.tone_str, 
                                      query_str="What action do you to choose to do?")


  def generate_prompt_reply_chat(self, new_message: str, previous_messages: list[str] = None) -> str:
    context = "You have to be informative and clear in giving information to users. You also have to assure the correctness of the facts that you provide.\n"

    if (previous_messages is not None):
      # TODO
      context += ""
    
    context = None
    examples = []

    # Handle subprompt
    context_subprompt = self.generate_subprompt_context(context)
    example_subprompt = self.generate_subprompt_example(examples)
    answer_format_subprompt = self.generate_subprompt_answer_format(None, None)

    return self.prompt_template.format(context_subprompt=context_subprompt,
                                  example_subprompt=example_subprompt, 
                                  answer_format_subprompt=answer_format_subprompt,
                                  tone_str=self.tone_str, 
                                  query_str=new_message)


  def generate_prompt_reply_comment(self, new_comment: str, previous_comments: list[str] = None) -> str:
    # new_comment as context_str
    # predefined query_str
    # TODO
    return 


  def generate_prompt_comment(self, caption: str, additional_context: str = None, examples: list[dict] = None) -> str:
    context_str = f"You are expected to make a comment on a post in Instagram with this caption: \"{caption}\""
    if (additional_context is not None):
      context_str += "\n"
      context_str += f"Here are some additional context: {additional_context}"

    context_subprompt = self.generate_subprompt_context(context_str)
    example_subprompt = self.generate_subprompt_example(examples)
    answer_format_subprompt = self.generate_subprompt_answer_format(None, None)
    query_str = "Make a comment for Instagram post based on the context"

    return self.prompt_template.format(context_subprompt=context_subprompt,
                                  example_subprompt=example_subprompt, 
                                  answer_format_subprompt=answer_format_subprompt,
                                  tone_str=self.tone_str, 
                                  query_str=query_str)


  def generate_prompt_post_caption(self, keywords: list[str], additional_context: str = None, examples: list[dict] = None) -> str:
    keywords_str = ", ".join(keywords)
    context_str = f"You are expected to make a caption based on these keywords: {keywords_str}"
    if (additional_context is not None):
      context_str += "\n"
      context_str += f"Here are some additional context of the captions: {additional_context}"
    
    context_subprompt = self.generate_subprompt_context(context_str)
    example_subprompt = self.generate_subprompt_example(examples)
    answer_format_subprompt = self.generate_subprompt_answer_format(None, None)
    query_str = "Make a caption for Instagram post based on the context"

    return self.prompt_template.format(context_subprompt=context_subprompt,
                                  example_subprompt=example_subprompt, 
                                  answer_format_subprompt=answer_format_subprompt,
                                  tone_str=self.tone_str, 
                                  query_str=query_str)
  


  