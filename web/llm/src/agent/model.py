from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent
from llama_index.core import  VectorStoreIndex

class Model():
  """
  Model name. Is adjustable to another model to be used
  """
  _llm_model_name: str = "llama3.1"
  _embed_model_name: str = "intfloat/multilingual-e5-base"

  """
  Mutable variable in the model. Can be changed through Configurator component
  """
  _temperature: float = 0.3
  _top_k : int = 10
  _max_token : int = 4096
  _max_iteration: int = 10

  """
  Constant variable in the model. Should not be changed when the model is operating
  """
  _request_timeout: float = 60.0
  _tools: list = []


  def __init__(self):
    """
    Initialization of the LLM and the embedding model
    """
    self.llm_model = Ollama(model = self._llm_model_name,
                            temperature = self._temperature,
                            request_timeout = self._request_timeout)
    self.embed_model  = HuggingFaceEmbedding(model_name=self._embed_model_name)
    print(f"[MODEL INITIALIZED] Model is initialized with llm_model: {self._llm_model_name} and embed_model: {self._embed_model_name}")

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
    self._tools.append(tool)
    self._agent = ReActAgent.from_tools(
      self._tools, 
      llm = self.llm_model, 
      verbose= True, 
      max_iterations=self._max_iteration
    )

  ######## PUBLIC ########

  def display_config(self):
    """
    Display current config
    """
    print(f"LLM name: {self._llm_model_name}")
    print(f"Embedding Model name: {self._embed_model_name}")
    print(f"Temperature: {self._temperature}")
    print(f"Top K: {self._top_k}")
    print(f"Max Token: {self._max_token}")
    print(f"Max Iteration: {self._max_iteration}")
    

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
        similarity_top_k=self._top_k,
        llm_kwargs={"max_tokens": self._max_token}
      )
      self._setup_agent(query_engine, topic, query)


  def answer(self, prompt: str, is_direct: bool = False) -> str:
    """
    Answer the prompt using the agentic system
    """
    try:
      if (is_direct):
         result = self.llm_model.complete(prompt).text
      else:
        result = self._agent.query(prompt).response
      return result
    
    except ValueError as e:
       return "I'm sorry, I was unable to answer your question after several attempts. Could you please rephrase or try a simpler version?"
  

  def refresh_tools(self):
    """
    Reset tools that has been constructed before
    """
    self._tools = []


  def config(self, config_data : tuple):
    """
    Config the performance of the model
    """
    self._temperature = config_data[0]
    self._top_k = config_data[1]
    self._max_token = config_data[2]
    self._max_iteration = config_data[3]

    

