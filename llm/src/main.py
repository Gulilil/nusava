from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    Document,
    Settings
)

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.llms.ollama import Ollama
from llama_index.core.query_engine import RouterQueryEngine


llm = Ollama(model="llama3.1",
             temperature = 0,
             request_timeout=120.0,
             system_prompt="""
  You are a helpful assistant.
  All questions and answers should be in English.
""")
Settings.llm = llm

# Embedding
embed_model  = HuggingFaceEmbedding(model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")
Settings.embed_model = embed_model

