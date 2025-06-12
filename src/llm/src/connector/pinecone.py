from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore
from typing import Tuple

from pinecone import Pinecone
import os

from dotenv import load_dotenv
load_dotenv()


class PineconeConnector():
  """
  Connecting component to Pinecone : VectorDB for LLM and RAG
  """
  def __init__(self): 
    """
    Instantiate the database client
    """
    self.client = Pinecone(api_key=(os.getenv("PINECONE_API_KEY")))
    self.index = self.client.Index(os.getenv("PINECONE_INDEX"))


  def get_vector_store(self, namespace: str) -> Tuple[VectorStoreIndex, StorageContext]:
    """
    Get vector store and storage context from pinecone for certain namespace
    """
    vector_store = PineconeVectorStore(pinecone_index=self.index, namespace=namespace)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return vector_store, storage_context


  def store_data(self, nodes, storage_context, embed_model) -> None:
    """
    Store processed data to certain storage_context
    """
    VectorStoreIndex(nodes, storage_context=storage_context, embed_model=embed_model)


  def get_index_stats(self) -> None:
    """
    Display status of the pinecone index
    """
    print(self.index.describe_index_stats())

  
  def is_namespace_exist(self, namespace_name: str) -> bool:
    """
    Check if a certain namespace exist
    """
    namespaces_data = self.index.describe_index_stats()['namespaces']
    return namespace_name in namespaces_data
