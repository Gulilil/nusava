from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator
import json


class Evaluator():
  """
  Evaluator component for evaluating the performance of the agent, for (RAG).
  It uses various evaluators such as faithfulness and relevancy to assess the agent's responses.
  """

  def __init__(self, model_component: object, persona_component: object):
    """
    Initialize the evaluators for faithfulness and relevancy.
    """
    self._model_component = model_component
    self._persona_compnent = persona_component
    self.faithfulness_evaluator = FaithfulnessEvaluator(llm=self._model_component.llm_model)
    self.relevancy_evaluator = RelevancyEvaluator(llm=self._model_component.llm_model)


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
  

  async def _evaluate_naturalness(self, response: str) -> dict:
    """
    Evaluate the naturalness of a response based on the query.
    """
    # Prepare
    persona_str = self._persona_compnent.get_persona_str()
    prompt =  "You are evaluating the *naturalness* of a generated response based on how human-like, fluent, and coherent it sounds. \n" \
              "Naturalness criteria:\n" \
              "- Fluency: Grammar, phrasing, and sentence structure are smooth and natural. \n" \
              "- Coherence: The response makes logical sense and flows well. \n" \
              "- Readability: It is easy to read and understand. \n" \
              "\n" \
              "Rate the response on a scale of **1 to 5**:\n" \
              "1 = Very unnatural while 5 = Very natural \n" \
              "Also provide the reason why you give the rating. \n"\
              f"You also need to mind the naturalness of the response compared to this persona:\n {persona_str} \n" \
              "Return your answer in this JSON format, without any extra explanation or text.: \n" \
              "{\n" \
              "\"score\": int,\n"\
              "\"passing\" : boolean\n" \
              "\"reason\" : str\n" \
              "}\n" \
              "\n"\
              f"This is the response you need to evaluate: {response}"
    answer, _ = await self._model_component.answer(prompt, is_direct=True) 
    # Parse answer
    naturalness = json.loads(answer)
    return {"passing": int(naturalness['score']) >= 3, "reason": naturalness['reason'], "score": naturalness['score']}
  

  async def evaluate_response(self, query: str, response: str, contexts: list[str], evaluation_aspect: list[str]) -> dict:
    """
    Evaluate response for each evaluation aspects given
    """
    evaluation_result = {"evaluation_passing": True}

    # Evaluate each aspect in evaluation aspect

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

    if ("naturalness" in evaluation_aspect):
      current_evaluation = await self._evaluate_naturalness(response)
      for key, val in current_evaluation.items():
        evaluation_result[f"naturalness_{key}"] = val
      evaluation_result["evaluation_passing"] = evaluation_result["evaluation_passing"] and current_evaluation["passing"]
    
    return evaluation_result


  def is_passable(self, evaluation_result: dict) -> bool:
    """
    Check if the evaluation result is passable (only naturalness is allowed to fail)
    """
    for key, val in evaluation_result.items():
      if ("_passing" in key and key != "naturalness_passing"):
        if (not val):
          return False
    return True
