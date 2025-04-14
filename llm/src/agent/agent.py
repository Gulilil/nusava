
from parser.parser import Parser
from model.model import Model
from prompt_generator.prompt_generator import PromptGenerator
from gateway.gateway import Gateway
from evaluator.evaluator import Evaluator

class Agent():
  
  def __init__(self):
    self.parser_component = Parser()
    self.model_component = Model()
    self.prompt_generator_component = PromptGenerator()
    self.gateway_component = Gateway()
    self.evaluator_component = Evaluator()