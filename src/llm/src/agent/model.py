from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import  VectorStoreIndex
from llama_index.core.agent import ReActAgent
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from typing import Tuple, Optional
from dotenv import load_dotenv
load_dotenv()
import os

class Model():
  """
  Model name. Is adjustable to another model to be used
  """
  _llm_model_name: str = "gpt-4o-mini"
  _embed_model_name: str = "text-embedding-3-small"
  # Uncomment the following lines to use alternative models
  # _llm_model_name: str = "llama3.2"
  # _embed_model_name: str = "BAAI/bge-m3"

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
  _tools: list = []
  

  def __init__(self, 
               persona_component: object):
    """
    Initialization of the LLM and the embedding model
    """
    self.llm_model = OpenAI(model=self._llm_model_name,
                            api_key=os.getenv("OPENAI_API_KEY"),
                            temperature=self._temperature)
    self.embed_model  = OpenAIEmbedding(model=self._embed_model_name,
                                        api_key=os.getenv("OPENAI_API_KEY"))
    self._persona_component = persona_component
    print(f"[MODEL INITIALIZED] Model is initialized with llm_model: {self._llm_model_name} and embed_model: {self._embed_model_name}")

  ######## SETUP ########

  def config(self, config_data : tuple) -> None:
    """
    Config the performance of the model
    """
    self._temperature = config_data[0]
    self._top_k = config_data[1]
    self._max_token = config_data[2]
    self._max_iteration = config_data[3]
    self.display_config()

  ######## PRIVATE ########

  def _construct_metadata(self, name, description) -> ToolMetadata:
    """
    Construct metadata based on the topic and user input query for agentic tools usage
    """
    return ToolMetadata(
      name= name,
      description= description
    )


  def _setup_tool(self, query_engine, metadata_name, metadata_description) -> None:
    """
    Setup tools for agentic system and query engine
    """
    metadata = self._construct_metadata(metadata_name, metadata_description)
    tool = QueryEngineTool(
      query_engine=query_engine,
      metadata=metadata
    )
    self._tools.append(tool)

  ######## PUBLIC ########

  def display_config(self) -> None:
    """
    Display current config
    """
    print("[MODEL CONFIGURATION]")
    print(f"LLM name: {self._llm_model_name}")
    print(f"Embedding Model name: {self._embed_model_name}")
    print(f"Temperature: {self._temperature}")
    print(f"Top K: {self._top_k}")
    print(f"Max Token: {self._max_token}")
    print(f"Max Iteration: {self._max_iteration}")
    

  async def load_data(self,  vector_store, storage_context, metadata_name, metadata_description) -> None:
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
        llm_kwargs={"max_tokens": self._max_token},
        response_mode="compact",
        return_source_nodes=True
      )
      self._setup_tool(query_engine, metadata_name, metadata_description)


  async def answer(self, 
                   prompt: str, 
                   is_direct: bool = False, 
                   verbose: bool = True
                  ) -> Tuple[Optional[str], Optional[list]]:
    """
    Answer the prompt using the llm_model or agentic system
    If is_direct is True, it will use the llm_model directly.
    """
    system_prompt=(
        f"You are a user in Instagram who responds with clarity and purpose."
        f"You have a certain persona on which you should follow strictly."
        f"Here is the detaul of your persona:\n"
        f"{self._persona_component.get_persona_str()}\n\n"
    )

    try:
      if (is_direct):
         response = await self.llm_model.acomplete(prompt)
         result = response.text
         return result, None
      else:

        agent = ReActAgent.from_tools(
          self._tools, 
          llm = self.llm_model, 
          verbose= verbose, 
          max_iterations=self._max_iteration,
          system_prompt = system_prompt
        )
        response = await agent.aquery(prompt)
        result = response.response
        contexts = [node.node.text for node in response.source_nodes]
        return result, contexts
    
    except Exception as e:
       print(f"[ERROR MODEL ANSWER] Error occured while processing answer: {e}")
       return None, None
  

  def refresh_tools(self) -> None:
    """
    Reset tools that has been constructed before
    """
    self._tools = []


