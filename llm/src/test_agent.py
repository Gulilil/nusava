from agent.agent import Agent
import json

if __name__ == "__main__":
  nusava = Agent()
  model_component = nusava.model_component
  prompt_generator_component = nusava.prompt_generator_component

  last_action = None
  last_action_details = None
  i = 1
  
  while (last_action != "none"):
    print(f"Iteration {i}")
    i += 1
    action_answer = nusava.decide_action(last_action, last_action_details)
    print(action_answer)
    json_answer = json.loads(action_answer)

    last_action = json_answer['action']
    last_action_details = f"You have this reason: {json_answer['reason']}"


  
  