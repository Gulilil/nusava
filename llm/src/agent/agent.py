
from parser.parser import Parser
from llm.src.model.model import Model
from prompt_generator.prompt_generator import PromptGenerator
from gateway.gateway import Gateway

class Agent():
  
  def __init__(self):
    self.parser_component = Parser()
    self.model_component = Model()
    self.prompt_generator_component = PromptGenerator()