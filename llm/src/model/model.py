from llama_index.core import (
    VectorStoreIndex,
    Document
)

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent

class Model():
  # Declare constants
  llm_model_name: str = "llama3.1"
  embed_model_name: str = "BAAI/bge-m3"

  # Mutable
  temperature: float = 0.3
  top_k : int = 5
  max_token : int = 512

  # Initialization
  def __init__(self):
    # Declare LLM Model
    self.llm_model = Ollama(model = self.llm_model_name,
                            temperature = self.temperature,
                            request_timeout = 30.0)
    # Declare Embedding Model
    self.embed_model  = HuggingFaceEmbedding(model_name=self.embed_model_name)
    print(f"[MODEL INITIALIZED] Model is initialized with llm_model: {self.llm_model_name} and embed_model: {self.embed_model_name}")

  # Learn by making vector store Index from documents
  def learn(self, list_documents: list, list_metadata: list[dict]) -> None:
      # Ensure that the lengths of the input lists are the same
      if not (len(list_documents) == len(list_metadata)):
          raise ValueError("The lengths of documents, document_names, and document_descriptions must be equal.")

      self.tools = []
      for document, metadata in zip(list_documents, list_metadata):
          # Create a vector index for the document
          vector_index = VectorStoreIndex.from_documents(document, embed_model=self.embed_model)

          # Create query engine for the index
          query_engine = vector_index.as_query_engine(
              llm=self.llm_model,
              similarity_top_k=self.top_k,
              llm_kwargs={"max_tokens": self.max_token}
          )

          # Create and store the tool
          tool = QueryEngineTool(
              query_engine=query_engine,
              metadata=ToolMetadata(
                  name=metadata.get("filename", "Unnamed"),
                  description=metadata.get("type", "No description")
              )
          )
          self.tools.append(tool)

      print(f"[LEARN] Finish model learning for {len(list_documents)} documents.")
  
  # Config agent
  def config(self, context: str) -> None:
    self.agent = ReActAgent.from_tools(self.tools, 
                                       llm = self.llm_model, 
                                       verbose= True, 
                                       context= context,
                                       max_iterations=20)
  
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
  

  

