from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator, CorrectnessEvaluator
from agent.model import Model
from agent.persona import Persona


class Evaluator():
  """
  Evaluator component for evaluating the performance of the agent, for (RAG).
  It uses various evaluators such as faithfulness and relevancy to assess the agent's responses.
  """

  def __init__(self, model_component: Model, persona_component: Persona):
    """
    Initialize the evaluators for correctness, faithfulness, and relevancy.
    """
    self._model_component = model_component
    self._persona_compnent = persona_component
    self.correctness_evaluator = CorrectnessEvaluator(llm=self._model_component.llm_model)
    self.faithfulness_evaluator = FaithfulnessEvaluator(llm=self._model_component.llm_model)
    self.relevancy_evaluator = RelevancyEvaluator(llm=self._model_component.llm_model)


  async def _evaluate_correctness(self, query: str, response:str, contexts: list) -> dict:
    """
    Evaluate the correctness of a response based on the query and contexts.
    """
    reference = ""
    for i, context in enumerate(contexts):
      reference += f"Reference {i+1}"
      reference += "\n"
      reference += context
      reference += "\n"
    correctness = await self.correctness_evaluator.aevaluate(query=query, response=response, reference=reference)
    return {"passing" : correctness.passing, "reason": correctness.feedback, "score" : correctness.score}


  async def _evaluate_faithfulness(self, query: str, response: str, contexts: list) -> dict:
    """
    Evaluate the faithfulness of a response based on the query and contexts.
    """
    faithfulness = await self.faithfulness_evaluator.aevaluate(query=query, response=response, contexts=contexts)
    return {"passing": faithfulness.passing, "reason": faithfulness.feedback}
  

  async def _evaluate_relevancy(self, query: str, response: str, additional_contexts: list = []) -> dict:
    """
    Evaluate the relevancy of a response based on the query.
    """
    contexts = [query]
    if (len(additional_contexts) > 0):
      contexts.extend(additional_contexts)
    
    relevancy = await self.relevancy_evaluator.aevaluate(query=query, response=response, contexts=contexts)
    return {"passing": relevancy.passing, "reason": relevancy.feedback}
  

  async def _evaluate_naturalness(self, query: str, response: str) -> dict:
    """
    Evaluate the naturalness of a response based on the query.
    """


    contexts = [query]
    if (len(additional_contexts) > 0):
      contexts.extend(additional_contexts)
    
    relevancy = await self.relevancy_evaluator.aevaluate(query=query, response=response, contexts=contexts)
    return {"passing": relevancy.passing, "reason": relevancy.feedback}
  
  

  async def evaluate_response(self, query: str, response: str, contexts: list[str], evaluation_aspect: list[str]) -> dict:
    """
    Evaluate response for each evaluation aspects given
    """
    evaluation_result = {"evaluation_passing": True}

    # Evaluate each aspect in evaluation aspect
    if ("correctness" in evaluation_aspect):
      current_evaluation = await self._evaluate_correctness(query, response, contexts)
      for key, val in current_evaluation.items():
        evaluation_result[f"correctness_{key}"] = val
      evaluation_result["evaluation_passing"] = evaluation_result["evaluation_passing"] and current_evaluation["passing"]

    if ("faithfulness" in evaluation_aspect):
      current_evaluation = await self._evaluate_faithfulness(query, response, contexts)
      for key, val in current_evaluation.items():
        evaluation_result[f"faithfulness_{key}"] = val
      evaluation_result["evaluation_passing"] = evaluation_result["evaluation_passing"] and current_evaluation["passing"]

    if ("relevancy" in evaluation_aspect):
      current_evaluation = await self._evaluate_relevancy(query, response, contexts)
      for key, val in current_evaluation.items():
        evaluation_result[f"relevancy_{key}"] = val
      evaluation_result["evaluation_passing"] = evaluation_result["evaluation_passing"] and current_evaluation["passing"]
    
    return evaluation_result