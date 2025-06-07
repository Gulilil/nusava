from typing import Any
import copy

class Memory():
    """
    Base class for different types of memory.
    """

    def _preprocess_value_for_storage(self, value: Any) -> Any:
        """
        Preprocesses a value before storing it in memory.
        """
        # by default, we don't preprocess the value
        return value

    def _store(self, value: Any) -> None:
        """
        Stores a value in memory.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    def store(self, value: dict) -> None:
        """
        Stores a value in memory.
        """
        self._store(self._preprocess_value_for_storage(value))
    
    def store_all(self, values: list) -> None:
        """
        Stores a list of values in memory.
        """
        for value in values:
            self.store(value)

    def retrieve(self, first_n: int, last_n: int, include_omission_info:bool=True) -> list:
        """
        Retrieves the first n and/or last n values from memory. If n is None, all values are retrieved.

        Args:
            first_n (int): The number of first values to retrieve.
            last_n (int): The number of last values to retrieve.
            include_omission_info (bool): Whether to include an information message when some values are omitted.

        Returns:
            list: The retrieved values.
        
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def retrieve_recent(self) -> list:
        """
        Retrieves the n most recent values from memory.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def retrieve_all(self) -> list:
        """
        Retrieves all values from memory.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def retrieve_relevant(self, relevance_target:str, top_k=20) -> list:
        """
        Retrieves all values from memory that are relevant to a given target.
        """
        raise NotImplementedError("Subclasses must implement this method.")




