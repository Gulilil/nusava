from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent

import time

class Model():
  # Declare constants
  llm_model_name: str = "llama3.1"
  embed_model_name: str = "intfloat/multilingual-e5-base"

  # Mutable
  temperature: float = 0.3
  top_k : int = 5
  max_token : int = 512
  max_iteration: int = 20


  # Initialization
  def __init__(self):
    # Declare LLM Model
    self.llm_model = Ollama(model = self.llm_model_name,
                            temperature = self.temperature,
                            request_timeout = 30.0)
    # Declare Embedding Model
    self.embed_model  = HuggingFaceEmbedding(model_name=self.embed_model_name)
    print(f"[MODEL INITIALIZED] Model is initialized with llm_model: {self.llm_model_name} and embed_model: {self.embed_model_name}")


  # Auto timer function
  def __getattribute__(self, name):
    attr = object.__getattribute__(self, name)
    if callable(attr) and not name.startswith("__"):
        # If attr belongs to a different object than self, don't wrap it
        if hasattr(attr, "__self__") and attr.__self__ is not self:
            return attr
        # If attr is a function but not a bound method (no __self__), return as is
        if not hasattr(attr, "__self__"):
            return attr
        def timed(*args, **kwargs):
            start = time.perf_counter()
            result = attr(*args, **kwargs)
            end = time.perf_counter()
            print(f"[{name}] Execution time: {end - start:.6f} seconds")
            return result
        return timed
    return attr


  # # Embed/ encode text to make it into vectors/matrices
  # def embed(self, text: str) -> list:
  #   return self.embed_model.get_text_embedding_batch(text)


  # Learn by making vector store Index from documents
  def learn(self, vector_index) -> None:
      # Create query engine for the index
      query_engine = vector_index.as_query_engine(
          llm=self.llm_model,
          embed_model=self.embed_model,
          similarity_top_k=self.top_k,
          llm_kwargs={"max_tokens": self.max_token}
      )

      # Create and store the tool
      tool = QueryEngineTool(query_engine=query_engine)
      self.tools.append(tool)

      # Use agent tools
      self.agent = ReActAgent.from_tools(self.tools, 
                                    llm = self.llm_model, 
                                    verbose= True, 
                                    max_iterations=self.max_iteration)
  

  # Run the system
  def answer(self, prompt: str, is_direct: bool = False) -> str:
    try:
      if (not is_direct):
        result = self.agent.query(prompt).response
      else:
        result = self.llm_model.complete(prompt).text
      return result
    
    except ValueError as e:
       return "I'm sorry, I was unable to answer your question after several attempts. Could you please rephrase or try a simpler version?"
  

  

