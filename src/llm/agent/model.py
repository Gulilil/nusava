from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import  VectorStoreIndex
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool, ToolMetadata
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
  _tools: dict[list] = {}


  def __init__(self, 
               persona_component: object):
    """
    Initialization of the LLM and the embedding model
    """
    self._persona_component = persona_component
    self.llm_model = None
    self.embed_model  = None

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

  def set_model(self) -> None:
    """
    Set the model based on the configuration
    """
    system_prompt = (
        f"You are a user in Instagram who responds with clarity and purpose. "
        f"You have a certain persona on which you should follow strictly. "
        f"Here is the detail of your persona:\n"
        f"{self._persona_component.get_persona_str()}\n\n"
    )

    self.llm_model = OpenAI(model=self._llm_model_name,
                            api_key=os.getenv("OPENAI_API_KEY"),
                            temperature=self._temperature,
                            system_prompt=system_prompt)
    self.embed_model  = OpenAIEmbedding(model=self._embed_model_name,
                                        api_key=os.getenv("OPENAI_API_KEY"))
    print(f"[MODEL SET] Model is set with llm_model: {self._llm_model_name} and embed_model: {self._embed_model_name}")

  ######## PRIVATE ########

  def _construct_metadata(self, name, description) -> ToolMetadata:
    """
    Construct metadata based on the topic and user input query for agentic tools usage
    """
    return ToolMetadata(
      name= name,
      description= description
    )


  def _add_tool(self, tool_user_id: str, tool) -> None:
    """
    Add tool component to dictionary
    """
    if (tool_user_id in self._tools):
      self._tools[tool_user_id].append(tool)
    else:
      self._tools[tool_user_id] = [tool]
  

  def _setup_tool(self, query_engine, metadata_name, metadata_description, tool_user_id: str) -> None:
    """
    Setup tools for agentic system and query engine
    """
    metadata = self._construct_metadata(metadata_name, metadata_description)
    tool = QueryEngineTool(
      query_engine=query_engine,
      metadata=metadata
    )
    self._add_tool(tool_user_id, tool)


  ######## PUBLIC ########

  def get_config(self) -> dict:
    """
    Return the configuration model in dictionary
    """
    config = {
      "llm_name": self._llm_model_name,
      "embedding_model_name": self._embed_model_name,
      "temperature": self._temperature,
      "top_k": self._top_k,
      "max_token": self._max_token,
      "max_iteration": self._max_iteration
    }
    return config
    

  def refresh_tools(self, tool_user_id : str,  is_all: bool = False) -> None:
    """
    Reset tools that has been constructed before
    """
    if (is_all):
      self._tools = {}
    else:
      if(tool_user_id in self._tools):
        del self._tools[tool_user_id]
        print(f"[REFRESH TOOLS] Tools list has been refreshed for {tool_user_id}")


  def display_tools_count(self) -> None:
    """
    Display all tools
    """
    print("[REGISTERED TOOLS]")
    for tool_user_id, tools in self._tools:
      print(f"{tool_user_id}: {len(tools)}")


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


  def construct_retrieval_system( self, 
                                  vector_store, 
                                  storage_context,
                                  top_k : int):
      """
      Returns query engine as retrieval system
      """
      vector_index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store, 
        storage_context=storage_context, 
        embed_model=self.embed_model
      )
      query_engine = vector_index.as_query_engine(
        llm=self.llm_model,
        embed_model=self.embed_model,
        similarity_top_k=top_k,
        llm_kwargs={"max_tokens": self._max_token},
        response_mode="compact",
        return_source_nodes=True
      )
      return query_engine
    

  async def load_data(self, 
                      vector_store, 
                      storage_context, 
                      metadata_name, 
                      metadata_description, 
                      tool_user_id: str):
      """
      Load data from pinecone based on the vector store and storage_context
      """
      query_engine = self.construct_retrieval_system(vector_store, storage_context, self._top_k)
      self._setup_tool(query_engine, metadata_name, metadata_description, tool_user_id)


  async def answer(self, 
                   prompt: str, 
                   is_direct: bool = False, 
                   verbose: bool = True,
                   allow_direct_answer: bool = True,
                   tool_user_id: str = "",
                  ) -> Tuple[Optional[str], Optional[list]]:
    """
    Answer the prompt using the llm_model or agentic system
    If is_direct is True, it will use the llm_model directly.
    """
    try:
      if (is_direct):
         response = await self.llm_model.acomplete(prompt)
         result = response.text
         return result, None
      else:
        tools = self._tools.get(tool_user_id, [])
        agent = ReActAgent.from_tools(
          tools, 
          llm = self.llm_model, 
          verbose= verbose, 
          max_iterations=self._max_iteration,
          allow_direct_answer=allow_direct_answer
        )
        response = await agent.aquery(prompt)
        result = response.response
        contexts = [node.node.text for node in response.source_nodes]
        return result, contexts
    except Exception as e:
      print(f"[ERROR MODEL ANSWER] Error occured while processing answer: {e}")
      return None, None
    


