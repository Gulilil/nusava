from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    Document,
    Settings
)

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent



class Model():
  # Declare constants
  llm_model_name: str = "llama3.1"
  embed_model_name: str = "BAAI/bge-m3"
  temperature: float = 0.3

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
  def learn(self, document_text: str, document_name: str, document_description: str, k: int = 5):
    # Make document to vector_index
    document_doc = [Document(text=document_text)]
    self.document_name = document_name
    self.document_description = document_description
    self.vector_index = VectorStoreIndex.from_documents(document_doc, embed_model=self.embed_model)

    # Make searching tool
    self.tools = QueryEngineTool(
        self.vector_index.as_query_engine(llm = self.llm_model,  similarity_top_k=k),
        metadata = ToolMetadata(
          name = self.document_name,
          description = document_description
        )
      )
    print(f"[LEARN] Finish model learning for the documents {document_name}")
  
  # Config agent
  def config(self, context: str):
    self.agent = ReActAgent.from_tools([self.tools], llm = self.llm_model, verbose= True, context= context)
  
  # Run the system
  def answer(self, prompt: str):
    result = self.agent.query(prompt)
    return result


  

