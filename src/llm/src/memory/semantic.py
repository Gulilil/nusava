from llama_index.core import Document
from memory.base import Memory
from typing import Any
import copy


class SemanticMemory(Memory):
    """
    In Cognitive Psychology, semantic memory is the memory of meanings, understandings, and other concept-based knowledge unrelated to specific 
    experiences. It is not ordered temporally, and it is not about remembering specific events or episodes. This class provides a simple implementation
    of semantic memory, where the agent can store and retrieve semantic information.
    """

    serializable_attrs = ["memories"]

    def __init__(self, memories: list=None) -> None:
        self.memories = memories

        if not hasattr(self, 'memories') or self.memories is None:
            self.memories = []

        self.semantic_grounding_connector = BaseSemanticGroundingConnector("Semantic Memory Storage")
        self.semantic_grounding_connector.add_documents(self._build_documents_from(self.memories))

    
        
    def _preprocess_value_for_storage(self, value: dict) -> Any:
        engram = None 

        if value['type'] == 'action':
            engram = f"# Fact\n" +\
                     f"I have performed the following action at date and time {value['simulation_timestamp']}:\n\n"+\
                     f" {value['content']}"
        
        elif value['type'] == 'stimulus':
            engram = f"# Stimulus\n" +\
                     f"I have received the following stimulus at date and time {value['simulation_timestamp']}:\n\n"+\
                     f" {value['content']}"
            
        return engram

    def _store(self, value: Any) -> None:
        engram_doc = self._build_document_from(self._preprocess_value_for_storage(value))
        self.semantic_grounding_connector.add_document(engram_doc)
    
    def retrieve_relevant(self, relevance_target:str, top_k=20) -> list:
        """
        Retrieves all values from memory that are relevant to a given target.
        """
        return self.semantic_grounding_connector.retrieve_relevant(relevance_target, top_k)

    #####################################
    # Auxiliary compatibility methods
    #####################################

    def _build_document_from(memory) -> Document:
        # TODO: add any metadata as well?
        return Document(text=str(memory))
    
    def _build_documents_from(self, memories: list) -> list:
        return [self._build_document_from(memory) for memory in memories]
    
   