from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.ingestion import IngestionPipeline
from llama_index.node_parser import SemanticSplitterNodeParser

from pinecone import Pinecone
import pymongo
import os

from dotenv import load_dotenv
load_dotenv()


class DatabaseConnector():
  # Initialization
  def __init__(self): 
    # Instantiate mongo client
    self.mongo_client = pymongo.MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
    self.mongo_database = self.mongo_client[os.getenv("MONGO_DB_NAME")]
    # Instantiate pinecone client
    self.pinecone_client = Pinecone(api_key=(os.getenv("PINECONE_API_KEY")))
    self.pinecone_index = self.pinecone_client.Index(os.getenv("PINECONE_INDEX"))


  # Get parsed based on filename
  def mongo_get_data(self, collection_name: str, filters: dict = {}) -> list:
    collection = self.mongo_database[collection_name]
    json_documents = collection.find(filters)
    return list(json_documents)


  # Parse json
  def mongo_parse(self, collection_name: str, title: str) -> str:
    documents = self.mongo_get_data(collection_name, {"title": title})

    assert len(documents) > 0, "[ERROR] No data found"
    assert len(documents) == 1, "[ERROR] Multiple title, not unique"

    document = documents[0]
    # Delete id since it is not necessary
    del document['_id']
    # Delete reviews
    del document['reviews']
    return document


  # Get pinecone vector store and storage context
  def pinecone_get_vector_store(self, namespace: str):
    vector_store = PineconeVectorStore(pinecone_index=self.pinecone_index, namespace=namespace)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return vector_store, storage_context


  # Store data to pinecone
  def pinecone_store_data(self, document_list: list, vector_store, embed_model):
    # VectorStoreIndex.from_documents(document_list, 
    #                                 vector_store=vector_store, 
    #                                 embed_model=embed_model)

    # Our pipeline with the addition of our PineconeVectorStore
    pipeline = IngestionPipeline(
        transformations=[
            SemanticSplitterNodeParser(
                buffer_size=1,
                breakpoint_percentile_threshold=95, 
                embed_model=embed_model,
                ),
            embed_model,
            ],
            vector_store=vector_store  # Our new addition
        )

    # Now we run our pipeline!
    pipeline.run(documents=document_list)
  

  # Get index stats
  def pinecone_get_index_stats(self):
    print(self.pinecone_index.describe_index_stats())