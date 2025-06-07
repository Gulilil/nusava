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

  def evaluate(self, query: str, response: str, contexts: list) -> dict:
    """
    Run multiple evaluators (correctness, faithfulness, relevancy) on a response.
    """
    results = {}
    
    faithfulness = self.faithfulness_evaluator.evaluate(query=query, response=response, contexts=contexts)
    results["faithfulness"] = {"score": faithfulness.score, "passing": faithfulness.passing}
    
    relevancy = self.relevancy_evaluator.evaluate(query=query, response=response, contexts=contexts)
    results["relevancy"] = {"score": relevancy.score, "passing": relevancy.passing}

    return results