from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent
from llama_index.core import  VectorStoreIndex

class Model():
  """
  Model name. Is adjustable to another model to be used
  """
  llm_model_name: str = "llama3.1"
  embed_model_name: str = "intfloat/multilingual-e5-base"

  """
  Mutable variable in the model. Can be changed through Configurator component
  """
  temperature: float = 0.3
  top_k : int = 10
  max_token : int = 4096
  max_iteration: int = 10

  """
  Constant variable in the model. Should not be changed when the model is operating
  """
  request_timeout: float = 60.0
  tools: list = []


  def __init__(self):
    """
    Initialization of the LLM and the embedding model
    """
    self.llm_model = Ollama(model = self.llm_model_name,
                            temperature = self.temperature,
                            request_timeout = self.request_timeout)
    self.embed_model  = HuggingFaceEmbedding(model_name=self.embed_model_name)
    print(f"[MODEL INITIALIZED] Model is initialized with llm_model: {self.llm_model_name} and embed_model: {self.embed_model_name}")

  ######## PRIVATE ########

  def _construct_metadata(self, topic, query):
    """
    Construct metadata based on the topic and user input query for agentic tools usage
    """
    return ToolMetadata(
      name= f"rag_tools_for_{topic}",
      description= f"Used to answering {topic}-related query of input: \"{query}\" based on retrieved documents"
    )


  def _setup_agent(self, query_engine, topic, query) -> None:
    """
    Setup agentic system and tools for query engine
    """
    metadata = self._construct_metadata(topic, query)
    tool = QueryEngineTool(
      query_engine=query_engine,
      metadata=metadata
    )
    self.tools.append(tool)
    self.agent = ReActAgent.from_tools(
      self.tools, 
      llm = self.llm_model, 
      verbose= True, 
      max_iterations=self.max_iteration
    )

  ######## PUBLIC ########

  def load_data(self,  vector_store, storage_context, topic, query) -> None:
      """
      Load data from pinecone based on the vector store and storage_context
      """
      vector_index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store, 
        storage_context=storage_context, 
        embed_model=self.embed_model
      )
      query_engine = vector_index.as_query_engine(
        llm=self.llm_model,
        embed_model=self.embed_model,
        similarity_top_k=self.top_k,
        llm_kwargs={"max_tokens": self.max_token}
      )
      self._setup_agent(query_engine, topic, query)


  def answer(self, prompt: str) -> str:
    """
    Answer the prompt using the agentic system
    """
    try:
      result = self.agent.query(prompt).response
      return result
    
    except ValueError as e:
       return "I'm sorry, I was unable to answer your question after several attempts. Could you please rephrase or try a simpler version?"
  

  def refresh_tools(self):
    """
    Reset tools that has been constructed before
    """
    self.tools = []


  def config(self, config_dict : dict):
    """
    Config the performance of the model
    """
    if ("temperature" in config_dict):
      self.temperature = config_dict['temperature']
    if ("top_k" in config_dict):
      self.top_k = config_dict['top_k']
    if ("max_token" in config_dict):
      self.max_token = config_dict['max_token']
    if ("max_iteration" in config_dict):
      self.max_iteration = config_dict['max_iteration']

    

