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
  temperature: float = 0.1
  top_k = 5

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
      if not (len(list_documents)  == len(list_metadata)):
          raise ValueError("The lengths of documents, document_names, and document_descriptions must be equal.")

      # Create vector index from all documents
      self.vector_index = VectorStoreIndex.from_documents(list_documents, embed_model=self.embed_model)

      # Create a list to hold the tools for each document
      self.tools = []
      for i in range(len(list_documents)):
          tool = QueryEngineTool(
              self.vector_index.as_query_engine(llm=self.llm_model, similarity_top_k=self.top_k),
              metadata=ToolMetadata(
                  filename=list_metadata[i]['filename'],
                  filetype=list_metadata[i]['type']
              )
          )
          self.tools.append(tool)

      print(f"[LEARN] Finish model learning for {len(list_documents)} documents.")
  
  # Config agent
  def config(self, context: str) -> None:
    self.agent = ReActAgent.from_tools([self.tools], llm = self.llm_model, verbose= True, context= context)
  
  # Run the system
  def answer(self, prompt: str) -> str:
    result = self.agent.query(prompt).response
    return result
  
  # Run the system without reading a document
  def direct_answer(self, prompt: str) -> str:
     result = self.llm_model.complete(prompt).text
     return result


  

