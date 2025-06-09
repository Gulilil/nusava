from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator

class Evaluator():
  """
  Evaluator component for evaluating the performance of the agent, for (RAG).
  It uses various evaluators such as faithfulness and relevancy to assess the agent's responses.
  """

  def __init__(self, model_component):
    """
    Initialize the evaluators for correctness, faithfulness, and relevancy.
    """
    self.model_component = model_component
    self.faithfulness_evaluator = FaithfulnessEvaluator(llm=self.model_component.llm_model)
    self.relevancy_evaluator = RelevancyEvaluator(llm=self.model_component.llm_model)

  def evaluate_faithfulness(self, query: str, response: str, contexts: list, threshold : float = 0.8) -> dict:
    """
    Evaluate the faithfulness of a response based on the query and contexts.
    """
    faithfulness = self.faithfulness_evaluator.evaluate(query=query, response=response, contexts=contexts)
    return {"score": faithfulness.score, "passing": faithfulness.score >= threshold, "reason": faithfulness.feedback}
  
  def evaluate_relevancy(self, query: str, response: str, contexts: list, threshold : float = 0.8) -> dict:
    """
    Evaluate the relevancy of a response based on the query.
    """
    relevancy = self.relevancy_evaluator.evaluate(query=query, response=response, contexts=contexts)
    return {"score": relevancy.score, "passing": relevancy.score >= threshold, "reason": relevancy.feedback}