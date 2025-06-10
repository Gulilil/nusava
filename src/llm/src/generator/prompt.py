from llama_index.core.prompts import PromptTemplate
import json

PROMPT_TEMPLATE = """Definition:
{persona_subprompt}.
---------------------
{context_subprompt}
{example_subprompt}
{additional_subprompt}
{previous_iteration_notes_subprompt}
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
    Format of examples:
    [
      {"iteration" : x, "your_answer": "...", "evaluator": "...", "evaluation_score" : "...", "reason_of_rejection" : ...},
      ..., 
      {"iteration" : x, "your_answer": "...", "evaluator": "...", "evaluation_score" : "...", "reason_of_rejection" : ...},
    ]
    """
    if (previous_iteration_notes is not None and len(previous_iteration_notes) > 0):
      previous_iteration_notes_subprompt = "Here are some notes from your previous iterations. This notes are important to be considered in your answer.\n"
      previous_iteration_notes_subprompt += "Your answer are expected to pass the evaluator. But, here I provide some notes on your previous answers and the reason it does not pass the evaluator.\n"
      for notes in previous_iteration_notes:
        previous_iteration_notes_subprompt += "{\n"
        for key, value in notes.items():
          previous_iteration_notes_subprompt += f"{key}: {value}\n"
        previous_iteration_notes_subprompt += "}\n"
    else:
      previous_iteration_notes_subprompt = "I have no provided notes from the previous iteration. This is your first iteration"
    
    return previous_iteration_notes_subprompt

  # GENERATE PROMPT
  ##############################

  def generate_prompt_error(self, user_query: str,  error_message: str) -> str:
    """
    Generate a prompt for error message
    """
    context_str = "You are expected to answer the user query, but you cannot answer this query due to some error."
    context_str += f"\nHere is the user query: \"{user_query}\""
    if (error_message is not None):
      context_str += f"\nHere is the error message: {error_message}"

    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context_str)
    example_subprompt = self.generate_subprompt_example(None)
    additional_subprompt =  "You are expected to explain to user concisely yet informative." \
                            "Make sure to not answer more than 1 paragraph."
    previous_iteration_notes_subprompt = ""
    query_str = "Explain to user that you cannot answer this query."

    return self.prompt_template.format(persona_subprompt=persona_subprompt,
                                  context_subprompt=context_subprompt,
                                  example_subprompt=example_subprompt, 
                                  additional_subprompt=additional_subprompt,
                                  previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                                  query_str=query_str)

  def generate_prompt_evaluate(self, query: str, answer: str, contexts: list[str], evaluator_type: str) -> str:
    """
    Generate a prompt for evaluation
    """
    context_str = "You are expected to evaluate the answer based on the query and contexts."
    context_str += f"\nHere is the query: \"{query}\""
    context_str += f"\nHere is the answer: \"{answer}\""
    context_str += "\nHere are the contexts that can be used to evaluate the answer:\n"
    for i, context in enumerate(contexts):
      context_str += f"{i+1}. {context}\n"

    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context_str)
    example_subprompt = self.generate_subprompt_example(None)
    if (evaluator_type == "faithfulness"):
      additional_subprompt = f"You are expected to evaluate the answer based on the {evaluator_type} evaluator."
    previous_iteration_notes_subprompt = ""

    return self.prompt_template.format(persona_subprompt=persona_subprompt,
                                  context_subprompt=context_subprompt,
                                  example_subprompt=example_subprompt, 
                                  additional_subprompt=additional_subprompt,
                                  previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                                  query_str="Evaluate the answer")

  def generate_prompt_reply_chat(self, new_message: str, previous_messages: list[str] = None, previous_iteration_notes: list[dict] = None) -> str:
    """
    Generate a prompt for replying chat
    """
    context = "You have to be informative and clear in giving information to users. You also have to assure the correctness of the facts that you provide.\n"

    # Process previous messages
    if (previous_messages is not None):
      # TODO
      context += ""
    
    # TODO Process examples
    examples = []

    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context)
    example_subprompt = self.generate_subprompt_example(examples)
    additional_subprompt = ""
    previous_iteration_notes_subprompt = self.generate_subprompt_previous_iteration_notes(previous_iteration_notes)

    return self.prompt_template.format(persona_subprompt=persona_subprompt,
                                  context_subprompt=context_subprompt,
                                  example_subprompt=example_subprompt, 
                                  additional_subprompt=additional_subprompt,
                                  previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                                  query_str=new_message)


  def generate_prompt_comment(self, caption: str, additional_context: str = None, previous_iteration_notes: list[dict] = None) -> str:
    """
    Generate a prompt for making a comment on Instagram post
    """

    context_str = f"You are expected to make a comment on a post in Instagram with this caption: \"{caption}\""
    if (additional_context is not None):
      context_str += "\n"
      context_str += f"Here are some additional context: {additional_context}"

    # TODO Process examples
    examples = []

    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context_str)
    example_subprompt = self.generate_subprompt_example(examples) #TODO
    additional_subprompt = ""
    previous_iteration_notes_subprompt = self.generate_subprompt_previous_iteration_notes(previous_iteration_notes)
    
    # Setup query string
    query_str = "Make a comment for Instagram post based on the context"

    return self.prompt_template.format(persona_subprompt=persona_subprompt,
                                  context_subprompt=context_subprompt,
                                  example_subprompt=example_subprompt, 
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

    # TODO Process examples
    examples = []

    # Setup subprompts
    persona_subprompt = self.generate_subprompt_persona()
    context_subprompt = self.generate_subprompt_context(context_str)
    example_subprompt = self.generate_subprompt_example(examples)
    additional_subprompt =  "Only answer the text caption without any explanation text. " \
                            "Return the answer in string format without any quotation (\") symbol."
    if (additional_context is not None):
      additional_subprompt += f" Here are some additional context: {additional_context}"
    previous_iteration_notes_subprompt = self.generate_subprompt_previous_iteration_notes(previous_iteration_notes)
    
    # Setup query string
    query_str = "Make a caption for Instagram post based on the context"

    return self.prompt_template.format(persona_subprompt=persona_subprompt,
                                      context_subprompt=context_subprompt,
                                      example_subprompt=example_subprompt, 
                                      additional_subprompt=additional_subprompt,
                                      previous_iteration_notes_subprompt=previous_iteration_notes_subprompt,
                                      query_str=query_str)
  


  