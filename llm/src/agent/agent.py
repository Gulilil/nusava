
from llm.src.searcher.searcher import Searcher
from model.model import Model
from prompt_generator.prompt_generator import PromptGenerator
from gateway.gateway import Gateway
from evaluator.evaluator import Evaluator

class Agent():
  
  def __init__(self):
    self.Searcher_component = Searcher()
    self.model_component = Model()
    self.prompt_generator_component = PromptGenerator()
    self.gateway_component = Gateway()
    self.evaluator_component = Evaluator()

  
  def decide_action(self, last_action: str = None, last_action_details: str = None):
    prompt = self.prompt_generator_component.generate_prompt_decide_action(last_action, last_action_details)
    answer = self.model_component.answer(prompt, True)
    return answer