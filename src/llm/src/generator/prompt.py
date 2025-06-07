from llama_index.core.prompts import PromptTemplate
import json

PROMPT_TEMPLATE = """Definition:
{persona_subprompt}.
---------------------
{context_subprompt}
{example_subprompt}
{additional_subprompt}
---------------------
Instruction:
Given this information, answer the query.
Query: {query_str}
"""

class PromptGenerator():

  def __init__(self, persona_component):
    """
    Instantiate the template
    """
    self.prompt_template = PromptTemplate(PROMPT_TEMPLATE)
    self.persona_component = persona_component

  # GENERATE SUBPROMPT
  ##############################
  def generate_subprompt_persona(self):
    age, style, occupation = self.persona_component.get_typing_style()
    return f"You are {age} years old with the occupation of {occupation}. You have the characterstics to be {style} "


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

  # GENERATE PROMPT
  ##############################

  def generate_prompt_reply_chat(self, new_message: str, previous_messages: list[str] = None) -> str:
    context = "You have to be informative and clear in giving information to users. You also have to assure the correctness of the facts that you provide.\n"

    # Process previous messages
    if (previous_messages is not None):
      # TODO
      context += ""
    
    # Process examples
    examples = []

    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context)
    example_subprompt = self.generate_subprompt_example(examples)
    additional_subprompt = ""

    return self.prompt_template.format(persona_subprompt=persona_subprompt,
                                  context_subprompt=context_subprompt,
                                  example_subprompt=example_subprompt, 
                                  additional_subprompt=additional_subprompt,
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

    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context_str)
    example_subprompt = self.generate_subprompt_example(examples)
    additional_subprompt = ""
    query_str = "Make a comment for Instagram post based on the context"

    return self.prompt_template.format(persona_subprompt=persona_subprompt,
                                  context_subprompt=context_subprompt,
                                  example_subprompt=example_subprompt, 
                                  additional_subprompt=additional_subprompt,
                                  query_str=query_str)


  def generate_prompt_post_caption(self, img_description: str,  keywords: list[str], additional_context: str = None, examples: list[dict] = None) -> str:
    keywords_str = ", ".join(keywords)
    context_str = f"You are expected to make a caption with images of this description: \"{img_description}\" and based on these keywords: \"{keywords_str}\" at the same time."
    if (additional_context is not None):
      context_str += "\n"
      context_str += f"Here are some additional context of the captions: {additional_context}"
    
    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context_str)
    example_subprompt = self.generate_subprompt_example(examples)
    additional_subprompt =  "Only answer the text caption without any explanation text. " \
                            "Return the answer in string format without any quotation (\") symbol."
    if (additional_context is not None):
      additional_subprompt += f" Here are some additional context: {additional_context}"
    query_str = "Make a caption for Instagram post based on the context"

    return self.prompt_template.format(persona_subprompt=persona_subprompt,
                                      context_subprompt=context_subprompt,
                                      example_subprompt=example_subprompt, 
                                      additional_subprompt=additional_subprompt,
                                      query_str=query_str)
  


  