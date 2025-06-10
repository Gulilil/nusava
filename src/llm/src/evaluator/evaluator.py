from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator

class Evaluator():
  """
  Evaluator component for evaluating the performance of the agent, for (RAG).
  It uses various evaluators such as faithfulness and relevancy to assess the agent's responses.
  """

  def __init__(self, llm_model):
    """
    Initialize the evaluators for correctness, faithfulness, and relevancy.
    """
    self.faithfulness_evaluator = FaithfulnessEvaluator(llm=llm_model)
    self.relevancy_evaluator = RelevancyEvaluator(llm=llm_model)


  async def evaluate_faithfulness(self, query: str, response: str, contexts: list) -> dict:
    """
    Evaluate the faithfulness of a response based on the query and contexts.
    """
    faithfulness = await self.faithfulness_evaluator.aevaluate(query=query, response=response, contexts=contexts)
    return {"passing": faithfulness.passing, "reason": faithfulness.feedback}
  

  async def evaluate_relevancy(self, query: str, response: str, contexts: list) -> dict:
    """
    Evaluate the relevancy of a response based on the query.
    """
    relevancy = await self.relevancy_evaluator.aevaluate(query=query, response=response, contexts=contexts)
    return {"passing": relevancy.passing, "reason": relevancy.feedback}